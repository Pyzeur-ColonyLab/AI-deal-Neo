#!/usr/bin/env python3
"""
Public server runner for Aid-al-Neo API
This version binds to all interfaces for public access
WARNING: Only use with proper security measures!
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
    """Set up environment variables for public access"""
    # Create necessary directories
    os.makedirs("./models/cache", exist_ok=True)
    os.makedirs("./logs", exist_ok=True)
    os.makedirs("./params", exist_ok=True)
    
    # Set environment variables for public access
    os.environ.setdefault("ENV", "production")
    os.environ.setdefault("API_KEY", "your_secure_api_key_here")  # CHANGE THIS!
    os.environ.setdefault("ADMIN_TOKEN", "your_secure_admin_token_here")  # CHANGE THIS!
    os.environ.setdefault("MODEL_CACHE_DIR", "./models/cache")
    os.environ.setdefault("LOG_DIR", "./logs")
    os.environ.setdefault("PARAMS_DIR", "./params")
    os.environ.setdefault("ALLOWED_ORIGINS", "https://cryptomaltese.com,https://www.cryptomaltese.com")
    
    logger.info("Environment setup completed for public access")

def run_server():
    """Run the FastAPI server on all interfaces"""
    try:
        import uvicorn
        from backend.main_improved import app  # Use improved version for security
        
        logger.info("Starting Aid-al-Neo API server for public access...")
        logger.info("⚠️  WARNING: Server will be accessible from the internet!")
        logger.info("Server will be available at: http://0.0.0.0:8000")
        logger.info("API documentation at: http://0.0.0.0:8000/docs")
        logger.info("Health check at: http://0.0.0.0:8000/health")
        
        # Run the server on all interfaces
        uvicorn.run(
            app,
            host="0.0.0.0",  # Bind to all interfaces
            port=8000,
            reload=False,  # Disable reload for production
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
    logger.info("Setting up Aid-al-Neo public server...")
    setup_environment()
    run_server() 