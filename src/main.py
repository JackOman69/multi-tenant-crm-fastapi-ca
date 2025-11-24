from fastapi import APIRouter, FastAPI

from src.api.middleware.error_handler import add_exception_handlers
from src.api.v1.endpoints import (
    activities,
    analytics,
    auth,
    contacts,
    deals,
    organizations,
    tasks,
)
from src.core.config import settings

app = FastAPI(
    title="CRM API",
    version="0.1.0",
    docs_url=f"{settings.api_v1_prefix}/docs",
    redoc_url=f"{settings.api_v1_prefix}/redoc",
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
)

add_exception_handlers(app)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(organizations.router)
api_router.include_router(contacts.router)
api_router.include_router(deals.router)
api_router.include_router(tasks.router)
api_router.include_router(activities.router)
api_router.include_router(analytics.router)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
