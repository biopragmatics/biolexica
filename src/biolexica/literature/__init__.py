"""Tools for working with literature."""

from .annotate import (
    AnnotatedArticle,
    Annotation,
    annotate_abstracts_from_pubmeds,
    annotate_abstracts_from_search,
)
from .retrieve import get_article_dataframe_from_pubmeds
from .search import get_article_dataframe_from_search, query_pubmed

__all__ = [
    "query_pubmed",
    "get_article_dataframe_from_pubmeds",
    "get_article_dataframe_from_search",
    "AnnotatedArticle",
    "Annotation",
    "annotate_abstracts_from_pubmeds",
    "annotate_abstracts_from_search",
]
