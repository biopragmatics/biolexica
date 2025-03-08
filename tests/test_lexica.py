"""Test loading and applying lexica."""

import typing
import unittest
from pathlib import Path
from typing import ClassVar

from ssslm import Grounder

import biolexica
from biolexica.api import PREDEFINED

HERE = Path(__file__).parent.resolve()
ROOT = HERE.parent
LEXICA = ROOT.joinpath("lexica")
CELL_TERMS = LEXICA.joinpath("cell", "terms.tsv.gz")
ANATOMY_TERMS = LEXICA.joinpath("anatomy", "terms.tsv.gz")
PHENOTYPE_TERMS = LEXICA.joinpath("phenotype", "terms.tsv.gz")


class TestLexica(unittest.TestCase):
    """Test loading and applying lexica."""

    cell_grounder: ClassVar[Grounder]
    phenotype_grounder: ClassVar[Grounder]

    @classmethod
    def setUpClass(cls) -> None:
        """Set up the class with several grounders."""
        cls.cell_grounder = biolexica.load_grounder(CELL_TERMS)
        cls.phenotype_grounder = biolexica.load_grounder(PHENOTYPE_TERMS)

    def test_predefined_list(self) -> None:
        """Check the predefined list is right."""
        self.assertEqual(
            set(typing.get_args(PREDEFINED)), {d.name for d in LEXICA.iterdir() if d.is_dir()}
        )

    def test_ground_cells(self) -> None:
        """Test grounding cells."""
        res = self.cell_grounder.get_matches("hela")
        self.assertIsInstance(res, list)
        self.assertEqual(1, len(res))
        self.assertEqual("cellosaurus", res[0].prefix)
        self.assertEqual("0030", res[0].identifier)
