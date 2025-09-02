"""
WorkBox API Server Launcher
==========================

This script runs the FastAPI server for the WorkBox application.
"""

import uvicorn
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    print("Starting WorkBox API Server...")
    uvicorn.run("WorkBox.api.server:app", host="0.0.0.0", port=8000, reload=True)
