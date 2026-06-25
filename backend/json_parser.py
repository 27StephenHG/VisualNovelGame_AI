from __future__ import annotations

import json
from typing import Any

FALLBACK_RESPONSE = {
    "reply": "I heard you, but my memory is unstable. Please tell me again.",
    "analysis": {
        "intent": "unknown",
        "important": False,
    },
    "emotion_change": {
        "trust": 0,
        "stability": -1,
        "emotion": "unstable",
    },
    "memory_to_save": "",
}

ALLOWED_INTENTS = {
    "memory",
    "emotion",
    "question",
    "identity",
    "correction",
    "hostile",
    "unrelated",
    "unknown",
}

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


# Cari JSON
def _extract_json(raw_text: str) -> dict[str, Any] | None:
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        pass

    start = raw_text.find("{")
    end = raw_text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        return None

    try:
        return json.loads(raw_text[start : end + 1])
    except json.JSONDecodeError:
        return None


#LLM Return invalid JSON = respon daripada crash
def parse_llm_json(raw_text: str) -> dict[str, Any]:

    if not raw_text or not isinstance(raw_text, str):
        return FALLBACK_RESPONSE.copy()

    parsed = _extract_json(raw_text)
    if not isinstance(parsed, dict):
        return FALLBACK_RESPONSE.copy()

    reply = parsed.get("reply")
    analysis = parsed.get("analysis")
    emotion_change = parsed.get("emotion_change")
    memory_to_save = parsed.get("memory_to_save", "")

    if not isinstance(reply, str) or reply.strip() == "":
        reply = FALLBACK_RESPONSE["reply"]

    if not isinstance(analysis, dict):
        analysis = FALLBACK_RESPONSE["analysis"].copy()

    intent = analysis.get("intent", "unknown")
    if intent not in ALLOWED_INTENTS:
        intent = "unknown"

    important = analysis.get("important", False)
    if not isinstance(important, bool):
        important = False

    if not isinstance(emotion_change, dict):
        emotion_change = FALLBACK_RESPONSE["emotion_change"].copy()

    trust_change = emotion_change.get("trust", 0)
    stability_change = emotion_change.get("stability", 0)
    new_emotion = emotion_change.get("emotion", "neutral")

    if not isinstance(trust_change, int):
        trust_change = 0
    if not isinstance(stability_change, int):
        stability_change = 0
    if new_emotion not in ALLOWED_EMOTIONS:
        new_emotion = "neutral"

    trust_change = max(-5, min(5, trust_change))
    stability_change = max(-5, min(5, stability_change))

    if not isinstance(memory_to_save, str):
        memory_to_save = ""

    return {
        "reply": reply.strip(),
        "analysis": {
            "intent": intent,
            "important": important,
        },
        "emotion_change": {
            "trust": trust_change,
            "stability": stability_change,
            "emotion": new_emotion,
        },
        "memory_to_save": memory_to_save.strip(),
    }
