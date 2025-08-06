"""Configuration for a cell lexical index."""

import semra
import semra.landscape.cell

import biolexica

__all__ = ["CELL_CONFIGURATION"]

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
    mapping_configuration=semra.landscape.cell.CELL_CONFIGURATION,
)
