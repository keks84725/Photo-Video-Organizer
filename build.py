"""
Standalone executable builder using PyInstaller.
Usage:
    pip install pyinstaller
    python build.py
"""
import os
import sys
import subprocess
from pathlib import Path

def build():
    root = Path(__file__).resolve().parent
    main_file = "main.py"

    sep = ";" if sys.platform == "win32" else ":"
    data_flag = f"assets{sep}assets"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=PhotoVideoOrganizer",
        "--noconsole",
        "--onefile",
        "--add-data", data_flag,
        "--clean",
        main_file
    ]

    print("🚀 Building standalone executable...")
    print("Command:", " ".join(cmd))
    result = subprocess.run(cmd, cwd=root)

    if result.returncode == 0:
        print("\n✅ Build completed successfully!")
        print("📁 Executable is located in the 'dist/' folder.")
    else:
        print(f"\n❌ Build failed with return code {result.returncode}")
        sys.exit(result.returncode)

if __name__ == "__main__":
    build()
