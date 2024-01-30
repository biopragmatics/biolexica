"""API for assembling biomedial lexica."""

from pathlib import Path
from typing import TYPE_CHECKING, Iterable, List, Literal, Optional

import bioregistry
import biosynonyms
import gilda
import pyobo
from gilda.process import normalize
from pydantic import BaseModel
from tqdm.auto import tqdm

if TYPE_CHECKING:
    import semra

__all__ = [
    "Input",
    "assemble_terms",
    "iter_terms_by_prefix",
]

HERE = Path(__file__).parent.resolve()
Processor = Literal["pyobo", "bioontologies", "biosynonyms"]


class Input(BaseModel):
    """An input towards lexicon assembly."""

    processor: Processor
    source: str
    ancestors: None | str | list[str] = None


def assemble_grounder(
    inputs: list[Input],
    mappings: Optional[List["semra.Mapping"]] = None,
    *,
    include_biosynonyms: bool = True,
) -> gilda.Grounder:
    terms = assemble_terms(
        inputs=inputs, mappings=mappings, include_biosynonyms=include_biosynonyms
    )
    grounder = gilda.Grounder(list(terms))
    return grounder


def assemble_terms(
    inputs: list[Input],
    mappings: Optional[List["semra.Mapping"]] = None,
    *,
    include_biosynonyms: bool = True,
) -> list[gilda.Term]:
    """Assemble terms from multiple resources."""
    terms = []
    for inp in inputs:
        if inp.processor in {"pyobo", "bioontologies"}:
            terms.extend(
                iter_terms_by_prefix(
                    inp.source, ancestors=inp.ancestors, processor=inp.processor
                )
            )
        elif inp.processor == "biosynonyms":
            terms.extend(
                s.as_gilda_term() for s in biosynonyms.parse_synonyms(inp.source)
            )
        else:
            raise ValueError(f"Unknown processor {inp.processor}")

    if include_biosynonyms:
        terms.extend(biosynonyms.get_gilda_terms())

    if mappings is not None:
        from semra.gilda_utils import update_terms

        terms = update_terms(terms, mappings)

    return terms


def iter_terms_by_prefix(
    prefix: str, *, ancestors: None | str | list[str] = None, processor: Processor
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


def _get_pyobo_subset_terms(
    source: str, ancestors: str | list[str]
) -> Iterable[gilda.Term]:
    from pyobo.gilda_utils import get_gilda_terms

    subset = {
        descendant
        for parent_curie in _ensure_list(ancestors)
        for descendant in pyobo.get_descendants(*parent_curie.split(":"))
    }
    for term in get_gilda_terms(source):
        if bioregistry.curie_to_str(term.db, term.id) in subset:
            yield term


def _ensure_list(s: str | list[str]) -> list[str]:
    if isinstance(s, str):
        return [s]
    return s


def _get_bioontologies_subset_terms(
    source: str, parent_curie: str | list[str]
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
        descendant
        for c in _ensure_list(parent_curie)
        for descendant in nx.ancestors(graph, c)
    }

    for node in tqdm(obograph.nodes, leave=False):
        if (
            not node.name
            or node.reference is None
            or node.reference.curie not in descendant_curies
        ):
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


def _main() -> None:
    import pystow
    import semra

    PRIORITY = ["mesh", "efo", "cellosaurus", "ccle", "depmap", "bto", "cl", "clo"]
    MODULE = pystow.module("semra", "case-studies", "cancer-cell-lines")
    PRIORITY_SSSOM_PATH = MODULE.join(name="priority.sssom.tsv")

    biolexica_input = [
        Input(source="mesh", processor="pyobo", ancestors=["mesh:D002477"]),  # cells
        Input(source="efo", processor="pyobo", ancestors=["efo:0000324"]),
        Input(source="cellosaurus", processor="pyobo"),
        # Input(source="ccle", processor="pyobo"),
        Input(source="bto", processor="pyobo"),
        Input(source="cl", processor="pyobo"),
        Input(source="clo", processor="pyobo"),
    ]

    semra_config = semra.Configuration(
        name="Cell and Cell Line Mappings",
        description="Originally a reproduction of the EFO/Cellosaurus/DepMap/CCLE scenario "
        "posed in the Biomappings paper, this configuration imports several different cell and "
        "cell line resources and identifies mappings between them.",
        inputs=[
            semra.Input(source="biomappings"),
            semra.Input(source="gilda"),
            semra.Input(prefix="cellosaurus", source="pyobo", confidence=0.99),
            semra.Input(prefix="bto", source="bioontologies", confidence=0.99),
            semra.Input(prefix="cl", source="bioontologies", confidence=0.99),
            semra.Input(prefix="clo", source="custom", confidence=0.99),
            semra.Input(prefix="efo", source="pyobo", confidence=0.99),
            semra.Input(
                prefix="depmap",
                source="pyobo",
                confidence=0.99,
                extras={"version": "22Q4", "standardize": True, "license": "CC-BY-4.0"},
            ),
            semra.Input(
                prefix="ccle",
                source="pyobo",
                confidence=0.99,
                extras={"version": "2019"},
            ),
        ],
        add_labels=False,
        priority=PRIORITY,
        keep_prefixes=PRIORITY,
        remove_imprecise=False,
        mutations=[
            semra.Mutation(source="efo", confidence=0.7),
            semra.Mutation(source="bto", confidence=0.7),
            semra.Mutation(source="cl", confidence=0.7),
            semra.Mutation(source="clo", confidence=0.7),
            semra.Mutation(source="depmap", confidence=0.7),
            semra.Mutation(source="ccle", confidence=0.7),
            semra.Mutation(source="cellosaurus", confidence=0.7),
        ],
        raw_pickle_path=MODULE.join(name="raw.pkl"),
        raw_sssom_path=MODULE.join(name="raw.sssom.tsv"),
        raw_neo4j_path=MODULE.join("neo4j_raw"),
        processed_pickle_path=MODULE.join(name="processed.pkl"),
        processed_sssom_path=MODULE.join(name="processed.sssom.tsv"),
        processed_neo4j_path=MODULE.join("neo4j"),
        processed_neo4j_name="semra-cell",
        priority_pickle_path=MODULE.join(name="priority.pkl"),
        priority_sssom_path=PRIORITY_SSSOM_PATH,
    )

    mappings = semra_config.get_mappings()

    terms = assemble_terms(inputs=biolexica_input, mappings=mappings)
    gilda.term.dump_terms(terms, HERE.joinpath("terms.tsv.gz"))


if __name__ == "__main__":
    _main()
