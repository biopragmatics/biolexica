"""Tools for analyzing the results of annotation."""

from collections import Counter
from operator import attrgetter
from typing import List
import typing as t

from itertools import combinations
from .annotate import AnnotatedArticle
from curies import Reference

__all__ = [
    "count_references",
    "count_cooccurrences",
]


def count_references(
    annotated_articles: List[AnnotatedArticle],
) -> t.Counter[t.Tuple[Reference, str]]:
    """Count the number of references in the annotated articles."""
    return Counter(
        reference_name
        for annotated_article in annotated_articles
        for reference_name in annotated_article.count_references()
    )


def count_cooccurrences(
    annotated_articles: List[AnnotatedArticle],
) -> t.Counter[t.Tuple[t.Tuple[Reference, str], t.Tuple[Reference, str]]]:
    """Count the co-occurrences of entities in the annotated articles."""
    return Counter(
        tuple(sorted(pair, key=lambda p: p[0].curie))  # type:ignore
        for annotated_article in annotated_articles
        for pair in combinations(annotated_article.count_references(), 2)
    )
