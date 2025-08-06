"""Configuration for an anatomy lexical index."""

import semra.landscape.anatomy
from pyobo.sources.mesh import get_mesh_category_curies

import biolexica

__all__ = ["ANATOMY_CONFIGURATION"]

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
    mapping_configuration=semra.landscape.anatomy.ANATOMY_CONFIGURATION,
)
