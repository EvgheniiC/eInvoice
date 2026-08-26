"""API route modules."""

from fastapi import APIRouter

from app.api.routes import admin, auth, export, health, invoices, org, plan_requests, product

api_router: APIRouter = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(product.router, tags=["product"])
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(org.router, tags=["organization"])
api_router.include_router(plan_requests.router, tags=["plan requests"])
api_router.include_router(admin.router, tags=["admin"])
api_router.include_router(invoices.router, prefix="/invoices", tags=["invoices"])
api_router.include_router(export.router, prefix="/invoices", tags=["export"])
