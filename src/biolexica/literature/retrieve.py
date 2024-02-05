"""Tools for retrieving text content."""

from __future__ import annotations

import logging
from typing import Dict, Iterable, List, Union

import pandas as pd
from tqdm.asyncio import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm

__all__ = [
    "get_pubmed_dataframe",
    "PUBMED_DATAFRAME_COLUMNS",
    "clean_df",
]

logger = logging.getLogger(__name__)


PUBMED_DATAFRAME_COLUMNS = ["pubmed", "title", "abstract"]


def get_pubmed_dataframe(
    pubmed_ids: Iterable[Union[str, int]], *, use_indra_db: bool = True, db=None
) -> pd.DataFrame:
    """Get a dataframe indexed by PubMed identifier (str) with title and abstract columns."""
    if use_indra_db:
        try:
            return _from_indra_db(pubmed_ids, db=db)
        except (ValueError, ImportError):
            logger.warning(
                "Could not to access INDRA DB, relying on PubMed API. "
                "Warning: this could be intractably slow depending on the query, and also is missing full text."
            )
    return _from_api(pubmed_ids)


def _clean_pubmeds(pubmeds: Iterable[Union[str, int]]) -> List[str]:
    return sorted(map(str, pubmeds), key=int)


def _from_api(pmids: Iterable[Union[str, int]]) -> pd.DataFrame:
    from indra.literature import pubmed_client

    with logging_redirect_tqdm():
        rows = [
            (
                pmid,
                pubmed_client.get_title(pmid),
                pubmed_client.get_abstract(pmid, prepend_title=False),
            )
            for pmid in tqdm(
                _clean_pubmeds(pmids),
                leave=False,
                unit_scale=True,
                unit="article",
                desc="Getting PubMed titles/abstracts",
            )
        ]
    df = pd.DataFrame(rows, columns=PUBMED_DATAFRAME_COLUMNS).set_index("pubmed")
    df = clean_df(df)
    return df


def _from_indra_db(pmids: Iterable[Union[str, int]], db=None) -> pd.DataFrame:
    """Get titles and abstracts from the INDRA database."""
    db = _ensure_db(db)
    pmids = _clean_pubmeds(pmids)
    df = pd.DataFrame(
        {
            "title": _get_text(pmids, text_type="title", db=db),
            "abstract": _get_text(pmids, text_type="abstract", db=db),
        }
    )
    df.index.name = "pubmed"
    df = clean_df(df)
    return df


def _get_text(pmids: List[str], text_type: str, db) -> Dict[str, str]:
    from indra_db.util.helpers import unpack as unpack_indra_db

    return {
        row.pmid: unpack_indra_db(row.content).replace("\t", " ").replace("\n", "\t")
        for row in (
            db.session.query(db.TextRef.pmid, db.TextContent.text_type, db.TextContent.content)
            .filter(db.TextRef.pmid_in(pmids))
            .join(db.TextContent)
            .filter(db.TextContent.text_type == text_type)
            .all()
        )
    }


def _ensure_db(db=None):
    from indra_db import get_db

    if db is None:
        db = get_db("primary")
    if db is None:
        raise ValueError("Could not connect to INDRA DB")
    return db


def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the literature dataframe by remove missing titles/abstracts and questionable whitespace."""
    df = df[df.title.notna()].copy()
    df["title"] = df["title"].map(lambda s: s.replace("\n", " ").replace("\t", " "))
    df = df[df.abstract.notna()]
    df["abstract"] = df["abstract"].map(lambda s: s.replace("\n", " ").replace("\t", " "))
    return df
