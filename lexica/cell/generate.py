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

"""Generate a lexical index for cell resources."""

from pathlib import Path

import semra

import biolexica

HERE = Path(__file__).parent.resolve()
LITERAL_MAPPINGS_PATH = HERE.joinpath("cell.ssslm.tsv.gz")
GILDA_PATH = HERE.joinpath("terms.tsv.gz")

PRIORITY = ["cl", "cellosaurus", "bto", "clo", "efo", "mesh", "ccle", "depmap"]
BIOLEXICA_CONFIG = biolexica.Configuration(
    inputs=[
        biolexica.Input(
            source="mesh", processor="pyobo", ancestors=["mesh:D002477"]
        ),  # cells (A11)
        biolexica.Input(source="efo", processor="pyobo", ancestors=["efo:0000324"]),
        biolexica.Input(source="cellosaurus", processor="pyobo"),
        biolexica.Input(source="ccle", processor="pyobo"),
        biolexica.Input(source="bto", processor="pyobo"),
        biolexica.Input(source="cl", processor="pyobo"),
        biolexica.Input(source="clo", processor="pyobo"),
        biolexica.Input(
            source="ncit",
            processor="pyobo",
            ancestors=["ncit:C12508", "ncit:C192998"],
            # kwargs={"version": "2024-05-07"},
        ),
        biolexica.Input(
            source="umls",
            processor="pyobo",
            ancestors=[
                "umls:C0007634",  # cell
                "umls:C0007600",  # cell line
            ],
        ),
    ]
)

SEMRA_CONFIG = semra.Configuration(
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
        semra.Input(prefix="ncit", source="pyobo", confidence=0.99),
        semra.Input(
            prefix="umls",
            source="pyobo",
            confidence=0.99,
            # extras={"version": "2023AB"},
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
        semra.Mutation(source="ncit", confidence=0.7),
        semra.Mutation(source="umls", confidence=0.7),
    ],
    raw_pickle_path=HERE.joinpath("mappings_raw.pkl.gz"),
    processed_pickle_path=HERE.joinpath("mappings_processed.pkl.gz"),
    priority_pickle_path=HERE.joinpath("mappings_prioritized.pkl"),
)


def _main() -> None:
    """Generate a lexical index for cell resources."""
    mappings = SEMRA_CONFIG.get_mappings()
    biolexica.assemble_terms(
        BIOLEXICA_CONFIG,
        mappings=mappings,
        processed_path=LITERAL_MAPPINGS_PATH,
        gilda_path=GILDA_PATH,
    )


if __name__ == "__main__":
    _main()
