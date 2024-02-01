"""Test loading and applying lexica."""

import unittest
from pathlib import Path

import biolexica
from biolexica.api import PREDEFINED
from biolexica.literature import annotate_abstracts_from_pubmeds, annotate_abstracts_from_search

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

    def test_exclude_doid_4(self):
        """Test that exclusion during construction of the phenotype index works properly."""
        pubmed_id = "38279949"
        results = annotate_abstracts_from_pubmeds(
            [pubmed_id], grounder=self.phenotype_grounder, show_progress=False
        )
        articles_with_doid_4 = {
            result.pubmed
            for result in results
            for ref, _name in result.count_references()
            if ref.curie == "doid:4"
        }
        self.assertEqual(
            set(),
            articles_with_doid_4,
            msg="No articles should contain the reference `doid:4` for the top-level disease annotation, "
            "since this should be filtered out during construction of the lexical index.",
        )

    def test_search_alz(self):
        """Test searching and annotating Alzheimer's docs gets a desired annotation."""
        results = annotate_abstracts_from_search(
            "alzheimers",
            grounder=self.phenotype_grounder,
            limit=20,
            show_progress=False,
        )
        self.assertTrue(
            any(
                ref.curie == "doid:10652"  # this is the DOID term for Alzheimer's disease
                for result in results
                for ref, _name in result.count_references()
            )
        )
