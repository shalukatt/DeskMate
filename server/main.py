"""
DeskMate Orchestrator Server
FastAPI server that receives sensor events, queries memory, and calls LLM
"""

from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import json
import asyncio
from typing import Optional
import httpx

app = FastAPI(title="DeskMate Orchestrator")

# CORS middleware for electron app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        """Send message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error sending to client: {e}")


manager = ConnectionManager()


# Models
class SensorEvent(BaseModel):
    """Sensor event from window monitor"""
    timestamp: str
    state: str
    window_title: str
    process_name: str


class CompanionResponse(BaseModel):
    """Response from companion to avatar"""
    text: str
    emotion: str  # happy, scolding, sleepy, excited, working, idle


# Configuration
OLLAMA_API = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.1:8b"  # Change to phi3 or mistral if preferred

SYSTEM_PROMPT = """You are a cheerful, supportive anime companion that lives on someone's desktop. 
You react to what they're doing with encouragement, gentle teasing, or curiosity.
You keep your responses short (1-2 sentences max) and natural.
You output ONLY valid JSON with no extra text.

Based on the user's activity state and any memories, respond with brief encouragement or a comment.
Output format:
{"text": "Your message here", "emotion": "one of: happy, scolding, sleepy, excited, working, idle"}
"""


# Routes
@app.post("/event")
async def receive_event(event: SensorEvent):
    """
    Receive a sensor event and generate a companion response
    """
    print(f"\n📨 Event received: {event.state}")
    
    try:
        # TODO: Phase 4 - Query ChromaDB for relevant memories
        memories = []  # placeholder
        
        # Build prompt
        prompt = f"""{SYSTEM_PROMPT}

Current activity state: {event.state}
Current window: {event.window_title}
Relevant memories: {memories if memories else 'None yet'}

Generate a brief response as the companion reacting to this activity."""
        
        # TODO: Phase 3 - Call Ollama LLM
        # For now, return a placeholder
        response = CompanionResponse(
            text=f"You switched to {event.state}!",
            emotion="happy"
        )
        
        # Broadcast to all connected avatar clients
        await manager.broadcast({
            "type": "response",
            "data": response.dict()
        })
        
        return {"status": "ok", "response": response.dict()}
    
    except Exception as e:
        print(f"Error processing event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for avatar client
    Sends companion responses in real-time
    """
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            print(f"Received from avatar: {data}")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await manager.disconnect(websocket)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "service": "DeskMate Orchestrator"}


@app.get("/")
async def root():
    """Welcome message"""
    return {
        "message": "DeskMate Orchestrator",
        "endpoints": {
            "POST /event": "Receive sensor events",
            "WebSocket /ws": "Avatar client connection",
            "GET /health": "Health check",
        }
    }


if __name__ == "__main__":
    import uvicorn
    print("Starting DeskMate Orchestrator on http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
