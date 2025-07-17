from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import router as api_router
from backend.services.hf_model_service import HFModelService
import os
import logging
import asyncio

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

@app.on_event("startup")
async def startup_event():
    """Pre-load the model when the application starts"""
    logger.info("Starting model pre-loading...")
    try:
        # Initialize the HF model service
        hf_service = HFModelService()
        
        # Load the Pyzeur/Code-du-Travail-mistral-finetune model
        # This model should be the finetuned version
        base_model = "mistralai/Mistral-7B-Instruct-v0.2"
        finetuned_model = "Pyzeur/Code-du-Travail-mistral-finetune"
        
        logger.info(f"Loading model: {finetuned_model}")
        hf_service.load_model(base_model, finetuned_model)
        logger.info("Model loaded successfully and ready for inference!")
        
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        # Don't raise the exception to allow the app to start
        # The chat endpoint will handle the case when model is not loaded 