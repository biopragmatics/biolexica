"""Tools for searching PubMed."""

from __future__ import annotations

import subprocess
from typing import Any, List, Literal, Optional

import pandas as pd

from .retrieve import get_article_dataframe_from_pubmeds

__all__ = [
    "get_article_dataframe_from_search",
    "query_pubmed",
]

Method = Literal["api", "esearch"]


def get_article_dataframe_from_search(
    search_term: str,
    *,
    method: Optional[Method] = None,
    use_indra_db: bool = True,
    db=None,
    batch_size: Optional[int] = None,
    show_progress: bool = True,
    limit: Optional[int] = None,
    **kwargs: Any,
) -> pd.DataFrame:
    """Query PubMed for article identifiers based on a given search and get a dataframe."""
    pubmed_ids = query_pubmed(search_term, method=method, **kwargs)
    if limit:
        pubmed_ids = pubmed_ids[:limit]
    return get_article_dataframe_from_pubmeds(
        pubmed_ids,
        use_indra_db=use_indra_db,
        db=db,
        batch_size=batch_size,
        show_progress=show_progress,
    )


def query_pubmed(
    search_term: str,
    *,
    method: Optional[Method] = None,
    **kwargs: Any,
) -> List[str]:
    """Query PubMed for article identifiers based on a given search."""
    if method == "esearch":
        return _get_pmids_with_esearch(search_term)
    elif method is None or method == "api":
        return _get_pmids_with_indra(search_term, **kwargs)
    raise ValueError(f"Unknown method: {method}")


def _get_pmids_with_indra(search_term: str, **kwargs: Any) -> List[str]:
    from indra.literature import pubmed_client

    return pubmed_client.get_ids(search_term, **kwargs)


def _get_pmids_with_esearch(search_term: str) -> List[str]:
    #  TODO replace with https://github.com/sorgerlab/indra/pull/1424/files
    injection = "PATH=/Users/cthoyt/edirect:${PATH}"
    cmd = f'{injection} esearch -db pubmed -query "{search_term}" | {injection} efetch -format uid'
    res = subprocess.getoutput(cmd)
    if "esearch: command not found" in res:
        raise RuntimeError("esearch is not properly on the filepath")
    if "efetch: command not found" in res:
        raise RuntimeError("efetch is not properly on the filepath")
    # Output is divided by new lines
    elements = res.split("\n")
    # If there are more than 10k IDs, the CLI outputs a . for each
    # iteration, these have to be filtered out
    pmids = [e for e in elements if "." not in e]
    return pmids
