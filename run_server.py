#!/usr/bin/env python3
"""
Robust server runner for Aid-al-Neo API
This version handles imports more carefully and provides better error handling
"""

import os
import sys
import logging
from pathlib import Path

# Set up logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_environment():
    """Set up environment variables and paths"""
    try:
        # Get the current directory
        current_dir = Path(__file__).parent.absolute()
        backend_dir = current_dir / "backend"
        
        # Add backend to Python path
        if str(backend_dir) not in sys.path:
            sys.path.insert(0, str(backend_dir))
            logger.info(f"Added {backend_dir} to Python path")
        
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
        
        logger.info("Environment setup completed")
        logger.info(f"Current directory: {current_dir}")
        logger.info(f"Backend directory: {backend_dir}")
        logger.info(f"Python path: {sys.path[:3]}...")  # Show first 3 entries
        
    except Exception as e:
        logger.error(f"Failed to setup environment: {e}")
        sys.exit(1)

def test_imports():
    """Test if all required modules can be imported"""
    try:
        logger.info("Testing imports...")
        
        # Test basic imports
        import fastapi
        import uvicorn
        logger.info("✓ FastAPI and uvicorn imported successfully")
        
        # Test backend imports
        from backend import main
        logger.info("✓ Backend main module imported successfully")
        
        from backend.api import routes
        logger.info("✓ Backend routes imported successfully")
        
        from backend.services import hf_model_service
        logger.info("✓ HF model service imported successfully")
        
        logger.info("All imports successful!")
        return True
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.error("Please check that all dependencies are installed:")
        logger.error("pip install -r requirements.txt")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during import test: {e}")
        return False

def run_server():
    """Run the FastAPI server"""
    try:
        logger.info("Starting Aid-al-Neo API server...")
        
        # Import the app
        from backend.main import app
        
        logger.info("✓ FastAPI app imported successfully")
        logger.info("Server will be available at: http://localhost:8000")
        logger.info("API documentation at: http://localhost:8000/docs")
        logger.info("Health check at: http://localhost:8000/api/v1/health")
        
        # Import and run uvicorn
        import uvicorn
        
        # Run the server
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=False,  # Disable reload for stability
            log_level="info",
            access_log=True
        )
        
    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        logger.error("Please install requirements: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

def main():
    """Main function"""
    logger.info("=" * 60)
    logger.info("Aid-al-Neo API Server - Direct Python Execution")
    logger.info("=" * 60)
    
    # Setup environment
    setup_environment()
    
    # Test imports
    if not test_imports():
        logger.error("Import test failed. Exiting.")
        sys.exit(1)
    
    # Run server
    run_server()

if __name__ == "__main__":
    main() 