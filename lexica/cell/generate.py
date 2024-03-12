from pathlib import Path

import semra

import biolexica

HERE = Path(__file__).parent.resolve()
TERMS_PATH = HERE.joinpath("terms.tsv.gz")

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
            source="ncit", processor="pyobo", ancestors=["ncit:C192998"]  # probably incomplete
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
        semra.Input(prefix="ncit", source="pyobo", confidence=0.99),
        semra.Input(prefix="umls", source="pyobo", confidence=0.99, extras={"version": "2023AB"}),
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
        semra.Mutation(source="ncit", confidence=0.7),
        semra.Mutation(source="umls", confidence=0.7),
    ],
    raw_pickle_path=HERE.joinpath("mappings_raw.pkl.gz"),
    processed_pickle_path=HERE.joinpath("mappings_processed.pkl.gz"),
    priority_pickle_path=HERE.joinpath("mappings_prioritized.pkl"),
)


def _main() -> None:
    mappings = SEMRA_CONFIG.get_mappings()
    biolexica.assemble_terms(
        BIOLEXICA_CONFIG,
        mappings=mappings,
        processed_path=TERMS_PATH,
    )


if __name__ == "__main__":
    _main()
