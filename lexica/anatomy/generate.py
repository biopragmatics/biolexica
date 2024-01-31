from pathlib import Path

import semra

import biolexica

HERE = Path(__file__).parent.resolve()
TERMS_PATH = HERE.joinpath("terms.tsv.gz")

PRIORITY = [
    "uberon",
    "mesh",
    "bto",
    "caro",
]
BIOLEXICA_CONFIG = [
    biolexica.Input(source="uberon", processor="pyobo"),
    biolexica.Input(
        source="mesh", ancestors=biolexica.get_mesh_category_curies("A"), processor="pyobo"
    ),
    biolexica.Input(source="bto", processor="pyobo"),
    biolexica.Input(source="caro", processor="pyobo"),
]

SEMRA_CONFIG = semra.Configuration(
    name="Anatomy mappints",
    description="Originally a reproduction of the EFO/Cellosaurus/DepMap/CCLE scenario "
    "posed in the Biomappings paper, this configuration imports several different cell and "
    "cell line resources and identifies mappings between them.",
    inputs=[
        semra.Input(source="biomappings"),
        semra.Input(source="gilda"),
        semra.Input(prefix="uberon", source="pyobo", confidence=0.99),
        semra.Input(prefix="bto", source="pyobo", confidence=0.99),
        semra.Input(prefix="caro", source="pyobo", confidence=0.99),
        semra.Input(prefix="mesh", source="pyobo", confidence=0.99),
    ],
    add_labels=False,
    priority=PRIORITY,
    keep_prefixes=PRIORITY,
    remove_imprecise=False,
    mutations=[
        semra.Mutation(source="uberon", confidence=0.8),
        semra.Mutation(source="bto", confidence=0.65),
        semra.Mutation(source="caro", confidence=0.8),
    ],
    raw_pickle_path=HERE.joinpath("mappings_raw.pkl.gz"),
    processed_pickle_path=HERE.joinpath("mappings_processed.pkl.gz"),
    priority_pickle_path=HERE.joinpath("mappings_prioritized.pkl"),
)


def _main() -> None:
    mappings = SEMRA_CONFIG.get_mappings()
    biolexica.assemble_terms(
        inputs=BIOLEXICA_CONFIG,
        mappings=mappings,
        processed_path=TERMS_PATH,
    )


if __name__ == "__main__":
    _main()
