"""ASGI lifespan state management."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi.applications import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.openapi_schema = None
    yield
