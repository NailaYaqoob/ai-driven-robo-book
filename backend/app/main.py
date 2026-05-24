"""FastAPI main application for Physical AI & Humanoid Robotics Textbook backend."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.database import init_db, close_db
from app.services.rag.vectorstore import vector_store
from app.api.dependencies import (
    correlation_id_middleware,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
)

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for FastAPI application.

    Handles startup and shutdown events.
    """
    # Startup
    logger.info("application_startup", version=settings.VERSION)

    # Initialize database — log failure but don't crash the app so /health stays reachable
    try:
        await init_db()
        logger.info("database_initialized")
    except Exception as e:
        logger.error("database_initialization_failed", error=str(e))

    # Create Qdrant collection if not exists
    try:
        await vector_store.create_collection_if_not_exists()
        logger.info("vector_store_initialized")
    except Exception as e:
        logger.error("vector_store_initialization_failed", error=str(e))

    yield

    # Shutdown
    logger.info("application_shutdown")
    await close_db()


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add correlation ID middleware
app.middleware("http")(correlation_id_middleware)

# Add exception handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns:
        dict: Health status of the application and dependent services
    """
    # Check database connection
    db_status = "healthy"
    try:
        # TODO: Add actual database health check
        pass
    except Exception:
        db_status = "unhealthy"

    # Check vector store
    vector_store_status = "healthy"
    try:
        info = await vector_store.get_collection_info()
        if info["status"] == "not_found":
            vector_store_status = "degraded"
    except Exception:
        vector_store_status = "unhealthy"

    # Determine overall status
    if db_status == "unhealthy" or vector_store_status == "unhealthy":
        overall_status = "unhealthy"
    elif db_status == "degraded" or vector_store_status == "degraded":
        overall_status = "degraded"
    else:
        overall_status = "healthy"

    return {
        "status": overall_status,
        "version": settings.VERSION,
        "services": {
            "database": db_status,
            "vector_store": vector_store_status,
        },
    }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Physical AI & Humanoid Robotics Textbook API",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health",
    }


# Import API routers
from app.api.routes import auth, personalization, rag

# Include routers
app.include_router(auth.router)
app.include_router(personalization.router)
app.include_router(rag.router)
