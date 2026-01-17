"""Main application module.

This module initializes the FastAPI application and configures middleware.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from routers import analytics_router, customer_router, work_order_router

app = FastAPI(
    title="Service Order Management System",
    description="This API provides endpoints for managing customers, service orders and data analysis..",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(customer_router.router)
app.include_router(work_order_router.router)
app.include_router(analytics_router.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
