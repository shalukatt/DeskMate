# 📅 DeskMate - Implementation Timeline & Next Steps

## Phase 0: ✅ COMPLETE (85%)
**Status:** Infrastructure ready, awaiting Node.js + Ollama installation

### What's done:
- ✅ Python environment (3.14.6 with venv)
- ✅ All Python dependencies installed
- ✅ Project structure created
- ✅ Git repo initialized
- ✅ Sensor monitor module (sensor/monitor.py) - READY TO TEST
- ✅ FastAPI server (server/main.py) - READY TO TEST
- ✅ Configuration files (.env, .gitignore, requirements.txt)

### What's pending:
- ⏳ Install Node.js LTS (~5 min)
- ⏳ Install Ollama & pull llama3.1:8b (~15 min)

### Once installations complete:
1. Test sensor module
2. Test FastAPI server
3. Verify WebSocket connectivity

---

## Phase 1: Minimal Transparent Avatar Window
**Timeline:** 2-3 days (after Node.js installed)

### Deliverables:
- [ ] Electron project initialized
- [ ] Frameless, transparent window
- [ ] Static PNG sprite display
- [ ] Speech bubble div
- [ ] Window draggable

### Key files to create:
- `avatar/main.js` - Electron entry point
- `avatar/renderer.js` - Window rendering logic
- `avatar/styles.css` - Avatar styling
- `avatar/index.html` - Window HTML structure
- `avatar/package.json` - npm configuration

### Implementation approach:
```javascript
// key features needed:
// - BrowserWindow: frame=false, transparent=true, alwaysOnTop=true
// - preload script for security
// - WebSocket client connecting to server /ws endpoint
// - Message listener for JSON responses with text + emotion
// - Dynamic sprite/emotion rendering
```

---

## Phase 2: Sensor - Active Window Monitoring
**Timeline:** 1-2 days (runs parallel with Phase 1)

### Status:
- ✅ Module already created (sensor/monitor.py)
- ✅ All logic implemented:
  - Window polling
  - State detection
  - HTTP POST to server
  - Efficient change detection

### To test immediately:
```bash
# Terminal 1: Start server
cd d:\Projects\DeskMate && .\venv\Scripts\Activate.ps1
python -m uvicorn server.main:app --reload

# Terminal 2: Start sensor
cd d:\Projects\DeskMate && .\venv\Scripts\Activate.ps1
python sensor/monitor.py

# Switch apps and watch console output
```

---

## Phase 3: Orchestrator Server
**Timeline:** 2-3 days (integrate with Ollama)

### Current status:
- ✅ Basic server structure created (server/main.py)
- ⏳ Ollama integration needed

### Tasks:
- [ ] Test connection to Ollama
- [ ] Implement LLM prompt generation
- [ ] Parse JSON responses from Ollama
- [ ] Build system prompt with personality
- [ ] Error handling & retries

### Key function to implement:
```python
async def query_ollama(prompt: str) -> dict:
    """Query Ollama and return JSON response"""
    # POST to http://localhost:11434/api/generate
    # Parse response format
    # Return validated CompanionResponse
```

---

## Phase 4: Memory System
**Timeline:** 3 days

### Components:
- [ ] ChromaDB initialization
- [ ] Embedding generation
- [ ] Memory storage on each event
- [ ] Nightly summarization job
- [ ] Memory retrieval & injection into prompt

### Key implementation:
- Store events with timestamps
- Summarize daily using LLM
- Create embeddings for semantic search
- Inject top 3-5 memories into context

---

## Phase 5: Full Integration
**Timeline:** 2 days

### Loop to test:
1. Sensor detects app switch
2. Posts to /event endpoint
3. Server queries memory
4. Server calls Ollama LLM
5. Server sends response via WebSocket
6. Avatar displays text + emotion
7. Avatar sprite changes based on emotion

---

## Phase 6: Personality & Polish
**Timeline:** 3-4 days

### Tasks:
- [ ] Write strong system prompt
- [ ] Create 6 sprite variations (emotions)
- [ ] Add animations/transitions
- [ ] Implement cooldowns
- [ ] Add TTS (edge-tts) if desired
- [ ] Hotkey to mute/summon

---

## Phase 7: Stretch Goals
**Timeline:** Flexible

- Live2D model upgrade
- Voice input with faster-whisper
- More triggers (idle nudges, breaks)
- Settings UI
- Auto-startup

---

## 🎯 Recommended Order

### Week 1
1. ✅ Phase 0 - Setup complete
2. Phase 1 - Electron window (2-3 days)
3. Phase 2 - Sensor testing (parallel)

### Week 2
1. Phase 3 - Ollama integration (2-3 days)
2. Phase 4 - Memory system (3 days)

### Week 3
1. Phase 5 - Full integration (2 days)
2. Phase 6 - Polish & personality (3-4 days)

### Week 4+
1. Phase 7 - Stretch goals

---

## 📊 Progress Tracker

```
Phase 0: [████████████████████░░░░] 85% (waiting for installations)
Phase 1: [░░░░░░░░░░░░░░░░░░░░░░░░]  0%
Phase 2: [░░░░░░░░░░░░░░░░░░░░░░░░]  0% (code ready)
Phase 3: [░░░░░░░░░░░░░░░░░░░░░░░░]  0% (skeleton ready)
Phase 4: [░░░░░░░░░░░░░░░░░░░░░░░░]  0%
Phase 5: [░░░░░░░░░░░░░░░░░░░░░░░░]  0%
Phase 6: [░░░░░░░░░░░░░░░░░░░░░░░░]  0%
```

---

## 🔗 Important Commands

### Run Python Sensor
```bash
cd d:\Projects\DeskMate
.\venv\Scripts\Activate.ps1
python sensor/monitor.py
```

### Run FastAPI Server
```bash
cd d:\Projects\DeskMate
.\venv\Scripts\Activate.ps1
python -m uvicorn server.main:app --reload
```

### Update Python Dependencies
```bash
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Test Ollama
```bash
ollama run llama3.1:8b "You are a cheerful anime character. Respond briefly."
```

---

## 📞 Quick Reference

| Need | Solution | File |
|------|----------|------|
| Window detection logic | ✅ Done | sensor/monitor.py |
| Server framework | ✅ Done | server/main.py |
| Environment vars | ✅ Done | .env |
| Dependencies list | ✅ Done | requirements.txt |
| Electron setup | 🚧 Next | avatar/package.json |
| LLM integration | 🚧 Next | server/main.py |
| Memory DB | 🚧 Next | server/main.py |

---

**Ready to start Phase 1 once you install Node.js! 🚀**
