"""
Local server runner for Artisan AI Business Copilot.
Usage:
    python run_server.py
"""

import os
import sys
import uvicorn
from dotenv import load_dotenv

# Fix Windows cp1252 console encoding
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

PORT = int(os.getenv("PORT", 8000))
HOST = os.getenv("HOST", "0.0.0.0")

if __name__ == "__main__":
    print("=" * 60)
    print("[START] Artisan Speech Translation Service")
    print(f"[DOCS]  Swagger UI: http://localhost:{PORT}/docs")
    print(f"[HEALTH] Health Check: http://localhost:{PORT}/api/v1/health")
    print("=" * 60)
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=True)
