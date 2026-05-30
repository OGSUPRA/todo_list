from fastapi import APIRouter

from app.api.v1.endpoints.admin import router as admin_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.tasks import router as tasks_router
from app.api.v1.endpoints.users import router as users_router

api_router = APIRouter()
api_router.include_router(health_router, prefix="/v1/health", tags=["health"])
api_router.include_router(auth_router, prefix="/v1/auth", tags=["auth"])
api_router.include_router(tasks_router, prefix="/v1/tasks", tags=["tasks"])
api_router.include_router(users_router, prefix="/v1/users", tags=["users"])
api_router.include_router(admin_router, prefix="/v1/admin", tags=["admin"])
