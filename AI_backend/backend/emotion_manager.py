from __future__ import annotations

from save_manager import load_json, save_json

EMOTION_FILE = "emotion_state.json"

ALLOWED_EMOTIONS = {
    "neutral",
    "curious",
    "sad",
    "warm",
    "confused",
    "unstable",
    "angry",
    "afraid",
}


def clamp(value: int, minimum: int = 0, maximum: int = 100) -> int:
    return max(minimum, min(maximum, value))


def get_emotion_state() -> dict:
    state = load_json(EMOTION_FILE)

    return {
        "trust": clamp(int(state.get("trust", 10))),
        "stability": clamp(int(state.get("stability", 70))),
        "emotion": state.get("emotion", "confused")
        if state.get("emotion", "confused") in ALLOWED_EMOTIONS
        else "confused",
    }


#perubahan emosi ditentukan oleh LLM
def apply_emotion_change(change: dict) -> dict:

    state = get_emotion_state()

    trust_change = change.get("trust", 0)
    stability_change = change.get("stability", 0)
    new_emotion = change.get("emotion", state["emotion"])

    if not isinstance(trust_change, int):
        trust_change = 0
    if not isinstance(stability_change, int):
        stability_change = 0
    if new_emotion not in ALLOWED_EMOTIONS:
        new_emotion = state["emotion"]

    state["trust"] = clamp(state["trust"] + trust_change)
    state["stability"] = clamp(state["stability"] + stability_change)
    state["emotion"] = new_emotion

    save_json(EMOTION_FILE, state)
    return state
