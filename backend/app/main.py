"""
FastAPI Backend Application Entrypoint
======================================
Coordinates model lifecycle, MongoDB connectivity, CORS configuration,
and REST routing for the Indian E-Commerce Recommendation System.
"""

import os
import sys
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Ensure root workspace is available on Python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app.core.config import settings
from backend.app.db.mongodb import db_manager
from backend.app.services.catalog_service import catalog_service
from backend.app.services.recommendation_service import recommendation_service
from backend.app.api import api_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application Lifespan Event Handler:
    Loads heavy data & ML artifacts once into memory upon server startup,
    and cleanly disposes of database connections upon shutdown.
    """
    logger.info("Initializing FastAPI Backend Lifecycle...")
    
    # 1. Connect to MongoDB
    db_manager.connect()
    
    # 2. Load product catalog DataFrame
    catalog_service.load(settings.DATA_PROCESSED_PATH)
    
    # 3. Load Recommendation Engine (TF-IDF vectorizer + sparse feature matrix)
    recommendation_service.load(settings.ARTIFACTS_DIR, catalog_service.df)
    
    logger.info("FastAPI Backend startup complete. Ready to receive requests.")
    yield
    
    # Clean shutdown
    logger.info("Shutting down FastAPI Backend...")
    db_manager.disconnect()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Indian E-Commerce Recommendation API powered by TF-IDF & Cosine Similarity with MongoDB persistence.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all REST endpoints under /api
app.include_router(api_router)


@app.get("/", tags=["Root"])
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "docs": "/docs",
        "health": "/api/health",
        "categories": "/api/categories",
        "products": "/api/products"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
