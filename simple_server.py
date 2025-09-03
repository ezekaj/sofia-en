#!/usr/bin/env python3
"""
Simple health check server for Sofia Agent
"""
import os
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                "status": "healthy",
                "service": "sofia-agent",
                "timestamp": datetime.now().isoformat()
            }
            
            self.wfile.write(json.dumps(response).encode())
        
        elif self.path == '/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            response = {
                "service": "Sofia AI Agent",
                "status": "running",
                "environment": {
                    "livekit_url": os.getenv("LIVEKIT_URL", "not_set"),
                    "google_api_key": "configured" if os.getenv("GOOGLE_API_KEY") else "missing",
                    "calendar_url": os.getenv("CALENDAR_URL", "not_set"),
                }
            }
            
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        print(f"[{datetime.now()}] {format % args}")

def start_health_server():
    """Start the health check server"""
    port = int(os.getenv("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    print(f"Health server starting on port {port}")
    server.serve_forever()

if __name__ == "__main__":
    print("Starting Sofia Agent Health Server...")
    
    # Start health server in background
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    
    print("Health server started, keeping service alive...")
    
    # Keep the process alive
    try:
        while True:
            time.sleep(30)
            print(f"[{datetime.now()}] Sofia Agent service running...")
    except KeyboardInterrupt:
        print("Service stopped")