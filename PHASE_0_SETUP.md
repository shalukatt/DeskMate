# Phase 0: Environment Setup - Progress Tracker

## Completed ✅
- [x] Python 3.14.6 installed
- [x] Project folder structure created (sensor/, server/, avatar/, assets/, data/)
- [x] Python venv created and activated
- [x] Dependencies installed: fastapi, uvicorn, psutil, chromadb, websockets, pywin32
- [x] Git repository initialized

## TODO - Install External Tools 📥

### 1. **Install Node.js LTS**
**Why:** Needed to build the Electron desktop app for the avatar

**Steps:**
1. Visit: https://nodejs.org/
2. Download LTS version (v20.x or v22.x recommended)
3. Run installer (accept defaults)
4. Verify: Open a new terminal and run `node --version`

**Estimated time:** 5 minutes

---

### 2. **Install Ollama**
**Why:** Local LLM brain for the companion's responses

**Steps:**
1. Visit: https://ollama.com
2. Download for Windows
3. Run installer
4. Start Ollama (should auto-start after install)
5. In a terminal, test: `ollama pull llama3.1:8b`
6. Verify: `ollama run llama3.1:8b "Hello, I'm a cheerful anime companion!"`

**Note:** First pull may take 5-10 minutes depending on internet. Model is ~4.7GB.

**Estimated time:** 10-15 minutes

---

### 3. **Verify Everything Works**
Once you've installed Node.js and Ollama:

```bash
cd d:\Projects\DeskMate
python --version          # Should show Python 3.14.6
node --version           # Should show Node version
ollama --version         # Should show Ollama version
ollama list              # Should show your installed models
```

---

## What's Next
Once Node.js and Ollama are installed, we'll:
- Initialize the Electron project in `avatar/`
- Create the first minimal transparent window
- Test the basic sensor script

**Proceed to Phase 1 once you've completed the above installation steps!**
