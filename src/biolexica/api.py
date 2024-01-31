"""API for assembling biomedial lexica."""

import logging
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Iterable, List, Literal, Optional, Union
from urllib.request import urlretrieve

import bioregistry
import biosynonyms
import gilda
import pyobo
from gilda.grounder import load_entries_from_terms_file
from gilda.process import normalize
from pydantic import BaseModel
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
]

logger = logging.getLogger(__name__)

HERE = Path(__file__).parent.resolve()
Processor = Literal["pyobo", "bioontologies", "biosynonyms", "gilda"]

GrounderHint = Union[gilda.Grounder, str, Path]


class Input(BaseModel):
    """An input towards lexicon assembly."""

    processor: Processor
    source: str
    ancestors: Union[None, str, List[str]] = None


class Configuration(BaseModel):
    inputs: List[Input]
    excludes: Optional[List[str]] = None
    raw_path: Optional[Path] = None
    processed_path: Optional[Path] = None


PREDEFINED = ["cell", "anatomy", "phenotype"]
URL_FMT = "https://github.com/biopragmatics/biolexica/raw/main/lexica/{key}/terms.tsv.gz"


def load_grounder(grounder: GrounderHint) -> gilda.Grounder:
    """Load a gilda grounder, potentially from a remote location."""
    if isinstance(grounder, str):
        if grounder in PREDEFINED:
            grounder = URL_FMT.format(key=grounder)
        if grounder.startswith("http"):
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory).joinpath("terms.tsv.gz")
                urlretrieve(grounder, path)  # noqa:S310
                return gilda.Grounder(path)
    if isinstance(grounder, (str, Path)):
        path = Path(grounder).resolve()
        if not path.is_file():
            raise FileNotFoundError(path)
        return gilda.Grounder(grounder)
    return grounder


def assemble_grounder(
    configuration: Configuration,
    mappings: Optional[List["semra.Mapping"]] = None,
    *,
    extra_terms: Optional[List["gilda.Term"]] = None,
    include_biosynonyms: bool = True,
) -> gilda.Grounder:
    """Assemble terms from multiple resources and load into a grounder."""
    terms = assemble_terms(
        configuration=configuration,
        mappings=mappings,
        include_biosynonyms=include_biosynonyms,
        extra_terms=extra_terms,
    )
    grounder = gilda.Grounder(list(terms))
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
                iter_terms_by_prefix(inp.source, ancestors=inp.ancestors, processor=inp.processor)
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
    prefix: str, *, ancestors: Union[None, str, List[str]] = None, processor: Processor
) -> Iterable[gilda.Term]:
    """Iterate over all terms from a given prefix."""
    if processor == "pyobo":
        if ancestors is None:

            import pyobo.gilda_utils

            yield from pyobo.gilda_utils.get_gilda_terms(prefix)
        else:
            yield from _get_pyobo_subset_terms(prefix, ancestors)
    elif processor == "bioontologies":
        if ancestors is None:
            import bioontologies.gilda_utils

            yield from bioontologies.gilda_utils.get_gilda_terms(prefix)
        else:
            yield from _get_bioontologies_subset_terms(prefix, ancestors)
    else:
        raise ValueError(f"Unknown processor: {processor}")


def _get_pyobo_subset_terms(source: str, ancestors: Union[str, List[str]]) -> Iterable[gilda.Term]:
    from pyobo.gilda_utils import get_gilda_terms

    subset = {
        descendant
        for parent_curie in _ensure_list(ancestors)
        for descendant in pyobo.get_descendants(*parent_curie.split(":")) or []
    }
    for term in get_gilda_terms(source):
        if bioregistry.curie_to_str(term.db, term.id) in subset:
            yield term


def _ensure_list(s: Union[str, List[str]]) -> List[str]:
    if isinstance(s, str):
        return [s]
    return s


def _get_bioontologies_subset_terms(
    source: str, parent_curie: Union[str, List[str]]
) -> Iterable[gilda.Term]:
    import bioontologies
    import networkx as nx

    parse_results = bioontologies.get_obograph_by_prefix(source, check=False)
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
