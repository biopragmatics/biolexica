"""Run the cell/cell line grounder API."""

from biolexica.web import run_app

if __name__ == "__main__":
    run_app("terms.tsv.gz")
