"""Tools for analyzing the results of annotation."""

import typing as t
from collections import Counter
from itertools import combinations
from typing import List

import ssslm
from curies import NamableReference

from .annotate import AnnotatedArticle

__all__ = [
    "count_references",
    "count_cooccurrences",
    "analyze_pretokens",
]


def count_references(
    annotated_articles: List[AnnotatedArticle],
) -> t.Counter[NamableReference]:
    """Count the number of references in the annotated articles."""
    return Counter(
        reference
        for annotated_article in annotated_articles
        for reference in annotated_article.count_references()
    )


def count_cooccurrences(
    annotated_articles: List[AnnotatedArticle],
) -> t.Counter[frozenset[NamableReference]]:
    """Count the co-occurrences of entities in the annotated articles."""
    return Counter(
        frozenset(pair)
        for annotated_article in annotated_articles
        for pair in combinations(annotated_article.count_references(), 2)
    )


def analyze_pretokens(
    text: str, *, grounder: ssslm.GrounderHint, min_length: int = 1, max_length: int = 4
) -> t.Counter[str]:
    """Take a histogram over tokens appearing before matches to identify more detailed terms for curation.

    :param text: The text to analyze
    :param grounder: The grounder
    :param min_length: The minimum number of pre-tokens to keep a histogram
    :param max_length: The maximum number of pre-tokens to keep a histogram

    :returns: A counter of pre-tokens in the given length range

    Here's an example where we look at recent literature about dementia and try and identify if
    there are:

    1. synonyms that could be curated in one of the upstream first-party lexical resources or
       third-party lexical resources like Biosynonyms
    2. terms that can be added to upstream ontologies, databases, etc.

    .. code-block:: python

        from collections import Counter
        from tabulate import tabulate
        import biolexica
        from biolexica.literature import get_article_dataframe_from_search
        from biolexica.literature.analyze import analyze_pretokens

        grounder = biolexica.load_grounder("phenotype")
        df = get_article_dataframe_from_search("dementia")
        counter = Counter()
        for abstract in df["abstract"]:
            counter.update(analyze_pretokens(abstract, grounder=grounder))

        table = tabulate(counter.most_common(), headers=["phrase", "count"], tablefmt="github")
        print(table)

    """
    from gilda.ner import stop_words

    grounder = ssslm.make_grounder(grounder)
    text = text.replace("\n", " ").replace("  ", " ")
    rv: t.Counter[str] = Counter()
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
