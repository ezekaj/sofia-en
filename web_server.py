#!/usr/bin/env python3
"""
Web server wrapper for Sofia Agent deployment
Provides health endpoints and manages the LiveKit agent
"""

import os
import sys
import asyncio
import logging
import json
import subprocess
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
import threading

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Sofia Agent Server", version="1.0.0")

# Global agent process
agent_process = None
agent_status = {"status": "starting", "start_time": datetime.now()}

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    global agent_status
    
    return JSONResponse({
        "status": "healthy",
        "service": "sofia-agent",
        "agent_status": agent_status["status"],
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": (datetime.now() - agent_status["start_time"]).total_seconds()
    })

@app.get("/status")
async def get_status():
    """Detailed status endpoint"""
    global agent_process, agent_status
    
    return JSONResponse({
        "service": "Sofia AI Agent",
        "agent_status": agent_status["status"],
        "agent_pid": agent_process.pid if agent_process else None,
        "environment": {
            "livekit_url": os.getenv("LIVEKIT_URL", "not_set"),
            "google_api_key": "configured" if os.getenv("GOOGLE_API_KEY") else "missing",
            "calendar_url": os.getenv("CALENDAR_URL", "not_set"),
            "python_env": os.getenv("PYTHON_ENV", "development"),
        },
        "start_time": agent_status["start_time"].isoformat(),
        "uptime_seconds": (datetime.now() - agent_status["start_time"]).total_seconds()
    })

def start_sofia_agent():
    """Start the Sofia agent in a background process"""
    global agent_process, agent_status
    
    try:
        logger.info("Starting Sofia Agent...")
        agent_status["status"] = "starting"
        
        # Start the agent
        agent_process = subprocess.Popen([
            sys.executable, "agent.py", "dev"
        ], cwd="/app")
        
        agent_status["status"] = "running"
        logger.info(f"Sofia Agent started with PID: {agent_process.pid}")
        
        # Monitor the process
        while True:
            if agent_process.poll() is not None:
                logger.warning("Sofia Agent process ended, restarting...")
                agent_status["status"] = "restarting" 
                agent_process = subprocess.Popen([
                    sys.executable, "agent.py", "dev"
                ], cwd="/app")
                agent_status["status"] = "running"
                logger.info(f"Sofia Agent restarted with PID: {agent_process.pid}")
            
            asyncio.sleep(10)  # Check every 10 seconds
            
    except Exception as e:
        logger.error(f"Error starting Sofia Agent: {e}")
        agent_status["status"] = "error"

@app.on_event("startup")
async def startup_event():
    """Start the Sofia agent when the web server starts"""
    logger.info("Starting Sofia Agent Web Server...")
    
    # Start Sofia agent in background thread
    agent_thread = threading.Thread(target=start_sofia_agent, daemon=True)
    agent_thread.start()
    
    logger.info("Sofia Agent Web Server started successfully")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    logger.info(f"Starting Sofia Agent server on port {port}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )