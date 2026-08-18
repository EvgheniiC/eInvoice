"""API route modules."""

from fastapi import APIRouter

from app.api.routes import export, health, invoices, product

api_router: APIRouter = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(product.router, tags=["product"])
api_router.include_router(invoices.router, prefix="/invoices", tags=["invoices"])
api_router.include_router(export.router, prefix="/invoices", tags=["export"])
