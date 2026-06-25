from __future__ import annotations

import json
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

DEFAULT_FILES: dict[str, Any] = {
    "game_state.json": {
        "session_id": "player_001",
        "current_day": 1,
        "story_stage": "day_1_intro",
        "protagonist_name": "Player",
        "wife_name": "Clanker",
        "ai_name": "Clanker",
        "identity_stage": "empty_shell",
    },
    "emotion_state.json": {
        "trust": 10,
        "stability": 70,
        "emotion": "confused",
    },
    "conversation_history.json": [],
    "long_term_memory.json": [],
}


def ensure_data_files() -> None:
    """Create the data folder and missing JSON files."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for filename, default_content in DEFAULT_FILES.items():
        path = DATA_DIR / filename
        if not path.exists() or path.read_text(encoding="utf-8").strip() == "":
            save_json(filename, default_content)


# Load file JSON, kalau hilang/ndak ada, buat baru
def load_json(filename: str) -> Any:
    ensure_data_files()
    path = DATA_DIR / filename

    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        default_content = DEFAULT_FILES.get(filename, {})
        save_json(filename, default_content)
        return default_content


# Simpan data ke JSON file
def save_json(filename: str, data: Any) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / filename

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
