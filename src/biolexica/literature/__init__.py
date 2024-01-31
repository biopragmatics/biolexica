"""Tools for working with literature."""

from .annotate import (
    AnnotatedArticle,
    Annotation,
    annotate_abstracts_from_pubmeds,
    annotate_abstracts_from_search,
)
from .retrieve import get_pubmed_dataframe
from .search import query_pubmed

__all__ = [
    "query_pubmed",
    "get_pubmed_dataframe",
    "AnnotatedArticle",
    "Annotation",
    "annotate_abstracts_from_pubmeds",
    "annotate_abstracts_from_search",
]
