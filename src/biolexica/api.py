"""API for assembling biomedial lexica."""

import logging
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterable, List, Literal, Optional, Union, Dict
from urllib.request import urlretrieve

import bioregistry
import biosynonyms
import gilda
import pyobo
from curies import Reference
from gilda.grounder import load_entries_from_terms_file
from gilda.process import normalize
from pydantic import BaseModel, Field
from tqdm.auto import tqdm

if TYPE_CHECKING:
    import semra

__all__ = [
    "Configuration",
    "Input",
    "assemble_terms",
    "iter_terms_by_prefix",
    "load_grounder",
    "get_mesh_category_curies",
    "Annotation",
    "Match",
    "Grounder",
    "GrounderHint",
]

logger = logging.getLogger(__name__)

HERE = Path(__file__).parent.resolve()
LEXICA = HERE.parent.parent.joinpath("lexica")
Processor = Literal["pyobo", "bioontologies", "biosynonyms", "gilda"]

GrounderHint = Union[gilda.Grounder, str, Path]


class Input(BaseModel):
    """An input towards lexicon assembly."""

    processor: Processor
    source: str
    ancestors: Union[None, str, List[str]] = None
    kwargs: Optional[Dict[str, Any]] = None


class Configuration(BaseModel):
    """A configuration for construction of a lexicon."""

    inputs: List[Input]
    excludes: Optional[List[str]] = Field(
        default=None, description="A list of CURIEs to exclude after processing is complete"
    )


PREDEFINED = ["cell", "anatomy", "phenotype"]
URL_FMT = "https://github.com/biopragmatics/biolexica/raw/main/lexica/{key}/terms.tsv.gz"


class Match(BaseModel):
    """Model a scored match from Gilda."""

    reference: Reference
    name: str
    score: float

    @property
    def curie(self) -> str:
        """Get the reference's curie."""
        return self.reference.curie

    @classmethod
    def from_gilda(cls, scored_match: gilda.ScoredMatch):
        """Construct a match from a Gilda object."""
        return cls(
            reference=Reference(prefix=scored_match.term.db, identifier=scored_match.term.id),
            name=scored_match.term.entry_name,
            score=round(scored_match.score, 4),
        )


class Annotation(BaseModel):
    """Data about an annotation."""

    text: str
    start: int
    end: int
    match: Match

    @property
    def reference(self) -> Reference:
        """Get the match's reference."""
        return self.match.reference

    @property
    def name(self) -> str:
        """Get the match's entry name."""
        return self.match.name

    @property
    def curie(self) -> str:
        """Get the match's CURIE."""
        return self.match.curie

    @property
    def score(self) -> float:
        """Get the match's score."""
        return self.match.score

    @property
    def substr(self) -> str:
        """Get the substring that was matched."""
        return self.text[self.start : self.end]


class Grounder(gilda.Grounder):
    """Wrap a Gilda grounder with additional functionality."""

    def get_matches(
        self,
        s: str,
        context: Optional[str] = None,
        organisms: Optional[List[str]] = None,
        namespaces: Optional[List[str]] = None,
    ) -> List[Match]:
        """Get matches in Biolexica's format."""
        return [
            Match.from_gilda(scored_match)
            for scored_match in super().ground(
                s, context=context, organisms=organisms, namespaces=namespaces
            )
        ]

    def get_best_match(
        self,
        s: str,
        context: Optional[str] = None,
        organisms: Optional[List[str]] = None,
        namespaces: Optional[List[str]] = None,
    ) -> Optional[Match]:
        """Get the best match in Biolexica's format."""
        scored_matches = super().ground(
            s, context=context, organisms=organisms, namespaces=namespaces
        )
        if not scored_matches:
            return None
        return Match.from_gilda(scored_matches[0])

    def annotate(self, text: str, **kwargs: Any) -> List[Annotation]:
        """Annotate the text."""
        import gilda.ner

        return [
            Annotation(text=text, match=Match.from_gilda(match), start=start, end=end)
            for text, match, start, end in gilda.ner.annotate(text, grounder=self, **kwargs)
        ]


def load_grounder(grounder: GrounderHint) -> Grounder:
    """Load a gilda grounder, potentially from a remote location."""
    if isinstance(grounder, str):
        if grounder in PREDEFINED:
            if LEXICA.is_dir():
                # If biolexica is installed in editable mode, try looking for
                # the directory outside the package root and load the predefined
                # index directly
                grounder = LEXICA.joinpath(grounder, "terms.tsv.gz").as_posix()
            else:
                grounder = URL_FMT.format(key=grounder)
        if grounder.startswith("http"):
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory).joinpath("terms.tsv.gz")
                urlretrieve(grounder, path)  # noqa:S310
                return Grounder(path)
    if isinstance(grounder, (str, Path)):
        path = Path(grounder).resolve()
        if not path.is_file():
            raise FileNotFoundError(path)
        return Grounder(grounder)
    if isinstance(grounder, Grounder):
        return grounder
    if isinstance(grounder, gilda.Grounder):
        return Grounder(grounder.entries)
    raise TypeError


def assemble_grounder(
    configuration: Configuration,
    mappings: Optional[List["semra.Mapping"]] = None,
    *,
    extra_terms: Optional[List["gilda.Term"]] = None,
    include_biosynonyms: bool = True,
) -> Grounder:
    """Assemble terms from multiple resources and load into a grounder."""
    terms = assemble_terms(
        configuration=configuration,
        mappings=mappings,
        include_biosynonyms=include_biosynonyms,
        extra_terms=extra_terms,
    )
    grounder = Grounder(list(terms))
    return grounder


def _term_curie(term: gilda.Term) -> str:
    return f"{term.db}:{term.id}"


def assemble_terms(
    configuration: Configuration,
    mappings: Optional[List["semra.Mapping"]] = None,
    *,
    extra_terms: Optional[List["gilda.Term"]] = None,
    include_biosynonyms: bool = True,
    raw_path: Optional[Path] = None,
    processed_path: Optional[Path] = None,
) -> List[gilda.Term]:
    """Assemble terms from multiple resources."""
    terms: List[gilda.Term] = []
    for inp in configuration.inputs:
        if inp.processor in {"pyobo", "bioontologies"}:
            terms.extend(
                iter_terms_by_prefix(
                    inp.source,
                    ancestors=inp.ancestors,
                    processor=inp.processor,
                    **(inp.kwargs or {}),
                )
            )
        elif inp.processor == "biosynonyms":
            terms.extend(s.as_gilda_term() for s in biosynonyms.parse_synonyms(inp.source))
        elif inp.processor == "gilda":
            terms.extend(load_entries_from_terms_file(inp.source))
        else:
            raise ValueError(f"Unknown processor {inp.processor}")

    if extra_terms:
        terms.extend(extra_terms)

    if include_biosynonyms:
        terms.extend(biosynonyms.get_gilda_terms())

    if raw_path is not None:
        logger.info("Writing %d raw terms to %s", len(terms), raw_path)
        gilda.term.dump_terms(terms, raw_path)

    if mappings is not None:
        from semra.gilda_utils import update_terms

        terms = update_terms(terms, mappings)

    if configuration.excludes:
        _excludes_set = set(configuration.excludes)
        terms = [term for term in terms if _term_curie(term) not in _excludes_set]

    if processed_path is not None:
        logger.info("Writing %d processed terms to %s", len(terms), processed_path)
        gilda.term.dump_terms(terms, processed_path)

    return terms


def iter_terms_by_prefix(
    prefix: str, *, ancestors: Union[None, str, List[str]] = None, processor: Processor, **kwargs
) -> Iterable[gilda.Term]:
    """Iterate over all terms from a given prefix."""
    if processor == "pyobo":
        if ancestors is None:

            import pyobo.gilda_utils

            yield from pyobo.gilda_utils.get_gilda_terms(prefix, **kwargs)
        else:
            yield from _get_pyobo_subset_terms(prefix, ancestors, **kwargs)
    elif processor == "bioontologies":
        if ancestors is None:
            import bioontologies.gilda_utils

            yield from bioontologies.gilda_utils.get_gilda_terms(prefix, **kwargs)
        else:
            yield from _get_bioontologies_subset_terms(prefix, ancestors, **kwargs)
    else:
        raise ValueError(f"Unknown processor: {processor}")


def _get_pyobo_subset_terms(
    source: str, ancestors: Union[str, List[str]], **kwargs
) -> Iterable[gilda.Term]:
    from pyobo.gilda_utils import get_gilda_terms

    subset = {
        descendant
        for parent_curie in _ensure_list(ancestors)
        for descendant in pyobo.get_descendants(*parent_curie.split(":")) or []
    }
    for term in get_gilda_terms(source, **kwargs):
        if bioregistry.curie_to_str(term.db, term.id) in subset:
            yield term


def _ensure_list(s: Union[str, List[str]]) -> List[str]:
    if isinstance(s, str):
        return [s]
    return s


def _get_bioontologies_subset_terms(
    source: str, parent_curie: Union[str, List[str]], check: bool = False, **kwargs
) -> Iterable[gilda.Term]:
    import bioontologies
    import networkx as nx

    parse_results = bioontologies.get_obograph_by_prefix(source, check=check, **kwargs)
    obograph = parse_results.squeeze().standardize(prefix=source)
    graph = nx.DiGraph()
    for edge in obograph.edges:
        if (
            edge.subject
            and edge.predicate
            and edge.object
            and edge.predicate.curie == "rdfs:subClassOf"
        ):
            graph.add_edge(edge.subject.curie, edge.object.curie)

    descendant_curies = {
        descendant for c in _ensure_list(parent_curie) for descendant in nx.ancestors(graph, c)
    }

    for node in tqdm(obograph.nodes, leave=False):
        if not node.name or node.reference is None or node.reference.curie not in descendant_curies:
            continue
        yield gilda.Term(
            norm_text=normalize(node.name),
            text=node.name,
            db=node.reference.prefix,
            id=node.reference.identifier,
            entry_name=node.name,
            status="name",
            source=source,
        )
        for synonym in node.synonyms:
            yield gilda.Term(
                norm_text=normalize(synonym.value),
                text=synonym.value,
                db=node.reference.prefix,
                id=node.reference.identifier,
                entry_name=node.name,
                status="synonym",
                source=source,
            )


def get_mesh_category_curies(letter, skip=None) -> List[str]:
    """Get the MeSH LUIDs for a category, by letter (e.g., "A")."""
    # see https://meshb.nlm.nih.gov/treeView

    import bioversions
    from pyobo.sources.mesh import get_tree_to_mesh_id

    mesh_version = bioversions.get_version("mesh")
    if mesh_version is None:
        raise ValueError
    tree_to_mesh = get_tree_to_mesh_id(mesh_version)
    rv = []
    for i in range(1, 100):
        key = f"{letter}{i:02}"
        if skip and key in skip:
            continue
        mesh_id = tree_to_mesh.get(key)
        if mesh_id is None:
            break
        rv.append(f"mesh:{mesh_id}")
    return rv
