"""Test loading and applying lexica."""

import unittest
from pathlib import Path

import biolexica
from biolexica.api import PREDEFINED
from biolexica.literature import annotate_abstracts_from_search

HERE = Path(__file__).parent.resolve()
ROOT = HERE.parent
LEXICA = ROOT.joinpath("lexica")
CELL_TERMS = LEXICA.joinpath("cell", "terms.tsv.gz")
ANATOMY_TERMS = LEXICA.joinpath("anatomy", "terms.tsv.gz")
PHENOTYPE_TERMS = LEXICA.joinpath("phenotype", "terms.tsv.gz")


class TestLexica(unittest.TestCase):
    """Test loading and applying lexica."""

    @classmethod
    def setUpClass(cls):
        """Set up the class with several grounders."""
        cls.cell_grounder = biolexica.load_grounder(CELL_TERMS)
        # cls.anatomy_grounder = biolexica.load_grounder(ANATOMY_TERMS)
        cls.phenotype_grounder = biolexica.load_grounder(PHENOTYPE_TERMS)

    def test_predefined_list(self):
        """Check the predefined list is right."""
        self.assertEqual(set(PREDEFINED), {d.name for d in LEXICA.iterdir() if d.is_dir()})

    def test_ground_cells(self):
        """Test grounding cells."""
        res = self.cell_grounder.ground("hela")
        self.assertIsInstance(res, list)
        self.assertEqual(1, len(res))
        self.assertEqual("cellosaurus", res[0].term.db)
        self.assertEqual("0030", res[0].term.id)

    def test_search_alz(self):
        """Test searching and annotating Alzheimer's docs gets a desired annotation."""
        results = annotate_abstracts_from_search(
            "alzheimers", grounder=self.phenotype_grounder, limit=20
        )
        self.assertTrue(
            any(
                ref.curie == "doid:10652"  # this is the DOID term for Alzheimer's disease
                for result in results
                for ref, _name in result.count_references()
            )
        )
        self.assertFalse(
            any(
                ref.curie == "doid:4"  # this is the DOID term for disease, should be filtered out
                for result in results
                for ref, _name in result.count_references()
            )
        )
