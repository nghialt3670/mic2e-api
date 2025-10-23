"""
FastAPI application for MIC2E (Multimodal Interactive Image Editing)
"""

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.inference.manager.global_manager import (
    get_predictor_manager,
    shutdown_predictor_manager,
)
from routers.chat_router import router as chat_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown."""
    # Startup
    print("Starting MIC2E API...")
    predictor_manager = get_predictor_manager()
    await predictor_manager.initialize()
    print("Predictor manager initialized successfully")

    yield

    # Shutdown
    print("Shutting down MIC2E API...")
    await shutdown_predictor_manager()
    print("Shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="MIC2E API",
    description="Multimodal Interactive Image Editing API",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router, prefix="/api/v1", tags=["chat"])


@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {"message": "MIC2E API is running", "status": "healthy"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        predictor_manager = get_predictor_manager()
        return {
            "status": "healthy",
            "predictor_manager_initialized": predictor_manager.is_initialized(),
        }
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"status": "unhealthy", "error": str(e)}
        )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
