#!/bin/bash
cd /Users/nikhil/Desktop/Niksmind/niksmind/backend
export PATH="/Users/nikhil/Desktop/Niksmind/niksmind/backend/venv/bin:$PATH"
exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
