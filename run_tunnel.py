"""
Deprecated runner: Migrated to Render & standard local server runner.
Please use:
    python run_server.py
"""

import sys
from run_server import *

if __name__ == "__main__":
    print("[Note] ngrok was replaced with Render. Starting standard server on http://localhost:8000...")
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
