#!/usr/bin/env python3
"""
Standalone test server for Aid-al-Neo API
Run this script directly on the server to test the Python module without Docker
"""

import os
import sys
import logging
from pathlib import Path

# Add the backend directory to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_environment():
    """Set up environment variables for testing"""
    # Create necessary directories
    os.makedirs("./models/cache", exist_ok=True)
    os.makedirs("./logs", exist_ok=True)
    os.makedirs("./params", exist_ok=True)
    
    # Set environment variables
    os.environ.setdefault("ENV", "development")
    os.environ.setdefault("API_KEY", "test_api_key_123")
    os.environ.setdefault("ADMIN_TOKEN", "test_admin_token_456")
    os.environ.setdefault("MODEL_CACHE_DIR", "./models/cache")
    os.environ.setdefault("LOG_DIR", "./logs")
    os.environ.setdefault("PARAMS_DIR", "./params")
    os.environ.setdefault("ALLOWED_ORIGINS", "*")
    
    # Optional: Set HF token if you have one
    # os.environ.setdefault("HF_TOKEN", "your_hf_token_here")
    
    logger.info("Environment setup completed")

def run_server():
    """Run the FastAPI server"""
    try:
        import uvicorn
        from backend.main import app
        
        logger.info("Starting Aid-al-Neo API server...")
        logger.info("Server will be available at: http://localhost:8000")
        logger.info("API documentation at: http://localhost:8000/docs")
        logger.info("Health check at: http://localhost:8000/api/v1/health")
        
        # Run the server
        uvicorn.run(
            app,
            host="0.0.0.0",  # Allow external connections
            port=8000,
            reload=True,  # Auto-reload on code changes
            log_level="info"
        )
        
    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        logger.error("Please install requirements: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    logger.info("Setting up Aid-al-Neo test server...")
    setup_environment()
    run_server() 