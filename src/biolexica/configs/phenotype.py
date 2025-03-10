"""Configuration for a phenotype lexical index."""

import semra
from pyobo.sources.mesh import get_mesh_category_curies

import biolexica

__all__ = ["PHENOTYPE_CONFIGURATION"]

PRIORITY = [
    "doid",
    "mondo",
    "hp",
    "symp",
    "mesh",
    "efo",
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
        semra.Input(prefix="umls", source="pyobo", confidence=0.99),
        semra.Input(prefix="ncit", source="pyobo", confidence=0.99),
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
        semra.Mutation(source="umls", confidence=0.7),
        semra.Mutation(source="ncit", confidence=0.7),
    ],
)

PHENOTYPE_CONFIGURATION = biolexica.Configuration(
    inputs=[
        biolexica.Input(source="doid", processor="pyobo"),
        biolexica.Input(source="mondo", processor="pyobo"),
        biolexica.Input(source="hp", processor="pyobo"),
        biolexica.Input(source="symp", processor="pyobo"),
        biolexica.Input(
            source="mesh",
            processor="pyobo",
            ancestors=[
                *get_mesh_category_curies("C"),
                *get_mesh_category_curies("F"),
                # TODO should there be others?
            ],
        ),
        biolexica.Input(source="efo", processor="pyobo", ancestors=["EFO:0000408"]),
        biolexica.Input(source="ncit", processor="pyobo", ancestors=["ncit:C2991"]),
        biolexica.Input(source="umls", processor="pyobo", ancestors=["umls:C0012634"]),
    ],
    excludes=["doid:4"],
    mapping_configuration=SEMRA_CONFIG,
)
