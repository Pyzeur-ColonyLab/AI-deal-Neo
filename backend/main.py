from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import router as api_router
import os
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("aidalneo")

# Detect environment and allowed origins
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
ENV = os.getenv("ENV", "development")

logger.info(f"Starting Aid-al-Neo API in {ENV} mode.")
logger.info(f"Allowed CORS origins: {ALLOWED_ORIGINS}")

app = FastAPI(
    title="Aid-al-Neo API",
    version="1.0.0",
    description="Production-ready AI model API platform."
)

# CORS (allow all origins for now, restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1") 