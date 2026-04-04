from fastapi import APIRouter

from app.api.routes import auth, health, households, inventory, overview, receipts, shopping_list
from app.core.config import get_settings

settings = get_settings()

api_router = APIRouter(prefix=settings.api_v1_prefix)
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(households.router)
api_router.include_router(inventory.router)
api_router.include_router(overview.router)
api_router.include_router(receipts.router)
api_router.include_router(shopping_list.router)
