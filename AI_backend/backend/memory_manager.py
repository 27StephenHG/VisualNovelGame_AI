from __future__ import annotations

from datetime import datetime
from typing import Any

from save_manager import load_json, save_json

HISTORY_FILE = "conversation_history.json"
MEMORY_FILE = "long_term_memory.json"


def get_recent_history(limit: int = 6) -> list[dict[str, Any]]:
    history = load_json(HISTORY_FILE)
    if not isinstance(history, list):
        history = []
    return history[-limit:]


def add_history(player_message: str, ai_reply: str, analysis: dict, emotion: dict) -> None:
    history = load_json(HISTORY_FILE)
    if not isinstance(history, list):
        history = []

    history.append(
        {
            "time": datetime.now().isoformat(timespec="seconds"),
            "player": player_message,
            "ai": ai_reply,
            "analysis": analysis,
            "emotion": emotion,
        }
    )

    # menyimpan memori 100 chat terakhir saja
    history = history[-100:]
    save_json(HISTORY_FILE, history)


def get_memories(limit: int = 20) -> list[dict[str, Any]]:
    memories = load_json(MEMORY_FILE)
    if not isinstance(memories, list):
        memories = []
    return memories[-limit:]


def save_memory(memory_text: str, memory_type: str = "memory") -> str:
    memory_text = memory_text.strip()
    if memory_text == "":
        return ""

    memories = load_json(MEMORY_FILE)
    if not isinstance(memories, list):
        memories = []

    # Memori penting muncul dua kali = tidak kerecord
    for item in memories:
        if item.get("text", "").strip().lower() == memory_text.lower():
            return ""

    memories.append(
        {
            "time": datetime.now().isoformat(timespec="seconds"),
            "type": memory_type,
            "text": memory_text,
        }
    )

    save_json(MEMORY_FILE, memories)
    return memory_text


#Ambil percakapan akhir hari dan simpan ringkasannya ke long_term_memory.json
def summarize_day_simple() -> str:

    history = get_recent_history(limit=10)
    if not history:
        return ""

    important_lines = []
    for item in history:
        player_text = item.get("player", "")
        ai_text = item.get("ai", "")
        important_lines.append(f"Player said: {player_text} / AI replied: {ai_text}")

    summary = "End of day summary: " + " | ".join(important_lines)
    return save_memory(summary, memory_type="day_summary")
