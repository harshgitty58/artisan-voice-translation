"""
Artisan AI Studio — Local UI Runner
Serves the beige/terracotta test portal on http://localhost:3000
"""

import http.server
import socketserver
import webbrowser
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PORT = 3000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        # Enable CORS for local testing
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

def main():
    os.chdir(DIRECTORY)
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        url = f"http://localhost:{PORT}"
        print("=" * 60)
        print("  🎨 ARTISAN AI TEST PORTAL (SIH 2026)")
        print("=" * 60)
        print(f"  Serving at: {url}")
        print("  Target Backend: http://localhost:8000 or Render Live")
        print("  Press Ctrl+C to stop the server.")
        print("=" * 60)
        
        try:
            webbrowser.open(url)
        except Exception:
            pass
            
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down Artisan AI UI server...")

if __name__ == "__main__":
    main()
