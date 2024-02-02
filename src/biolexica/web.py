"""A FastAPI wrapper for Gilda."""

from typing import List

import fastapi
from fastapi import FastAPI, Request

from biolexica.api import Grounder, GrounderHint, Match, load_grounder

__all__ = [
    "run_app",
    "get_app",
]

api_router = fastapi.APIRouter()


def run_app(grounder: GrounderHint):
    """Construct a FastAPI app from a Gilda grounder and run with :mod:`uvicorn`."""
    import uvicorn

    uvicorn.run(get_app(grounder))


def get_app(grounder: GrounderHint) -> FastAPI:
    """Construct a FastAPI app from a Gilda grounder."""
    app = FastAPI(title="Biolexica Grounder")
    app.state = load_grounder(grounder)
    app.include_router(api_router, prefix="/api")
    return app


def _get_grounder(request: Request) -> Grounder:
    return request.app.state


def _ground(request: Request, text: str) -> List[Match]:
    return _get_grounder(request).get_matches(text)


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
