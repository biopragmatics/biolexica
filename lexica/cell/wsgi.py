"""Run the cell/cell line grounder API."""

from ssslm.web import run_app

if __name__ == "__main__":
    run_app("terms.ssslm.tsv.gz")
