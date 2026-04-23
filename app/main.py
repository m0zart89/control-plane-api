import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from app.api.routes import router
from app.reconciler import reconciler_loop


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(reconciler_loop(interval_seconds=30))
    yield
    task.cancel()


app = FastAPI(
    title="Control Plane API",
    description="API-first infrastructure control plane — lifecycle management with reconciliation",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/healthz", include_in_schema=False)
async def health():
    return {"status": "ok"}


@app.get("/metrics", include_in_schema=False)
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
