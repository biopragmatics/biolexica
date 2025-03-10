"""Configuration for a cell lexical index."""

import semra

import biolexica

__all__ = ["CELL_CONFIGURATION"]


PRIORITY = [
    "cl",
    "cellosaurus",
    "bto",
    "clo",
    "efo",
    "mesh",
    "ccle",
    "depmap",
]


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
        semra.Input(prefix="umls", source="pyobo", confidence=0.99),
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
)

CELL_CONFIGURATION = biolexica.Configuration(
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
            source="ncit", processor="pyobo", ancestors=["ncit:C12508", "ncit:C192998"]
        ),
        biolexica.Input(
            source="umls",
            processor="pyobo",
            ancestors=[
                "umls:C0007634",  # cell
                "umls:C0007600",  # cell line
            ],
        ),
    ],
    mapping_configuration=SEMRA_CONFIG,
)
