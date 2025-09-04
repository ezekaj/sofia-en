#!/usr/bin/env python3
"""
Sofia Tunnel Bridge - Connects web interface to local Sofia agent via WebSocket
This allows your local Sofia agent to be accessible through a tunneled connection
"""

import asyncio
import websockets
import json
import logging
import subprocess
import threading
import queue
import time
from flask import Flask, request, jsonify
from flask_cors import CORS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SofiaTunnelBridge:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        self.sofia_process = None
        self.connected_clients = set()
        self.setup_routes()
        
    def setup_routes(self):
        @self.app.route('/health')
        def health():
            return jsonify({
                "status": "healthy",
                "service": "Sofia Tunnel Bridge",
                "sofia_agent": "connected" if self.sofia_process else "disconnected",
                "clients": len(self.connected_clients)
            })
            
        @self.app.route('/api/sofia/connect', methods=['POST'])
        def connect_sofia():
            """Start Sofia agent if not running"""
            if not self.sofia_process:
                self.start_sofia_agent()
            return jsonify({"success": True, "status": "Sofia agent starting..."})
            
        @self.app.route('/api/sofia/message', methods=['POST'])
        def send_message():
            """Send message to Sofia agent"""
            data = request.json
            message = data.get('message', '')
            
            if self.sofia_process:
                try:
                    # Send message to Sofia's stdin
                    self.sofia_process.stdin.write(message + '\n')
                    self.sofia_process.stdin.flush()
                    return jsonify({"success": True, "sent": message})
                except Exception as e:
                    return jsonify({"success": False, "error": str(e)})
            
            return jsonify({"success": False, "error": "Sofia agent not running"})
            
        @self.app.route('/')
        def index():
            return '''
            <h1>🚇 Sofia Tunnel Bridge</h1>
            <p>Local Sofia Agent Bridge - Ready for tunneling!</p>
            <p><strong>Status:</strong> ✅ Running</p>
            <p><strong>Sofia Agent:</strong> {'🟢 Connected' if self.sofia_process else '🔴 Disconnected'}</p>
            <p><a href="/health">Health Check</a></p>
            <h2>📋 Instructions:</h2>
            <ol>
                <li>Install ngrok: <code>winget install ngrok</code></li>
                <li>Run: <code>ngrok http 5000</code></li>
                <li>Copy the HTTPS URL and use it in your web interface</li>
                <li>Your Sofia agent will be accessible worldwide!</li>
            </ol>
            '''
    
    def start_sofia_agent(self):
        """Start the Sofia agent process"""
        try:
            logger.info("🤖 Starting Sofia agent...")
            self.sofia_process = subprocess.Popen(
                ['python', 'agent.py', 'dev'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            logger.info("✅ Sofia agent started successfully")
            
            # Start thread to read Sofia's output
            threading.Thread(target=self.read_sofia_output, daemon=True).start()
            
        except Exception as e:
            logger.error(f"❌ Failed to start Sofia agent: {e}")
            
    def read_sofia_output(self):
        """Read output from Sofia agent and broadcast to clients"""
        if not self.sofia_process:
            return
            
        for line in iter(self.sofia_process.stdout.readline, ''):
            if line.strip():
                logger.info(f"Sofia: {line.strip()}")
                # Broadcast to connected websocket clients
                self.broadcast_to_clients({
                    "type": "sofia_output",
                    "message": line.strip(),
                    "timestamp": time.time()
                })
                
    def broadcast_to_clients(self, message):
        """Broadcast message to all connected WebSocket clients"""
        if self.connected_clients:
            # This would be implemented with websockets
            pass
    
    def run(self, host='0.0.0.0', port=5000):
        """Run the tunnel bridge server"""
        logger.info("🚇 Starting Sofia Tunnel Bridge...")
        logger.info(f"🌐 Server will be available at: http://{host}:{port}")
        logger.info("🔗 To tunnel: ngrok http 5000")
        
        self.app.run(host=host, port=port, debug=False)

if __name__ == '__main__':
    bridge = SofiaTunnelBridge()
    bridge.run()