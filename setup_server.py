#!/usr/bin/env python3
"""
Setup script for Aid-al-Neo server
Run this to install dependencies and prepare the environment
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        sys.exit(1)
    logger.info(f"Python version: {sys.version}")

def install_requirements():
    """Install required packages"""
    logger.info("Installing requirements...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        logger.info("Requirements installed successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install requirements: {e}")
        sys.exit(1)

def create_directories():
    """Create necessary directories"""
    directories = [
        "./models/cache",
        "./logs", 
        "./params"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Created directory: {directory}")

def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = [
        "fastapi",
        "uvicorn", 
        "transformers",
        "torch",
        "huggingface_hub",
        "requests"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Missing packages: {missing_packages}")
        logger.error("Please run: pip install -r requirements.txt")
        return False
    
    logger.info("All required packages are installed")
    return True

def main():
    """Main setup function"""
    logger.info("Setting up Aid-al-Neo server environment...")
    
    # Check Python version
    check_python_version()
    
    # Create directories
    create_directories()
    
    # Install requirements if not already installed
    if not check_dependencies():
        install_requirements()
        check_dependencies()
    
    logger.info("Setup completed successfully!")
    logger.info("\nNext steps:")
    logger.info("1. Run the server: python test_server.py")
    logger.info("2. In another terminal, test the API: python test_api.py")
    logger.info("3. Access the API at: http://localhost:8000")
    logger.info("4. View documentation at: http://localhost:8000/docs")

if __name__ == "__main__":
    main() 