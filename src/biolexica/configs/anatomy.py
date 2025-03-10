"""Configuration for an anatomy lexical index."""

import semra
from pyobo.sources.mesh import get_mesh_category_curies

import biolexica

__all__ = ["ANATOMY_CONFIGURATION"]

PRIORITY = [
    "uberon",
    "mesh",
    "bto",
    "caro",
    "ncit",
    "umls",
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
        semra.Input(prefix="ncit", source="pyobo", confidence=0.99),
        semra.Input(prefix="umls", source="pyobo", confidence=0.99),
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
        semra.Mutation(source="umls", confidence=0.7),
    ],
)

ANATOMY_CONFIGURATION = biolexica.Configuration(
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
                "ncit:C12219",  # Anatomic Structure, System, or Substance
            ],
            processor="pyobo",
        ),
        biolexica.Input(source="bto", processor="pyobo"),
        biolexica.Input(source="caro", processor="pyobo"),
        biolexica.Input(
            source="umls", processor="pyobo", ancestors=["umls:C0700276", "umls:C1515976"]
        ),
    ],
    mapping_configuration=SEMRA_CONFIG,
)
