"""Demonstrate running search, retrival, annotation, and analysis with recent diabetes literature."""

import click
from tabulate import tabulate

from biolexica import load_grounder
from biolexica.literature import annotate_abstracts_from_search
from biolexica.literature.analyze import count_cooccurrences, count_references


def _main():
    query = "diabetes"
    grounder = load_grounder("phenotype")
    annotated_articles = annotate_abstracts_from_search(query, grounder=grounder, limit=300)
    reference_counter = count_references(annotated_articles)
    co_occurrence_counter = count_cooccurrences(annotated_articles)

    click.echo("\nOccurrences")
    click.echo(
        tabulate(
            [(r.curie, name, count) for (r, name), count in reference_counter.most_common(10)],
            headers=["Reference", "Name", "Count"],
            tablefmt="github",
        )
    )

    click.echo("\nCo-occurrences")
    click.echo(
        tabulate(
            [
                (l_r.curie, l_n, r_r.curie, r_n, count)
                for ((l_r, l_n), (r_r, r_n)), count in co_occurrence_counter.most_common(10)
            ],
            headers=["Left Reference", "Left Name", "Right Reference", "Right Name", "Count"],
            tablefmt="github",
        )
    )


if __name__ == "__main__":
    _main()
