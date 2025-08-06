# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "biolexica",
#     "pyobo",
#     "semra",
#     "bioontologies",
#     "ssslm[gilda-slim]",
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

"""Generate a lexical index for anatomy resources."""

from pathlib import Path

import click

import biolexica
from biolexica.configs import ANATOMY_CONFIGURATION

HERE = Path(__file__).parent.resolve()
LITERAL_MAPPINGS_PATH = HERE.joinpath("anatomy.ssslm.tsv.gz")
GILDA_PATH = HERE.joinpath("terms.tsv.gz")
SUMMARY_PATH = HERE.joinpath("summary.json")


@click.command()
def _main() -> None:
    """Generate a lexical index for anatomy resources."""
    biolexica.assemble_terms(
        ANATOMY_CONFIGURATION,
        processed_path=LITERAL_MAPPINGS_PATH,
        gilda_path=GILDA_PATH,
        summary_path=SUMMARY_PATH,
    )


if __name__ == "__main__":
    _main()
