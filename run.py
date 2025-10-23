#!/usr/bin/env python3
"""
Startup script for MIC2E API
"""

import os
import sys
from pathlib import Path

import uvicorn

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))


def main():
    """Main function to start the FastAPI server."""

    # Set default environment variables if not set
    os.environ.setdefault("OPENAI_API_KEY", "")
    os.environ.setdefault("ANTHROPIC_API_KEY", "")

    # Configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    log_level = os.getenv("LOG_LEVEL", "info")

    print(f"Starting MIC2E API server...")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Reload: {reload}")
    print(f"Log Level: {log_level}")

    # Start the server
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level,
        access_log=True,
    )


if __name__ == "__main__":
    main()
