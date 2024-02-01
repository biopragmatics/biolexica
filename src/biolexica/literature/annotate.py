"""Tools for getting literature."""

from __future__ import annotations

import logging
import time
import typing as t
from collections import Counter
from typing import List, Optional, Union

import gilda
import gilda.ner
from curies import Reference
from more_itertools import batched
from pydantic import BaseModel
from tqdm.auto import tqdm

from biolexica.literature.retrieve import get_pubmed_dataframe
from biolexica.literature.search import query_pubmed

__all__ = [
    "AnnotatedArticle",
    "Annotation",
    "annotate_abstracts_from_search",
    "annotate_abstracts_from_pubmeds",
]


logger = logging.getLogger(__name__)


class Annotation(BaseModel):
    """Data about an annotation."""

    text: str
    reference: Reference
    score: float
    start: int
    end: int
    name: str

    @property
    def substr(self) -> str:
        """Get the substring that was matched."""
        return self.text[self.start : self.end]


class AnnotatedArticle(BaseModel):
    """A data model representing an annotated article from PubMed."""

    pubmed: str
    title: str
    abstract: str
    annotations: List[Annotation]

    def count_references(self) -> t.Counter[t.Tuple[Reference, str]]:
        """Count the references annotated in this article."""
        return Counter((annotation.reference, annotation.name) for annotation in self.annotations)


def annotate_abstracts_from_search(
    pubmed_query: str,
    grounder: gilda.Grounder,
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
        pubmed_ids, grounder=grounder, use_indra_db=use_indra_db, show_progress=show_progress
    )


def annotate_abstracts_from_pubmeds(
    pubmed_ids: t.Collection[Union[str, int]],
    grounder: gilda.Grounder,
    *,
    use_indra_db: bool = True,
    batch_size: int = 20_000,
    show_progress: bool = True,
) -> List[AnnotatedArticle]:
    """Annotate the given articles using the given Gilda grounder."""
    n_pmids = len(pubmed_ids)

    rv: List[AnnotatedArticle] = []

    outer_it = tqdm(
        batched(pubmed_ids, batch_size),
        total=1 + n_pmids // batch_size,
        unit="batch",
        desc="Annotating articles",
        disable=not show_progress,
    )
    for i, pubmed_batch in enumerate(outer_it, start=1):
        t = time.time()
        pubmed_batch = list(pubmed_batch)
        articles_df = get_pubmed_dataframe(pubmed_batch, use_indra_db=use_indra_db).reset_index()
        n_retrieved = len(articles_df.index)
        tqdm.write(
            f"[batch {i}] Got {n_retrieved:,} articles "
            f"({n_retrieved/len(pubmed_batch):.1%}) in {time.time() - t:.2f} seconds"
        )
        for pmid, title, abstract in tqdm(
            articles_df.values,
            desc=f"Annotating batch {i}",
            unit_scale=True,
            unit="article",
            total=n_retrieved,
            leave=False,
            disable=not show_progress,
        ):
            rv.append(
                AnnotatedArticle(
                    pubmed=pmid,
                    title=title,
                    abstract=abstract,
                    annotations=annotate(abstract, grounder=grounder),
                )
            )

    return rv


def annotate(text: str, grounder: gilda.Grounder) -> List[Annotation]:
    """Annotate text using the given Gilda grounder."""
    return [
        Annotation(
            text=text,
            reference=Reference(prefix=match.term.db, identifier=match.term.id),
            name=match.term.entry_name,
            score=match.score,
            start=start,
            end=end,
        )
        for text, match, start, end in gilda.ner.annotate(text, grounder=grounder)
    ]
