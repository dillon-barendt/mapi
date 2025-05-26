from fastapi import FastAPI
from starlette.requests import Request

from app.api.v1.router import api_v1_router
from .core.config import settings
from .core.middleware import ResponseTimeMiddleware
from .core.state import lifespan
from .utils.openapi_custom import custom_openapi

app = FastAPI(**settings.fastapi_kwargs, lifespan=lifespan)  # type: ignore
app.add_middleware(ResponseTimeMiddleware) # type: ignore
app.include_router(api_v1_router)
app.openapi = custom_openapi

@app.get("/")
async def root():
    return {"message": "Hello World"}



@app.get("/cache-status")
async def cache_status(request: Request):
    is_cached = request.app.state.openapi_schema is not None
    return {"schema_cached": is_cached}

