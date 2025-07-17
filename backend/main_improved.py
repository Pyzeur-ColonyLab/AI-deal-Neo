from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import router as api_router, hf_model_service
from backend.middleware.rate_limiter import rate_limit_middleware
from backend.middleware.timeout import timeout_middleware
from backend.utils.monitoring import api_monitor
import os
import logging
import time
import asyncio
import uuid

# Enhanced logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('./logs/api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("aidalneo")

# Detect environment and allowed origins
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")
ENV = os.getenv("ENV", "development")

logger.info(f"Starting Aid-al-Neo API in {ENV} mode.")
logger.info(f"Allowed CORS origins: {ALLOWED_ORIGINS}")

app = FastAPI(
    title="Aid-al-Neo API",
    version="1.0.0",
    description="Production-ready AI model API platform with enhanced security and monitoring."
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware for request tracking
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add unique request ID for tracking"""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    # Add request ID to response headers
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    """Monitor request performance and health"""
    start_time = time.time()
    success = True
    
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        success = False
        logger.error(f"Request failed: {str(e)}")
        raise
    finally:
        duration = time.time() - start_time
        api_monitor.record_request(duration, success)
        
        # Log request details
        logger.info(
            f"Request {request.state.request_id}: "
            f"{request.method} {request.url.path} - "
            f"{duration:.3f}s - {'SUCCESS' if success else 'FAILED'}"
        )

# Rate limiting middleware
@app.middleware("http")
async def rate_limit(request: Request, call_next):
    """Apply rate limiting"""
    return await rate_limit_middleware(request, call_next)

# Timeout middleware
@app.middleware("http")
async def timeout_handler(request: Request, call_next):
    """Apply request timeout"""
    return await timeout_middleware(request, call_next)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler with structured error responses"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.error(f"Global exception for request {request_id}: {str(exc)}")
    
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": f"HTTP_{exc.status_code}",
                    "message": exc.detail,
                    "request_id": request_id,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                }
            }
        )
    
    # Handle unexpected errors
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "request_id": request_id,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
        }
    )

app.include_router(api_router, prefix="/api/v1")

# Enhanced health check endpoint
@app.get("/health")
async def health_check():
    """Enhanced health check with system metrics"""
    try:
        # Check model status
        model_loaded = hf_model_service.is_model_loaded()
        
        # Get system health
        system_health = api_monitor.get_system_health()
        
        # Get API stats
        api_stats = api_monitor.get_stats()
        
        # Determine overall health
        memory_ok = system_health.get("memory", {}).get("percent_used", 0) < 90
        disk_ok = system_health.get("disk", {}).get("percent_used", 0) < 90
        model_ok = model_loaded
        
        overall_status = "healthy" if all([memory_ok, disk_ok, model_ok]) else "degraded"
        
        return {
            "status": overall_status,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "model": {
                "loaded": model_loaded,
                "name": "Pyzeur/Code-du-Travail-mistral-finetune" if model_loaded else None
            },
            "system": system_health,
            "api": api_stats
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
        )

@app.on_event("startup")
async def startup_event():
    """Enhanced startup with better error handling and monitoring"""
    logger.info("Starting model pre-loading...")
    try:
        # Use the same HF model service instance that will be used by routes
        base_model = "mistralai/Mistral-7B-Instruct-v0.3"
        finetuned_model = "Pyzeur/Code-du-Travail-mistral-finetune"
        
        logger.info(f"Loading model: {finetuned_model}")
        hf_model_service.load_model(base_model, finetuned_model)
        logger.info("Model loaded successfully and ready for inference!")
        
        # Log system health after startup
        system_health = api_monitor.get_system_health()
        logger.info(f"System health after startup: {system_health}")
        
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        # Don't raise the exception to allow the app to start
        # The chat endpoint will handle the case when model is not loaded

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Aid-al-Neo API...")
    try:
        # Unload model to free memory
        hf_model_service.unload_model()
        logger.info("Model unloaded successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}") 