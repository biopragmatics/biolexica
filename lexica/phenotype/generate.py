from pathlib import Path

import semra

import biolexica

HERE = Path(__file__).parent.resolve()
TERMS_PATH = HERE.joinpath("terms.tsv.gz")

PRIORITY = [
    "doid",
    "mondo",
    "hp",
    "symp",
    "mesh",
    "efo",
]
BIOLEXICA_CONFIG = [
    biolexica.Input(source="doid", processor="pyobo"),
    biolexica.Input(source="mondo", processor="pyobo"),
    biolexica.Input(source="hp", processor="pyobo"),
    biolexica.Input(source="symp", processor="pyobo"),
    # TODO get subsets of MeSH (C for diseases, F for Psychiatry/Psychology,
    #  and maybe others. See https://meshb.nlm.nih.gov/treeView)
    biolexica.Input(source="mesh", processor="pyobo"),
    biolexica.Input(source="efo", processor="pyobo"),  # TODO find subset of EFO
    # biolexica.Input(source="umls", processor="pyobo"), # TODO find subset of UMLS
    # biolexica.Input(source="ncit", processor="pyobo"), # TODO find subset of NCIT
]

SEMRA_CONFIG = semra.Configuration(
    name="Cell and Cell Line Mappings",
    description="Originally a reproduction of the EFO/Cellosaurus/DepMap/CCLE scenario "
    "posed in the Biomappings paper, this configuration imports several different cell and "
    "cell line resources and identifies mappings between them.",
    inputs=[
        semra.Input(source="biomappings"),
        semra.Input(source="gilda"),
        semra.Input(prefix="doid", source="pyobo", confidence=0.99),
        semra.Input(prefix="mondo", source="pyobo", confidence=0.99),
        semra.Input(prefix="hp", source="pyobo", confidence=0.99),
        semra.Input(prefix="symp", source="pyobo", confidence=0.99),
        semra.Input(prefix="mesh", source="pyobo", confidence=0.99),
        semra.Input(prefix="efo", source="pyobo", confidence=0.99),
    ],
    add_labels=False,
    priority=PRIORITY,
    keep_prefixes=PRIORITY,
    remove_imprecise=False,
    mutations=[
        semra.Mutation(source="doid", confidence=0.7),
        semra.Mutation(source="mondo", confidence=0.7),
        semra.Mutation(source="hp", confidence=0.7),
        semra.Mutation(source="symp", confidence=0.7),
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
        output_path=TERMS_PATH,
    )


if __name__ == "__main__":
    _main()
