"""
DeskMate Sensor Module
Monitors active window/foreground application on Windows
Detects state changes: coding, gaming, browsing, idle, etc.
"""

import time
import requests
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import win32gui
import win32process
import psutil


class ActivityState(Enum):
    """Activity states for the companion"""
    CODING = "coding"          # IDE windows
    GAMING = "gaming"          # Game windows
    BROWSING = "browsing"      # Browser windows
    MESSAGING = "messaging"    # Chat/Discord/Slack
    MEDIA = "media"            # Video/Music
    IDLE = "idle"              # Desktop/locked
    UNKNOWN = "unknown"


@dataclass
class WindowEvent:
    """Represents a window change event"""
    timestamp: datetime
    state: ActivityState
    window_title: str
    process_name: str


class WindowMonitor:
    """Monitors foreground window changes"""
    
    # Map process names to activity states
    STATE_MAPPING = {
        # IDEs
        r"code\.exe": ActivityState.CODING,
        r"pycharm64\.exe": ActivityState.CODING,
        r"idea64\.exe": ActivityState.CODING,
        r"devenv\.exe": ActivityState.CODING,
        r"sublime_text\.exe": ActivityState.CODING,
        r"vim\.exe": ActivityState.CODING,
        
        # Games
        r"genshinimpact\.exe": ActivityState.GAMING,
        r"steam\.exe": ActivityState.GAMING,
        r"epicgameslauncher\.exe": ActivityState.GAMING,
        r"valorant\.exe": ActivityState.GAMING,
        r"notepad\.exe": ActivityState.CODING,  # Simple text editor
        
        # Browsers
        r"chrome\.exe": ActivityState.BROWSING,
        r"firefox\.exe": ActivityState.BROWSING,
        r"msedge\.exe": ActivityState.BROWSING,
        r"iexplore\.exe": ActivityState.BROWSING,
        
        # Communication
        r"discord\.exe": ActivityState.MESSAGING,
        r"slack\.exe": ActivityState.MESSAGING,
        r"teams\.exe": ActivityState.MESSAGING,
        r"telegram\.exe": ActivityState.MESSAGING,
        
        # Media
        r"vlc\.exe": ActivityState.MEDIA,
        r"spotify\.exe": ActivityState.MEDIA,
    }
    
    def __init__(self, poll_interval: float = 3.0, server_url: str = "http://127.0.0.1:8000"):
        """
        Initialize window monitor
        Args:
            poll_interval: Seconds between window checks
            server_url: FastAPI server endpoint
        """
        self.poll_interval = poll_interval
        self.server_url = server_url
        self.last_state = ActivityState.IDLE
        self.running = False
    
    def get_foreground_window(self) -> tuple[str, str]:
        """
        Get the currently active window title and process name
        Returns:
            (window_title, process_name)
        """
        try:
            hwnd = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(hwnd)
            
            # Get process name
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            try:
                process = psutil.Process(pid)
                process_name = process.name().lower()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                process_name = "unknown"
            
            return title, process_name
        except Exception as e:
            print(f"Error getting foreground window: {e}")
            return "", "unknown"
    
    def map_to_state(self, process_name: str) -> ActivityState:
        """Map process name to activity state"""
        import re
        
        for pattern, state in self.STATE_MAPPING.items():
            if re.search(pattern, process_name):
                return state
        
        return ActivityState.UNKNOWN
    
    def send_event(self, event: WindowEvent):
        """Send event to FastAPI server"""
        try:
            response = requests.post(
                f"{self.server_url}/event",
                json={
                    "timestamp": event.timestamp.isoformat(),
                    "state": event.state.value,
                    "window_title": event.window_title,
                    "process_name": event.process_name,
                },
                timeout=2,
            )
            response.raise_for_status()
            print(f"✓ Event sent: {event.state.value} ({event.process_name})")
        except requests.exceptions.RequestException as e:
            print(f"✗ Failed to send event: {e}")
    
    def run(self):
        """Main monitoring loop"""
        print("DeskMate Sensor started. Monitoring foreground window...")
        print(f"Poll interval: {self.poll_interval}s")
        print(f"Server: {self.server_url}")
        print("-" * 50)
        
        self.running = True
        
        try:
            while self.running:
                window_title, process_name = self.get_foreground_window()
                current_state = self.map_to_state(process_name)
                
                # Only send event if state changed
                if current_state != self.last_state:
                    event = WindowEvent(
                        timestamp=datetime.now(),
                        state=current_state,
                        window_title=window_title,
                        process_name=process_name,
                    )
                    
                    print(f"{self.last_state.value} → {current_state.value}")
                    print(f"  Window: {window_title[:60]}")
                    print(f"  Process: {process_name}")
                    
                    self.send_event(event)
                    self.last_state = current_state
                
                time.sleep(self.poll_interval)
        
        except KeyboardInterrupt:
            print("\nSensor stopped by user.")
        except Exception as e:
            print(f"Sensor error: {e}")
        finally:
            self.running = False


def main():
    """Run the sensor"""
    monitor = WindowMonitor(poll_interval=3.0)
    monitor.run()


if __name__ == "__main__":
    main()
