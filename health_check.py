"""Health check endpoints module.

This module provides health and readiness check endpoints for container orchestration.
"""

import logging
from typing import Dict, Any

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import get_db
from settings import settings
from tasks.redis import redis_client

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, Any]:
    """Basic liveness check endpoint.
    
    Returns 200 if the application is running.
    This endpoint is used by container orchestrators to verify the application is alive.
    
    Returns:
        Dict[str, Any]: Health status with version information
    """
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check(db: Session = Depends(get_db)) -> JSONResponse:
    """Readiness check endpoint.
    
    Verifies that the application can connect to all required dependencies:
    - Database (PostgreSQL)
    - Redis
    
    Returns 200 if all dependencies are reachable, 503 otherwise.
    This endpoint is used by container orchestrators to verify the application is ready to serve traffic.
    
    Args:
        db: Database session dependency
        
    Returns:
        JSONResponse: Readiness status with dependency health information
    """
    dependencies_status = {
        "database": "unknown",
        "redis": "unknown",
    }
    all_healthy = True
    
    # Check database connectivity
    try:
        db.execute(text("SELECT 1"))
        dependencies_status["database"] = "healthy"
        logger.debug("Database health check passed")
    except Exception as e:
        dependencies_status["database"] = f"unhealthy: {str(e)}"
        all_healthy = False
        logger.error(f"Database health check failed: {e}")
    
    # Check Redis connectivity
    try:
        if redis_client is not None:
            redis_client.ping()
            dependencies_status["redis"] = "healthy"
            logger.debug("Redis health check passed")
        else:
            dependencies_status["redis"] = "unhealthy: client not initialized"
            all_healthy = False
            logger.warning("Redis client not initialized")
    except Exception as e:
        dependencies_status["redis"] = f"unhealthy: {str(e)}"
        all_healthy = False
        logger.error(f"Redis health check failed: {e}")
    
    if all_healthy:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "ready",
                "version": settings.APP_VERSION,
                "dependencies": dependencies_status,
            },
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not_ready",
                "version": settings.APP_VERSION,
                "dependencies": dependencies_status,
            },
        )
