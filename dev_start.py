#!/usr/bin/env python3
"""
Development startup script for ContentSyndicate
Sets up database and starts the development server
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_requirements():
    """Check if required packages are installed"""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import pydantic
        logger.info("✓ Core dependencies found")
        return True
    except ImportError as e:
        logger.error(f"✗ Missing dependency: {e}")
        logger.info("Please install requirements: pip install -r requirements.txt")
        return False

def setup_database():
    """Initialize database for development"""
    try:
        from app.migrations import init_database
        logger.info("Setting up database...")
        init_database()
        logger.info("✓ Database setup complete")
    except Exception as e:
        logger.error(f"✗ Database setup failed: {e}")
        return False
    return True

def start_server():
    """Start the development server"""
    try:
        logger.info("Starting ContentSyndicate development server...")
        logger.info("Server will be available at: http://localhost:8000")
        logger.info("API Documentation: http://localhost:8000/docs")
        logger.info("Press Ctrl+C to stop the server")
        
        # Start uvicorn server
        os.system("python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        
    except KeyboardInterrupt:
        logger.info("\nServer stopped by user")
    except Exception as e:
        logger.error(f"✗ Failed to start server: {e}")

def main():
    """Main development setup and startup"""
    logger.info("🚀 ContentSyndicate Development Setup")
    logger.info("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        logger.error("✗ Python 3.8+ required")
        sys.exit(1)
    
    logger.info(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Check if in virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        logger.info("✓ Virtual environment detected")
    else:
        logger.warning("⚠ Not in virtual environment - consider using one")
    
    # Check requirements
    if not check_requirements():
        logger.info("\nTo install requirements:")
        logger.info("pip install -r requirements.txt")
        sys.exit(1)
    
    # Setup environment file
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists():
        if env_example.exists():
            logger.info("Creating .env file from template...")
            env_example.rename(env_file)
            logger.info("✓ Created .env file - please update with your API keys")
        else:
            logger.warning("⚠ No .env file found - using defaults")
    
    # Setup database
    if not setup_database():
        sys.exit(1)
    
    # Start server
    start_server()

if __name__ == "__main__":
    main()
