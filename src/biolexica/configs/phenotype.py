"""Configuration for a phenotype lexical index."""

import semra.landscape.disease
from pyobo.sources.mesh import get_mesh_category_curies

import biolexica

__all__ = ["PHENOTYPE_CONFIGURATION"]

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
    mapping_configuration=semra.landscape.disease.DISEASE_CONFIGURATION,
)
