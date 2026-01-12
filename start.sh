#!/bin/bash
# Production startup script for VPS deployment

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt

# Run server with production settings
uvicorn src.server:app --host 0.0.0.0 --port 8000 --workers 4

