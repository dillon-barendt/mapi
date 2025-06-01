import time

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request

from .config import settings


class ResponseTimeMiddleware(BaseHTTPMiddleware):
    """
    Middleware component for measuring and attaching response time to the headers
    of HTTP responses. This is particularly useful for performance monitoring, debugging,
    and optimization of web applications.

    It measures the time taken to process each HTTP request and appends a custom header
    "X-Response-Time" to the HTTP response, indicating the total processing time in seconds.

    :ivar dispatch: Function responsible for handling the middleware logic.
    :type dispatch: Callable
    """

    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        response = await call_next(request)
        total_time = time.perf_counter() - start_time
        response.headers["X-Response-Time"] = f"{total_time:.4f}s"
        return response


def register_middlewares(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=["*"],
        allow_headers=["*"],
    )
