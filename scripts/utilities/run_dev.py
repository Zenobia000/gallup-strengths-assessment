#!/usr/bin/env python3
"""
Development server startup script - Gallup Strengths Assessment

Simple script to run the FastAPI development server.
Follows the "simple is better than complex" principle.
"""

import sys
import os
from pathlib import Path

# Add src/main/python to Python path
# Correctly identify the project root, which is two levels above this script.
project_root = Path(__file__).resolve().parent.parent.parent
python_path = project_root / "src" / "main" / "python"
sys.path.insert(0, str(python_path))


if __name__ == "__main__":
    import uvicorn
    from api.main import app

    print("Starting Gallup Strengths Assessment API")
    print(f"Project root: {project_root}")
    print(f"Python path: {python_path}")
    print("API docs: http://localhost:8004/api/v1/docs")
    print("Health check: http://localhost:8004/api/v1/health")

    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8004,
        reload=True,
        log_level="info"
    )