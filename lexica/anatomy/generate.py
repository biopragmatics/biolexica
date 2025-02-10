# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "biolexica",
#     "pyobo",
#     "semra",
#     "bioontologies",
#     "ssslm[gilda-slim]",
# ]
#
# [tool.uv.sources]
# semra = { path = "../../../semra", editable = true  }
# biolexica = { path = "../..", editable = true  }
# pyobo = { path = "../../../pyobo", editable = true }
# ssslm = { path = "../../../ssslm", editable = true }
# bioontologies = { path = "../../../bioontologies", editable = true }
#
# ///

from pathlib import Path

import click
import semra
from more_click import verbose_option
from pyobo.sources.mesh import get_mesh_category_curies

import biolexica

HERE = Path(__file__).parent.resolve()
LITERAL_MAPPINGS_PATH = HERE.joinpath("anatomy.ssslm.tsv.gz")
GILDA_PATH = HERE.joinpath("terms.tsv.gz")

PRIORITY = [
    "uberon",
    "mesh",
    "bto",
    "caro",
    "ncit",
    # "umls", # TODO find appropriate subset
]

SEMRA_CONFIG = semra.Configuration(
    name="Anatomy mappings",
    inputs=[
        semra.Input(source="biomappings"),
        semra.Input(source="gilda"),
        semra.Input(prefix="uberon", source="pyobo", confidence=0.99),
        semra.Input(prefix="bto", source="pyobo", confidence=0.99),
        semra.Input(prefix="caro", source="pyobo", confidence=0.99),
        semra.Input(prefix="mesh", source="pyobo", confidence=0.99),
        semra.Input(
            prefix="ncit",
            source="pyobo",
            confidence=0.99,
        ),
        # semra.Input(prefix="umls", source="pyobo", confidence=0.99),
    ],
    add_labels=False,
    priority=PRIORITY,
    keep_prefixes=PRIORITY,
    remove_imprecise=False,
    mutations=[
        semra.Mutation(source="uberon", confidence=0.8),
        semra.Mutation(source="bto", confidence=0.65),
        semra.Mutation(source="caro", confidence=0.8),
        semra.Mutation(source="ncit", confidence=0.7),
        # semra.Mutation(source="umls", confidence=0.7),
    ],
    raw_pickle_path=HERE.joinpath("mappings_raw.pkl.gz"),
    processed_pickle_path=HERE.joinpath("mappings_processed.pkl.gz"),
    priority_pickle_path=HERE.joinpath("mappings_prioritized.pkl"),
)

BIOLEXICA_CONFIG = biolexica.Configuration(
    inputs=[
        biolexica.Input(source="uberon", processor="pyobo"),
        biolexica.Input(
            source="mesh",
            # skip A11 since it's cells
            ancestors=get_mesh_category_curies("A", skip=["A11"]),
            processor="pyobo",
        ),
        biolexica.Input(
            source="ncit",
            ancestors=[
                "NCIT:C12219",  # Anatomic Structure, System, or Substance
            ],
            processor="pyobo",
            kwargs=dict(version="2024-05-07"),
        ),
        biolexica.Input(source="bto", processor="pyobo"),
        biolexica.Input(source="caro", processor="pyobo"),
    ],
    mapping_configuration=SEMRA_CONFIG,
)


@click.command()
@verbose_option
def _main() -> None:
    biolexica.assemble_terms(
        BIOLEXICA_CONFIG,
        processed_path=LITERAL_MAPPINGS_PATH,
        gilda_path=GILDA_PATH,
    )


if __name__ == "__main__":
    _main()
