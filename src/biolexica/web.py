"""A FastAPI wrapper for Gilda."""

from typing import List

import fastapi
import gilda
from curies import Reference
from fastapi import FastAPI, Request
from pydantic import BaseModel

from biolexica.api import GrounderHint, load_grounder

__all__ = [
    "run_app",
    "get_app",
]

api_router = fastapi.APIRouter()


class Match(BaseModel):
    """Model a scored match from Gilda."""

    reference: Reference
    name: str
    score: float


def run_app(grounder: GrounderHint):
    """Costruct a FastAPI app from a Gilda grounder and run with :mod:`uvicorn`."""
    import uvicorn

    uvicorn.run(get_app(grounder))


def get_app(grounder: GrounderHint) -> FastAPI:
    """Construct a FastAPI app from a Gilda grounder."""
    app = FastAPI(title="Biolexica Grounder")
    app.state = load_grounder(grounder)
    app.include_router(api_router, prefix="/api")
    return app


def _get_grounder(request: Request) -> gilda.Grounder:
    return request.app.state


def _ground(request: Request, text: str) -> List[Match]:
    return [
        Match(
            reference=Reference(prefix=scored_match.term.db, identifier=scored_match.term.id),
            name=scored_match.term.entry_name,
            score=scored_match.score,
        )
        for scored_match in _get_grounder(request).ground(text)
    ]


@api_router.get("/summarize")
def summarize(request: Request):
    """Summarize the lexical index."""
    grounder = _get_grounder(request)
    return {"number_terms": len(grounder.entries)}


@api_router.get("/ground/{text}", response_model=List[Match])
def ground(
    request: Request, text: str = fastapi.Path(..., description="Text to be grounded.")  # noqa:B008
):
    """Ground text using Gilda."""
    return _ground(request, text)
