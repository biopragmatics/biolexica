"""API for assembling biomedial lexica."""

from __future__ import annotations

import logging
import typing as t
from collections import Counter
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, TypeAlias

import ssslm
from curies import Reference
from pydantic import BaseModel, Field
from ssslm import LiteralMapping

if TYPE_CHECKING:
    import semra

__all__ = [
    "PREDEFINED",
    "Configuration",
    "Input",
    "Processor",
    "assemble_grounder",
    "assemble_terms",
    "get_literal_mappings",
    "load_grounder",
    "summarize_terms",
]

logger = logging.getLogger(__name__)

HERE = Path(__file__).parent.resolve()
LEXICA = HERE.parent.parent.joinpath("lexica")

#: A processor available as a literal mapping input
Processor: TypeAlias = Literal["pyobo", "bioontologies", "ssslm", "gilda"]


class Input(BaseModel):  # type:ignore
    """An input towards lexicon assembly."""

    processor: Processor
    source: str
    ancestors: None | str | list[str] = None
    kwargs: dict[str, Any] | None = None


class Configuration(BaseModel):
    """A configuration for construction of a lexicon."""

    inputs: list[Input]
    excludes: list[Reference] | None = Field(
        default=None,
        description="A list of CURIEs to exclude after processing is complete",
    )
    mapping_configuration: semra.Configuration | None = None


PREDEFINED: TypeAlias = Literal["cell", "anatomy", "phenotype", "obo"]
URL_FMT = "https://github.com/biopragmatics/biolexica/raw/main/lexica/{key}/{key}.ssslm.tsv.gz"


def load_grounder(grounder: ssslm.GrounderHint) -> ssslm.Grounder:
    """Load a grounder, potentially from a remote location."""
    if isinstance(grounder, str) and grounder in t.get_args(PREDEFINED):
        if LEXICA.is_dir():
            # If biolexica is installed in editable mode, try looking for
            # the directory outside the package root and load the predefined
            # index directly
            grounder = LEXICA.joinpath(grounder, f"{grounder}.ssslm.tsv.gz").as_posix()
        else:
            grounder = URL_FMT.format(key=grounder)
    return ssslm.make_grounder(grounder)


def assemble_grounder(
    configuration: Configuration,
    mappings: list[semra.Mapping] | None = None,
    *,
    extra_terms: list[LiteralMapping] | None = None,
    include_biosynonyms: bool = True,
) -> ssslm.Grounder:
    """Assemble terms from multiple resources and load into a grounder."""
    literal_mappings = assemble_terms(
        configuration=configuration,
        mappings=mappings,
        include_biosynonyms=include_biosynonyms,
        extra_terms=extra_terms,
    )
    return ssslm.make_grounder(literal_mappings)


def assemble_terms(  # noqa:C901
    configuration: Configuration,
    mappings: list[semra.Mapping] | None = None,
    *,
    extra_terms: list[LiteralMapping] | None = None,
    include_biosynonyms: bool = True,
    raw_path: Path | None = None,
    processed_path: Path | None = None,
    gilda_path: Path | None = None,
    summary_path: Path | None = None,
) -> list[LiteralMapping]:
    """Assemble terms from multiple resources."""
    terms: list[LiteralMapping] = []
    for inp in configuration.inputs:
        if inp.processor in {"pyobo", "bioontologies"}:
            terms.extend(
                get_literal_mappings(
                    inp.source,
                    ancestors=inp.ancestors,
                    processor=inp.processor,
                    **(inp.kwargs or {}),
                )
            )
        elif inp.processor == "ssslm":
            terms.extend(ssslm.read_literal_mappings(inp.source))
        elif inp.processor == "gilda":
            terms.extend(ssslm.read_gilda_terms(inp.source))
        else:
            raise ValueError(f"Unknown processor {inp.processor}")

    if extra_terms:
        terms.extend(extra_terms)

    if include_biosynonyms:
        import biosynonyms

        terms.extend(biosynonyms.get_positive_synonyms())

    if raw_path is not None:
        logger.info("Writing %d raw literal mappings to %s", len(terms), raw_path)
        ssslm.write_literal_mappings(terms, raw_path)

    _mappings: list[semra.Mapping] = []
    if configuration.mapping_configuration is not None:
        from semra.pipeline import AssembleReturnType

        _mappings.extend(
            configuration.mapping_configuration.get_mappings(
                return_type=AssembleReturnType.priority
            )
        )
    if mappings is not None:
        _mappings.extend(mappings)

    if _mappings is not None:
        from semra.api import assert_projection

        assert_projection(_mappings)
        terms = ssslm.remap_literal_mappings(
            literal_mappings=terms,
            mappings=[(mapping.subject, mapping.object) for mapping in _mappings],
        )

    if configuration.excludes:
        _excludes_set = set(configuration.excludes)
        terms = [term for term in terms if term.reference not in _excludes_set]

    if processed_path is not None:
        logger.info("Writing %d processed literal mappings to %s", len(terms), processed_path)
        ssslm.write_literal_mappings(terms, processed_path)

    if gilda_path is not None:
        ssslm.write_gilda_terms(terms, gilda_path)

    if summary_path is not None:
        summary = summarize_terms(terms)
        summary_path.write_text(summary.model_dump_json(indent=2))

    return terms


def get_literal_mappings(
    prefix: str,
    *,
    ancestors: None | str | Sequence[str] = None,
    processor: Processor,
    **kwargs: Any,
) -> list[ssslm.LiteralMapping]:
    """Iterate over all terms from a given prefix."""
    if ancestors is None:
        ancestor_refs = None
    elif isinstance(ancestors, str):
        ancestor_refs = [Reference.from_curie(ancestors)]
    else:
        ancestor_refs = [Reference.from_curie(a) for a in ancestors]
    if processor == "pyobo":
        import pyobo

        kwargs.setdefault("strict", False)

        if ancestor_refs is None:
            return pyobo.get_literal_mappings(prefix, **kwargs)
        else:
            return pyobo.get_literal_mappings_subset(prefix, ancestors=ancestor_refs, **kwargs)
    elif processor == "bioontologies":
        import bioontologies

        if ancestor_refs is None:
            return list(bioontologies.get_literal_mappings(prefix, **kwargs))
        else:
            return list(
                bioontologies.get_literal_mappings_subset(prefix, ancestors=ancestor_refs, **kwargs)
            )
    else:
        raise ValueError(f"Unknown processor: {processor}")


class Summary(BaseModel):
    """A model for summaries."""

    count: int
    provenance_counter: dict[str, int]
    type_counter: dict[str, int]


def summarize_terms(literal_mappings: list[LiteralMapping]) -> BaseModel:
    """Summarize terms."""
    provenance_counter: Counter[str] = Counter()
    type_counter: Counter[str] = Counter()
    for mapping in literal_mappings:
        for ref in mapping.provenance:
            provenance_counter[ref.prefix] += 1
        if mapping.type is not None:
            type_counter[mapping.type.curie] += 1
    return Summary(
        count=len(literal_mappings),
        provenance_counter=dict(provenance_counter),
        type_counter=dict(type_counter),
    )
