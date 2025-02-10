"""Tools for getting literature."""

from __future__ import annotations

import logging
import typing as t
from collections import Counter
from typing import List, Optional, Union

import ssslm
from curies import NamableReference
from pydantic import BaseModel
from tqdm.auto import tqdm

from .retrieve import _iter_dataframes_from_pubmeds
from .search import query_pubmed

__all__ = [
    "AnnotatedArticle",
    "annotate_abstracts_from_search",
    "annotate_abstracts_from_pubmeds",
]


logger = logging.getLogger(__name__)


class AnnotatedArticle(BaseModel):
    """A data model representing an annotated article from PubMed."""

    pubmed: str
    title: str
    abstract: str
    annotations: List[ssslm.Annotation]

    def count_references(self) -> t.Counter[NamableReference]:
        """Count the references annotated in this article."""
        return Counter(a.reference for a in self.annotations)


def annotate_abstracts_from_search(
    pubmed_query: str,
    grounder: ssslm.GrounderHint,
    *,
    use_indra_db: bool = True,
    limit: Optional[int] = None,
    show_progress: bool = True,
    **kwargs,
) -> List[AnnotatedArticle]:
    """Get articles based on the query and do NER annotation using the given Gilda grounder."""
    pubmed_ids = query_pubmed(pubmed_query, **kwargs)
    if limit is not None:
        pubmed_ids = pubmed_ids[:limit]
    return annotate_abstracts_from_pubmeds(
        pubmed_ids,
        grounder=grounder,
        use_indra_db=use_indra_db,
        show_progress=show_progress,
    )


def annotate_abstracts_from_pubmeds(
    pubmed_ids: t.Collection[Union[str, int]],
    grounder: ssslm.GrounderHint,
    *,
    use_indra_db: bool = True,
    batch_size: Optional[int] = None,
    show_progress: bool = True,
) -> List[AnnotatedArticle]:
    """Annotate the given articles using the given Gilda grounder."""
    grounder = ssslm.make_grounder(grounder)
    df_iterator = _iter_dataframes_from_pubmeds(
        pubmed_ids=pubmed_ids,
        batch_size=batch_size,
        use_indra_db=use_indra_db,
        show_progress=show_progress,
    )
    rv: List[AnnotatedArticle] = [
        AnnotatedArticle(
            pubmed=pubmed,
            title=title,
            abstract=abstract,
            annotations=grounder.annotate(abstract),
        )
        for i, df in enumerate(df_iterator, start=1)
        for pubmed, title, abstract in tqdm(
            df.itertuples(),
            desc=f"Annotating batch {i}",
            unit_scale=True,
            unit="article",
            total=len(df.index),
            leave=False,
            disable=not show_progress,
        )
    ]
    return rv
