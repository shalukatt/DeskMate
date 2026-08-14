One heads-up: Python 3.14 is very new, and a couple of libraries we'll need later (ChromaDB especially, which depends on onnxruntime) sometimes lag behind on supporting brand-new Python versions. Let's just proceed — if pip install fails on something in Phase 4, we'll deal with it then (easy fix: install Python 3.11/3.12 alongside via py -3.12 and make a second venv just for that piece). Not a blocker now.

#### Folder Structure #### 

Folder	Purpose
sensor/	The Python background script — polls the active window/process every few seconds and detects state changes (idle → coding → gaming, etc.)
server/	The FastAPI orchestrator — receives events from the sensor, builds prompts, calls Ollama, queries memory, and pushes responses to the avatar over WebSocket. This is the "brain" wiring
avatar/	The Electron app — the actual transparent floating window, sprite rendering, speech bubble, listens for WebSocket messages from the server
assets/	Static files: PNGTuber sprite images now, Live2D model files later, any audio clips
data/	Local storage — ChromaDB's memory database files, logs, anything persistent that isn't code

#### terminal codes ####
cd D:\Projects\DeskMate
python sensor/watcher.py