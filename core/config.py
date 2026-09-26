import json
import os
from pathlib import Path

CONFIG_FILE = Path.home() / ".photo_video_organizer_config.json"

DEFAULT_CONFIG = {
    "language": "EN",
    "mode": "full",
    "temp_path": "",
    "media_path": "",
    "duplicate_path": "",
    "other_path": ""
}

def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {**DEFAULT_CONFIG, **data}
        except Exception:
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()

def save_config(config: dict):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception:
        pass
