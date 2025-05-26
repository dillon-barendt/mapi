import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


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
