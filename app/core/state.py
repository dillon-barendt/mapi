from contextlib import asynccontextmanager
from fastapi.applications import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for the FastAPI application.
    Set up application state, such as precomputing the OpenAPI schema
    and initializing other global components.
    """
    # Perform startup tasks here
    app.state.openapi_schema = None  # Initialize the schema cache
    try:
        yield  # Let the app run
    finally:
        # Perform shutdown tasks here
        pass
