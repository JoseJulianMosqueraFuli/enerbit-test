"""Main application module.

This module initializes the FastAPI application and configures middleware.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from sqlalchemy.exc import DatabaseError as SQLAlchemyDatabaseError
from sqlalchemy.exc import OperationalError

from database import Base, engine
from error_handlers import (
    DatabaseError,
    NotFoundError,
    database_error_handler,
    generic_exception_handler,
    not_found_error_handler,
    sqlalchemy_database_error_handler,
    sqlalchemy_operational_error_handler,
    validation_error_handler,
)
from logger import setup_logging
from middleware import LoggingMiddleware
from routers import analytics_router, customer_router, work_order_router

# Setup logging
setup_logging(log_level="INFO")

app = FastAPI(
    title="Service Order Management System",
    description="This API provides endpoints for managing customers, service orders and data analysis..",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Register error handlers
app.add_exception_handler(DatabaseError, database_error_handler)
app.add_exception_handler(SQLAlchemyDatabaseError, sqlalchemy_database_error_handler)
app.add_exception_handler(OperationalError, sqlalchemy_operational_error_handler)
app.add_exception_handler(ValidationError, validation_error_handler)
app.add_exception_handler(NotFoundError, not_found_error_handler)
app.add_exception_handler(Exception, generic_exception_handler)

origins = ["*"]

# Add logging middleware
app.add_middleware(LoggingMiddleware)

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
