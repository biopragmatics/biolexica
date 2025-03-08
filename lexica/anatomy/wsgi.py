"""Run the anatomy grounder API."""

from ssslm.web import run_app

if __name__ == "__main__":
    run_app("anatomy.ssslm.tsv.gz")
