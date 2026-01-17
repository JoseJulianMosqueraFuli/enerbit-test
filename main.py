"""Main application module.

This module initializes the FastAPI application and configures middleware.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
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
from security_headers import SecurityHeadersMiddleware

# Setup logging
setup_logging(log_level="INFO")

# Setup rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

app = FastAPI(
    title="Service Order Management System",
    description="This API provides endpoints for managing customers, service orders and data analysis..",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Register error handlers
app.add_exception_handler(DatabaseError, database_error_handler)
app.add_exception_handler(SQLAlchemyDatabaseError, sqlalchemy_database_error_handler)
app.add_exception_handler(OperationalError, sqlalchemy_operational_error_handler)
app.add_exception_handler(ValidationError, validation_error_handler)
app.add_exception_handler(NotFoundError, not_found_error_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# TODO: Replace with environment-specific origins in production
# For production, use: origins = ["https://yourdomain.com"]
origins = ["*"]

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

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
