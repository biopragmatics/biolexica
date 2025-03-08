# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "biolexica",
#     "bioliterature",
#     "indra",
#     "ssslm[gilda-slim]",
#     "tabulate",
# ]
#
# [tool.uv.sources]
# semra = { path = "../../semra", editable = true  }
# biolexica = { path = "..", editable = true  }
# pyobo = { path = "../../pyobo", editable = true }
# ssslm = { path = "../../ssslm", editable = true }
# bioontologies = { path = "../../bioontologies", editable = true }
#
# ///
"""Run search, retrival, annotation, and analysis with recent diabetes literature."""

import click
from bioliterature.analyze import count_cooccurrences, count_references
from bioliterature.annotate import annotate_abstracts_from_search
from tabulate import tabulate

from biolexica import load_grounder


def _main() -> None:
    query = "diabetes"
    grounder = load_grounder("phenotype")
    annotated_articles = annotate_abstracts_from_search(query, grounder=grounder, limit=300)
    reference_counter = count_references(annotated_articles)
    co_occurrence_counter = count_cooccurrences(annotated_articles)

    click.echo("\nOccurrences")
    click.echo(
        tabulate(
            [(r.curie, r.name, count) for r, count in reference_counter.most_common(10)],
            headers=["Reference", "Name", "Count"],
            tablefmt="github",
        )
    )

    click.echo("\nCo-occurrences")
    click.echo(
        tabulate(
            [
                (left.curie, left.name, right.curie, right.name, count)
                for (
                    left,
                    right,
                ), count in co_occurrence_counter.most_common(10)
            ],
            headers=[
                "Left Reference",
                "Left Name",
                "Right Reference",
                "Right Name",
                "Count",
            ],
            tablefmt="github",
        )
    )


if __name__ == "__main__":
    _main()
