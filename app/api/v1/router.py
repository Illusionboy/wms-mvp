from fastapi import APIRouter

from app.api.v1.endpoints import admin, customers, health, inventory, telegram, warehouses

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(customers.router, prefix="/customers", tags=["customers"])
api_router.include_router(warehouses.router, prefix="/warehouses", tags=["warehouses"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["inventory"])
api_router.include_router(telegram.router, prefix="/telegram", tags=["telegram"])
