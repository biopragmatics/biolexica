"""API for assembling biomedial lexica."""

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Sequence, Union

import ssslm
from curies import Reference
from pydantic import BaseModel, Field
from ssslm import LiteralMapping

if TYPE_CHECKING:
    import semra

__all__ = [
    "Configuration",
    "Input",
    "assemble_terms",
    "get_literal_mappings_by_prefix",
    "load_grounder",
]

logger = logging.getLogger(__name__)

HERE = Path(__file__).parent.resolve()
LEXICA = HERE.parent.parent.joinpath("lexica")
Processor = Literal["pyobo", "bioontologies", "ssslm", "gilda"]


class Input(BaseModel):  # type:ignore
    """An input towards lexicon assembly."""

    processor: Processor
    source: str
    ancestors: Union[None, str, List[str]] = None
    kwargs: Optional[Dict[str, Any]] = None


class Configuration(BaseModel):
    """A configuration for construction of a lexicon."""

    inputs: List[Input]
    excludes: Optional[List[Reference]] = Field(
        default=None,
        description="A list of CURIEs to exclude after processing is complete",
    )


PREDEFINED = ["cell", "anatomy", "phenotype", "obo"]
URL_FMT = "https://github.com/biopragmatics/biolexica/raw/main/lexica/{key}/{key}.ssslm.tsv.gz"


def load_grounder(grounder: ssslm.GrounderHint) -> ssslm.Grounder:
    """Load a grounder, potentially from a remote location."""
    if isinstance(grounder, str) and grounder in PREDEFINED:
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
    mappings: Optional[List["semra.Mapping"]] = None,
    *,
    extra_terms: Optional[List[LiteralMapping]] = None,
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


def assemble_terms(
    configuration: Configuration,
    mappings: Optional[List["semra.Mapping"]] = None,
    *,
    extra_terms: Optional[List[LiteralMapping]] = None,
    include_biosynonyms: bool = True,
    raw_path: Optional[Path] = None,
    processed_path: Optional[Path] = None,
    gilda_path: Optional[Path] = None,
) -> List[LiteralMapping]:
    """Assemble terms from multiple resources."""
    terms: List[LiteralMapping] = []
    for inp in configuration.inputs:
        if inp.processor in {"pyobo", "bioontologies"}:
            terms.extend(
                get_literal_mappings_by_prefix(
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

    if mappings is not None:
        from semra.api import assert_projection

        assert_projection(mappings)
        terms = ssslm.remap_literal_mappings(
            literal_mappings=terms,
            mappings=[(mapping.s, mapping.o) for mapping in mappings],
        )

    if configuration.excludes:
        _excludes_set = set(configuration.excludes)
        terms = [term for term in terms if term.reference not in _excludes_set]

    if processed_path is not None:
        logger.info("Writing %d processed literal mappings to %s", len(terms), processed_path)
        ssslm.write_literal_mappings(terms, processed_path)

    if gilda_path is not None:
        ssslm.write_gilda_terms(terms, gilda_path)

    return terms


def get_literal_mappings_by_prefix(
    prefix: str,
    *,
    ancestors: Union[None, str, Sequence[str]] = None,
    processor: Processor,
    **kwargs,
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
