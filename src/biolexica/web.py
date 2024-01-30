"""A FastAPI wrapper for Gilda."""

from typing import Union

import fastapi
import gilda
from pydantic import BaseModel

from fastapi import FastAPI, Request
from curies import Reference
import pathlib

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


def run_app(grounder: Union[gilda.Grounder, str, pathlib.Path]):
    """Costruct a FastAPI app from a Gilda grounder and run with :mod:`uvicorn`."""
    import uvicorn

    if isinstance(grounder, (str, pathlib.Path)):
        grounder = gilda.Grounder(grounder)

    uvicorn.run(get_app(grounder))


def get_app(grounder: gilda.Grounder) -> FastAPI:
    """Construct a FastAPI app from a Gilda grounder."""
    app = FastAPI(title="Biolexica Grounder")
    app.state = grounder
    app.include_router(api_router, prefix="/api")
    return app


def _get_grounder(request: Request) -> gilda.Grounder:
    return request.app.state


def _ground(request: Request, text: str) -> list[Match]:
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


@api_router.get("/ground/{text}", response_model=list[Match])
def ground(request: Request, text: str = fastapi.Path(..., description="Text to be grounded.")):
    """Ground text using Gilda."""
    return _ground(request, text)
