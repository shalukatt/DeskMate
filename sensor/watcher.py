import time
import json
import os
import win32gui
import win32process
import psutil
import requests

CACHE_PATH = os.path.join("data", "app_classifications.json")

HARDCODED = {
    # coding
    "code.exe": "coding",
    "pycharm64.exe": "coding",
    "devenv.exe": "coding",
    "sublime_text.exe": "coding",
    "atom.exe": "coding",

    # terminal
    "windowsterminal.exe": "terminal",
    "cmd.exe": "terminal",
    "powershell.exe": "terminal",
    "pwsh.exe": "terminal",

    # writing_docs
    "winword.exe": "writing_docs",
    "notion.exe": "writing_docs",
    "obsidian.exe": "writing_docs",
    "acrord32.exe": "writing_docs",

    # spreadsheets_data
    "excel.exe": "spreadsheets_data",

    # communication
    "discord.exe": "communication",
    "slack.exe": "communication",
    "whatsapp.exe": "communication",
    "outlook.exe": "communication",
    "zoom.exe": "communication",
    "teams.exe": "communication",

    # design_creative
    "photoshop.exe": "design_creative",
    "figma.exe": "design_creative",
    "premiere pro.exe": "design_creative",
    "blender.exe": "design_creative",

    # browsing
    "chrome.exe": "browsing",
    "firefox.exe": "browsing",
    "msedge.exe": "browsing",

    # media_consumption
    "spotify.exe": "media_consumption",
    "vlc.exe": "media_consumption",

    # gaming
    "genshinimpact.exe": "gaming",
    "steam.exe": "gaming",

    # system_utility
    "explorer.exe": "system_utility",
    "taskmgr.exe": "system_utility",
    "msi center.exe": "system_utility",
    "msicenter.exe": "system_utility",
    "controlpanel.exe": "system_utility",

    # screen capture
    "SnippingTool.exe": "screen_capture",
    "obs64.exe": "screen_capture",

    # VPN
    "openvpn.exe": "vpn",
    "wireguard.exe": "vpn",

    # AI
    "Copilot.exe": "ai_apps",

    # photo apps
    "Photos.exe": "photo_apps",

    # video apps
    "vlc.exe": "video_apps",
    "PotPlayerMini64.exe": "video_apps",                        
}

VALID_STATES = {
    "coding",
    "terminal",
    "writing_docs",
    "spreadsheets_data",
    "communication",
    "design_creative",
    "browsing",
    "social_media",
    "media_consumption",
    "gaming",
    "system_utility",
    "screen_capture",
    "vpn",
    "recycle_bin",
    "photo_apps",
    "video_apps",
    "ai_apps",
    "idle",
    "other",
}

STATE_DESCRIPTIONS = """
- coding: IDEs, code editors, Git tools
- terminal: Command Prompt, PowerShell, Terminal apps
- writing_docs: Word, Notion, Obsidian, PDF viewers
- spreadsheets_data: Excel, Google Sheets, data tools
- communication: Slack, Discord, WhatsApp, Email, Zoom, Teams
- design_creative: Photoshop, Figma, Premiere, Blender
- browsing: general web browsers used for search/research
- social_media: Reddit, Twitter/X, LinkedIn (as apps or clearly that site in a browser tab)
- media_consumption: YouTube, Netflix, Spotify, VLC
- gaming: actual PC games or game launchers being actively played
- system_utility: File Explorer, Settings, Task Manager, hardware control panels (e.g. MSI Center, motherboard/GPU utility software - these are NOT games even if the brand sounds gaming-related)
- screen_capture: screen recording, screenshots, screen capture, Snipping Tool, OBS recording, capture utilities
- vpn: VPN applications and VPN connection/management tools
- recycle_bin: Windows Recycle Bin or applications specifically managing deleted/recycled files
- photo_apps: photo viewing, photo organization, photo management, and photo gallery applications
- video_apps: video players and applications primarily used to watch/play videos
- ai_apps: AI assistants and AI applications such as Microsoft Copilot, ChatGPT, Claude, Gemini, Perplexity, etc.                                                               
- idle: nothing meaningful in focus
- other: anything that doesn't clearly fit the above
"""


def load_cache() -> dict:
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r") as f:
            return json.load(f)
    return {}


def save_cache(cache: dict):
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH, "w") as f:
        json.dump(cache, f, indent=2)


def ask_llm_to_classify(process_name: str) -> str:
    prompt = (
        "You are classifying a Windows application by what the user is actually DOING "
        "when that app is focused — not by guessing from the brand or name alone.\n\n"
        f"Categories:\n{STATE_DESCRIPTIONS}\n"
        f"Process name: {process_name}\n"
        "Respond with only the single classification word, nothing else."
    )
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3.1:8b", "prompt": prompt, "stream": False},
            timeout=15,
        )
        response.raise_for_status()
        result = response.json()["response"].strip().lower()
        for state in VALID_STATES:
            if state in result:
                return state
        return "other"
    except Exception as e:
        print(f"[LLM classification failed: {e}] defaulting to 'other'")
        return "other"


def get_active_window_process():
    hwnd = win32gui.GetForegroundWindow()
    if not hwnd:
        return None
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    try:
        process = psutil.Process(pid)
        return process.name()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return None


def classify_state(process_name: str, cache: dict) -> str:
    if not process_name:
        return "idle"

    name = process_name.lower()

    if name in HARDCODED:
        return HARDCODED[name]

    if name in cache:
        return cache[name]

    print(f"[UNKNOWN APP] '{name}' not in list or cache — asking LLM to classify...")
    state = ask_llm_to_classify(name)
    cache[name] = state
    save_cache(cache)
    print(f"[LEARNED] '{name}' -> '{state}' (saved to cache)")

    return state


def print_cache_summary(cache: dict):
    if not cache:
        return
    print("\n--- Cached app classifications ---")
    for app, state in sorted(cache.items()):
        print(f"  {app} -> {state}")
    print("-----------------------------------\n")
    print("(Edit data/app_classifications.json directly to correct any wrong entries)\n")


def main():
    cache = load_cache()
    print_cache_summary(cache)

    last_state = None
    print("Watching active window... (Ctrl+C to stop)")

    while True:
        process_name = get_active_window_process()
        state = classify_state(process_name, cache)

        if state != last_state:
            print(f"[STATE CHANGE] {last_state} -> {state}  (process: {process_name})")
            last_state = state

        time.sleep(2)


if __name__ == "__main__":
    main()


# ============================================================
#                    COMPLETE FLOW
# ============================================================

# The entire program works approximately like this:
#
#
#                 START PROGRAM
#                       |
#                       v
#               Load JSON Cache
#                       |
#                       v
#              Find Active Window
#                       |
#                       v
#              Get Process ID (PID)
#                       |
#                       v
#             Get Process Name
#                 e.g. chrome.exe
#                       |
#                       v
#               Is process empty?
#                 /          \
#               YES           NO
#                |             |
#              idle       Check HARDCODED
#                              |
#                              v
#                       Is it known?
#                         /       \
#                       YES        NO
#                        |          |
#                   return state   Check CACHE
#                                    |
#                                    v
#                              Is it cached?
#                               /       \
#                             YES        NO
#                              |          |
#                        return state   Ask Ollama
#                                           |
#                                           v
#                                    Get classification
#                                           |
#                                           v
#                                    Save to JSON cache
#                                           |
#                                           v
#                                    Return classification
#                                           |
#                                           v
#                                    Check state change
#                                           |
#                                           v
#                                      Wait 2 seconds
#                                           |
#                                           v
#                                    Repeat forever