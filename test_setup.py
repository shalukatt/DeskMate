"""
Quick test script to verify Phase 0 setup
Run this to check that all components are ready
"""

import sys
import subprocess
from pathlib import Path

def check_python():
    """Check Python version"""
    version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"✅ Python {version}")
    return True

def check_package(package_name):
    """Check if a Python package is installed"""
    try:
        __import__(package_name)
        print(f"✅ {package_name}")
        return True
    except ImportError:
        print(f"❌ {package_name} NOT INSTALLED")
        return False

def check_folders():
    """Check if project folders exist"""
    folders = ["sensor", "server", "avatar", "assets", "data"]
    base = Path(__file__).parent
    
    for folder in folders:
        path = base / folder
        if path.exists():
            print(f"✅ {folder}/ exists")
        else:
            print(f"❌ {folder}/ MISSING")
    return True

def check_files():
    """Check if key files exist"""
    files = [
        "sensor/monitor.py",
        "server/main.py",
        ".env",
        "requirements.txt",
        "venv/pyvenv.cfg",
    ]
    base = Path(__file__).parent
    
    for file in files:
        path = base / file
        if path.exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} MISSING")

def check_external_tools():
    """Check for external tools"""
    tools = {
        "node": "Node.js",
        "npm": "NPM",
        "ollama": "Ollama",
    }
    
    for cmd, name in tools.items():
        try:
            result = subprocess.run(
                [cmd, "--version"],
                capture_output=True,
                timeout=2,
            )
            if result.returncode == 0:
                print(f"✅ {name}")
            else:
                print(f"❌ {name} (error checking)")
        except Exception:
            print(f"❌ {name} NOT INSTALLED or NOT IN PATH")

def main():
    print("\n" + "="*60)
    print("DeskMate Phase 0 Setup Verification")
    print("="*60 + "\n")
    
    print("📦 Python Version & Packages:")
    check_python()
    
    packages = [
        "fastapi",
        "uvicorn",
        "psutil",
        "chromadb",
        "websockets",
        "win32gui",
    ]
    
    for pkg in packages:
        check_package(pkg)
    
    print("\n📁 Project Folders:")
    check_folders()
    
    print("\n📄 Project Files:")
    check_files()
    
    print("\n🔧 External Tools:")
    check_external_tools()
    
    print("\n" + "="*60)
    print("✨ Verification Complete!")
    print("="*60 + "\n")
    
    print("⚠️  IMPORTANT - Still need to install:")
    print("   1. Node.js LTS from https://nodejs.org/")
    print("   2. Ollama from https://ollama.com/")
    print("\nOnce installed, run:")
    print("   ollama pull llama3.1:8b")
    print("\nThen you can start Phase 1! 🚀\n")

if __name__ == "__main__":
    main()
