"""ASGI State Management for the startup, lifespan, and shutdown of the FastAPI application.

ASGI Specification: https://asgi.readthedocs.io/en/latest/specs/main.html
ASGI: Lifespan Protocol: https://asgi.readthedocs.io/en/latest/specs/lifespan.html
"""

from contextlib import asynccontextmanager
from fastapi.applications import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the lifespan of the FastAPI application. This asynchronous
    context manager handles necessary setup at the startup and cleanup
    at the shutdown of the application, ensuring proper management of
    application state such as the OpenAPI schema cache and any other
    resources required for the application's lifecycle.

    Startup tasks can be performed before entering the context scope,
    while shutdown tasks are executed upon exiting. It facilitates a
    clean and efficient lifecycle management for the app.

    :param app: The FastAPI application instance whose lifespan is being
        managed.
    :type app: FastAPI
    :return: An asynchronous generator managing the application lifespan.
    """
    # Perform startup tasks here
    app.state.openapi_schema = None  # Initialize the schema cache
    try:
        yield  # Let the app run
    finally:
        # Perform shutdown tasks here
        pass
