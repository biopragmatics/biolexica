"""Tools for analyzing the results of annotation."""

import typing as t
from collections import Counter
from itertools import combinations
from typing import List

from curies import Reference

from .annotate import AnnotatedArticle
from ..api import GrounderHint, load_grounder


__all__ = [
    "count_references",
    "count_cooccurrences",
    "analyze_pretokens",
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


def analyze_pretokens(
    text: str, *, grounder: GrounderHint, min_length: int = 1, max_length: int = 4
) -> t.Counter[str]:
    """Take a histogram over tokens appearing before matches to identify more detailed terms for curation."""
    from gilda.ner import stop_words

    grounder = load_grounder(grounder)
    text = text.replace("\n", " ").replace("  ", " ")
    rv = Counter()
    for annotation in grounder.annotate(text):
        parts = text[: annotation.start].split()
        for i in range(min_length, max_length + 1):
            reduced_parts = parts[-i:]
            if len(reduced_parts) < min_length:
                continue
            if reduced_parts[0].lower() in stop_words:
                # doesn't make sense for a named entity to start
                # with one of these words, like "of"
                continue
            if reduced_parts[0].isnumeric():
                continue
            if any(part.strip().endswith(".") for part in reduced_parts):
                # If any of the parts ends with a dot, it means that this
                # set of pre-words goes into the previous sentence, so skip
                continue
            pre = " ".join(reduced_parts)
            rv[pre] += 1
    return rv
