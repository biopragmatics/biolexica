# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "biolexica",
#     "bioliterature",
#     "ssslm[gilda-slim]",
#     "tabulate",
#     "pubmed-downloader",
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
from bioliterature.annotate import AnnotatedArticle
from tabulate import tabulate
from pubmed_downloader import iterate_process_articles

from biolexica import load_grounder


def _main() -> None:
    grounder = load_grounder("phenotype")

    annotated_articles = []
    for article, _ in zip(iterate_process_articles(), range(100000)):
        abstract = article.get_abstract()
        annotated_article = AnnotatedArticle(
            pubmed=str(article.pubmed),
            title=article.title,
            abstract=abstract,
            annotations=grounder.annotate(abstract),
        )
        annotated_articles.append(annotated_article)

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
