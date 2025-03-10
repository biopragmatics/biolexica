# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "biolexica",
#     "pyobo",
#     "semra",
#     "ssslm[gilda-slim]",
#     "bioontologies",
#     "biomappings",
# ]
#
# [tool.uv.sources]
# semra = { path = "../../../semra", editable = true  }
# biolexica = { path = "../..", editable = true  }
# pyobo = { path = "../../../pyobo", editable = true }
# ssslm = { path = "../../../ssslm", editable = true }
# bioontologies = { path = "../../../bioontologies", editable = true }
# biomappings = { path = "../../../biomappings", editable = true }
#
# ///

"""Generate a lexical index for OBO Foundry ontologies."""

from pathlib import Path

import bioregistry
import click
import ssslm
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

from biolexica import get_literal_mappings, summarize_terms

HERE = Path(__file__).parent.resolve()
LITERAL_MAPPINGS_PATH = HERE.joinpath("obo.ssslm.tsv.gz")
GILDA_PATH = HERE.joinpath("terms.tsv.gz")
SUMMARY_PATH = HERE.joinpath("summary.json")
CACHE = HERE.joinpath("cache")
CACHE.mkdir(exist_ok=True, parents=True)


@click.command()
def main() -> None:
    """Generate a lexical index for OBO Foundry ontologies."""
    skip = {"pr"}
    prefixes = sorted(
        resource.prefix
        for resource in bioregistry.resources()
        if resource.get_obo_preferred_prefix()
        and not resource.is_deprecated()
        and not resource.no_own_terms
        and resource.prefix not in skip
    )

    literal_mappings: list[ssslm.LiteralMapping] = []
    for prefix in tqdm(prefixes, unit="ontology", desc="Extracting OBO literal mappings"):
        path = CACHE.joinpath(prefix).with_suffix(".ssslm.tsv.gz")
        if path.is_file():
            literal_mappings.extend(ssslm.read_literal_mappings(path))
        else:
            local_literal_mappings = list(get_literal_mappings(prefix, processor="bioontologies"))
            with logging_redirect_tqdm():
                ssslm.write_literal_mappings(path=path, literal_mappings=local_literal_mappings)
            literal_mappings.extend(local_literal_mappings)

    ssslm.write_literal_mappings(path=LITERAL_MAPPINGS_PATH, literal_mappings=literal_mappings)
    ssslm.write_gilda_terms(literal_mappings, GILDA_PATH)

    summary = summarize_terms(literal_mappings)
    SUMMARY_PATH.write_text(summary.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
