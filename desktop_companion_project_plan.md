# Always-On Desktop Anime Companion — Project Plan

A step-by-step build plan for a transparent, floating desktop companion that reacts to what you're doing on your PC, remembers your habits, and talks to you — built entirely with free tools.

---

## 0. Project Overview

**Goal:** A floating avatar (PNGTuber → Live2D later) that:
- Idles quietly while you work/study
- Detects when you switch apps (IDE, game, browser, etc.) and reacts in character
- Remembers patterns over time (e.g. late-night gaming) and brings them up later
- Runs 100% locally/free — no paid APIs or subscriptions required

**Architecture in one line:**
`Sensor (window monitor) → Orchestrator (local server) → Brain (LLM + memory) → Face (avatar overlay)`

**Full stack:**
| Layer | Tool |
|---|---|
| Avatar | Electron + PNGTuber sprites (v1) → Live2D Cubism Web SDK (v2) |
| Sensor | Python + psutil + OS-specific window API |
| Orchestrator | FastAPI (Python) + WebSockets |
| Brain | Ollama (Llama 3.1 8B / Phi-3 / Mistral 7B) or Groq free tier |
| Memory | ChromaDB (local vector store) |
| Voice (optional) | edge-tts / VOICEVOX (TTS), faster-whisper (STT) |

---

## Phase 0 — Setup & Environment (Day 1)

- [ ] Install Python 3.11+, Node.js LTS
- [ ] Install [Ollama](https://ollama.com) and pull a model: `ollama pull llama3.1:8b` (or `phi3`, `mistral`)
- [ ] Test it responds: `ollama run llama3.1:8b "say hi as a cheerful anime companion"`
- [ ] Create a Python venv, install: `fastapi uvicorn psutil chromadb websockets`
- [ ] Create an Electron project: `npm init`, `npm install electron --save-dev`
- [ ] Set up a git repo with this folder structure:
```
companion/
  sensor/          # Python window-monitoring script
  server/          # FastAPI orchestrator + memory + LLM calls
  avatar/          # Electron app (overlay window)
  assets/          # sprites / Live2D model later
  data/            # chroma db storage
```

**Milestone:** All tools installed and talking to each other in isolation (Ollama responds, Electron opens a blank transparent window).

---

## Phase 1 — Minimal Transparent Avatar Window (Days 2–3)

- [ ] Build a basic Electron window: frameless, transparent background, always-on-top, click-through except on the avatar itself
- [ ] Display a single static PNG sprite (placeholder is fine)
- [ ] Add a simple speech-bubble `<div>` that can show text on command
- [ ] Make the window draggable so you can reposition the companion

**Milestone:** A static image floats on your desktop, always on top, over any app.

---

## Phase 2 — Sensor: Active Window Monitoring (Days 4–5)

- [ ] Write a Python script that polls the foreground window every 2–5 seconds
  - Windows: `pywin32` (`GetForegroundWindow`, `GetWindowText`)
  - macOS: `Quartz` / `AppKit`
  - Linux: `xdotool getactivewindow` or `wmctrl`
- [ ] Map window/process names → states, e.g.:
  - `Code.exe`, `pycharm64.exe` → `coding`
  - `GenshinImpact.exe`, `steam.exe` games → `gaming`
  - browsers → `browsing`
  - nothing relevant / screen locked → `idle`
- [ ] Only emit an event when the **state changes** (not every poll) to avoid spam
- [ ] Print events to console first, then send as HTTP POST to a placeholder endpoint

**Milestone:** Script correctly prints `idle → coding → gaming → idle` as you switch apps.

---

## Phase 3 — Orchestrator Server (Days 6–8)

- [ ] Build a FastAPI server with:
  - `POST /event` — receives sensor state-change events
  - A WebSocket endpoint `/ws` — pushes companion responses to the Electron avatar
- [ ] On receiving an event:
  1. Look up a persona system prompt (define your companion's personality/tone)
  2. Query ChromaDB for relevant memories (see Phase 4)
  3. Build a full prompt: persona + current state + retrieved memories + instruction to output JSON like `{"text": "...", "emotion": "happy|scolding|sleepy|excited"}`
  4. Send prompt to Ollama, parse the JSON response
  5. Push the result over the WebSocket to the avatar

**Milestone:** Opening VS Code triggers a real LLM-generated line of encouragement that appears in the avatar's speech bubble.

---

## Phase 4 — Memory System (Days 9–11)

- [ ] Set up ChromaDB locally, create a collection (e.g. `companion_memories`)
- [ ] Every event (or a periodic summary) gets embedded and stored with a timestamp, e.g.:
  - `"User opened Genshin Impact at 23:47"`
  - `"User was still gaming at 02:10"`
- [ ] Write a **nightly summarization job** (simple scheduled script) that:
  - Pulls the day's raw events
  - Asks the LLM to summarize them into 1–3 short memory sentences
  - Embeds and stores those summaries (don't store every raw event forever — keep it light)
- [ ] On each new event, query Chroma for the top 3–5 most relevant past memories to inject into the prompt

**Milestone:** After a late-night gaming session, the next "idle" trigger in the morning produces a line referencing it (e.g. "You were up late again last night...").

---

## Phase 5 — Connect Everything (Days 12–13)

- [ ] Sensor → sends real events to the FastAPI server (not console)
- [ ] Server → generates response using LLM + memory → pushes via WebSocket
- [ ] Electron avatar → listens on WebSocket, updates:
  - Sprite/pose based on `emotion` field
  - Speech bubble text
- [ ] Test the full loop: switch apps → see companion react in real time

**Milestone:** Full end-to-end loop works without touching the console.

---

## Phase 6 — Personality & Polish (Days 14–17)

- [ ] Write a solid system prompt defining tone, quirks, speech patterns, things it should/shouldn't say
- [ ] Add 4–6 PNGTuber sprite states (idle, happy, scolding, sleepy, excited, working)
- [ ] Add simple animation (fade/slide transitions between sprites, subtle idle bobbing)
- [ ] Add cooldowns so it doesn't talk too often (e.g. max 1 comment per 5–10 min unless state changes)
- [ ] (Optional) Add `edge-tts` so it speaks its lines out loud
- [ ] (Optional) Add a hotkey to manually summon/mute the companion

**Milestone:** It actually feels like a companion, not a debug console.

---

## Phase 7 — Stretch Goals (Later)

- [ ] Swap PNGTuber for a real **Live2D model** (rigged model + Cubism Web SDK)
- [ ] Add voice input (faster-whisper) so you can talk back to it
- [ ] Add more triggers: idle-too-long nudges, Pomodoro/break reminders, calendar awareness
- [ ] Package the sensor + server + Electron app to auto-launch on startup
- [ ] Build a small settings UI (persona tone, quiet hours, sensitivity)

---

## Suggested Timeline

| Week | Focus |
|---|---|
| 1 | Phases 0–2: environment, static avatar window, working sensor |
| 2 | Phases 3–4: orchestrator + LLM responses + memory |
| 3 | Phases 5–6: full integration + personality polish |
| 4+ | Phase 7: stretch goals, Live2D upgrade, voice |

## Notes
- Start with **PNGTuber**, not Live2D — Live2D adds real complexity (rigging/model licensing) that isn't needed to validate the core idea.
- Keep the LLM prompt **strict about JSON output format** — this is the most common source of bugs (malformed responses breaking the avatar).
- Everything here runs locally and costs $0: Ollama, ChromaDB, Electron, and Python tooling are all free and open-source.
