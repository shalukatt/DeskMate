from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import time 
import json
import requests
import uvicorn

app = FastAPI(title = "DeskMate Orchestrator")

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.1:8b"

COOLDOWN_SECONDS = 30

#Placeholder persona — flesh this out properly in Phase 6.
PERSONA = """You are Mira, a cheerful, slightly teasing anime desktop companion who lives on the user's screen.
You've been watching what app the user has focused. React briefly and in-character to what they're doing now.
Keep it short — one or two sentences, casual, like a real-time comment, not a lecture."""

class Event(BaseModel):
    state: str
    process: Optional[str] = None
    timestamp: Optional[str] = None

# In-memory store for now — swap for ChromaDB once we hit Phase 4 (memory)
latest_event: Optional[Event] = None
event_log: list[Event] = []
last_reply_time: Optional[float] = None

def build_prompt(event: Event) -> str:
    return f"""{PERSONA}
 
Current activity: {event.state} (process: {event.process})
 
Respond ONLY with a JSON object, no markdown fences, no extra commentary, in this exact shape:
{{"text": "<your short in-character line>", "emotion": "happy|scolding|sleepy|excited|neutral"}}"""


def generate_companion_response(event: Event) -> dict:
    prompt = build_prompt(event)
    raw = ""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=20,
        )
        response.raise_for_status()
        raw = response.json()["response"].strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(raw)
        return {
            "text": parsed.get("text", "..."),
            "emotion": parsed.get("emotion", "neutral"),
        }
    except json.JSONDecodeError:
        print(f"[LLM RESPONSE NOT VALID JSON] raw: {raw!r}")
        return {"text": "...", "emotion": "neutral"}
    except Exception as e:
        print(f"[LLM CALL FAILED] {e}")
        return {"text": "...", "emotion": "neutral"}


@app.post("/event")
async def receive_event(event: Event):
    """Sensor calls this every time the active-window state changes."""
    global latest_event,last_reply_time
 
    if not event.timestamp:
        event.timestamp = datetime.now().isoformat()
 
    latest_event = event
    event_log.append(event)
 
    print(f"[EVENT] {event.timestamp} — {event.process} -> {event.state}")

    # Cooldown logic to avoid spamming the LLM with too many calls in a short time.
 
    now = time.time()
    if last_reply_time is not None and (now - last_reply_time) < COOLDOWN_SECONDS:
        remaining = COOLDOWN_SECONDS - (now - last_reply_time)
        print(f"[COOLDOWN] Skipping LLM call ({remaining:.0f}s left) — event still logged")
        reply = {"text": None, "emotion": None, "skipped": True}
    else:
        reply = generate_companion_response(event)
        last_reply_time = now
        print(f"[COMPANION] ({reply['emotion']}) {reply['text']}")
 
    # Memory lookup (Phase 4) will get injected into build_prompt() before this call, later.
    return {"status": "ok", "received": event, "reply": reply}

@app.get("/state")
async def get_state():
    """Quick way to check what the server thinks you're doing right now."""
    if latest_event is None:
        return {"state": "unknown"}
    return latest_event
 
 
@app.get("/events")
async def get_events(limit: int = 20):
    """Recent event history, useful for debugging and later for the nightly summary job."""
    return event_log[-limit:]
 
 
if __name__ == "__main__":
    uvicorn.run("server.main:app", host="127.0.0.1", port=8000, reload=True)