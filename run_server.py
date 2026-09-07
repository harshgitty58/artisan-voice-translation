"""
Local server runner for Artisan AI Business Copilot.
Usage:
    python run_server.py
"""

import os
import uvicorn
from dotenv import load_dotenv

load_dotenv()

PORT = int(os.getenv("PORT", 8000))
HOST = os.getenv("HOST", "0.0.0.0")

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Starting Artisan Speech Translation Service")
    print(f"📖 Interactive Swagger Docs: http://localhost:{PORT}/docs")
    print(f"🏥 Health Check Endpoint:    http://localhost:{PORT}/api/v1/health")
    print("=" * 60)
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=True)
