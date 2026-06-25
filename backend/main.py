from __future__ import annotations

import requests
from fastapi import FastAPI, HTTPException

from emotion_manager import apply_emotion_change, get_emotion_state
from json_parser import parse_llm_json
from memory_manager import (
    add_history,
    get_memories,
    get_recent_history,
    save_memory,
    summarize_day_simple,
)
from prompt_builder import build_prompt
from save_manager import DEFAULT_FILES, ensure_data_files, load_json, save_json
from schemas import ChatRequest, ChatResponse, StateResponse

app = FastAPI(title="Bini Clanker")

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "phi3"

#mengirim prompt ke ollama phi3
def ask_ollama(prompt: str) -> str:
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.2,
            "top_p": 0.9,
            "num_predict": 500,
        },
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=60,
        )

        response.raise_for_status()

        data = response.json()
        return data.get("response", "")

    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            "Cannot connect to Ollama. Make sure Ollama is running with: ollama serve"
        )

    except requests.exceptions.Timeout:
        raise RuntimeError(
            "Ollama took too long to respond. Try again or reduce the prompt size."
        )

    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Ollama request failed: {exc}")


#memastikan file json tersedia saat start API
@app.on_event("startup")
def startup() -> None:
    ensure_data_files()

#endpoint untuk mengecek backend aktif/ndak
@app.get("/")
def root() -> dict:
    return {
        "message": "Bini Clanker is running.",
        "docs": "/docs",
    }

#basically untuk chat: menerima pesan dari player -> mengirim ke phi3 -> update memory/emotion -> dibalikin dengan respon AI
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> dict:
    game_state = load_json("game_state.json")
    emotion_state = get_emotion_state()
    recent_history = get_recent_history(limit=6)
    memories = get_memories(limit=10)

    prompt = build_prompt(
        player_message=request.message,
        game_state=game_state,
        emotion_state=emotion_state,
        recent_history=recent_history,
        memories=memories,
    )

    try:
        raw_output = ask_ollama(prompt)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    parsed = parse_llm_json(raw_output)
    updated_emotion = apply_emotion_change(parsed["emotion_change"])

    memory_saved = ""
    if parsed["analysis"]["important"] and parsed["memory_to_save"]:
        memory_saved = save_memory(
            parsed["memory_to_save"],
            memory_type=parsed["analysis"]["intent"],
        )

    add_history(
        player_message=request.message,
        ai_reply=parsed["reply"],
        analysis=parsed["analysis"],
        emotion=updated_emotion,
    )

    return {
        "reply": parsed["reply"],
        "analysis": parsed["analysis"],
        "emotion": updated_emotion,
        "memory_saved": memory_saved,
        "current_day": game_state.get("current_day", 1),
    }


#endpoint untuk cek emotion/game_state
@app.get("/state", response_model=StateResponse)
def get_state() -> dict:
    return {
        "game_state": load_json("game_state.json"),
        "emotion_state": get_emotion_state(),
    }


#endpoint untuk melihat percakapan terakhir/history chat
@app.get("/history")
def history() -> dict:
    return {
        "history": get_recent_history(limit=20),
    }


#endpoint untuk melihat memory yang sudah disimpan
@app.get("/memories")
def memories() -> dict:
    return {
        "memories": get_memories(limit=50),
    }


#Endpoint untuk mengakhiri hari dan pindah ke hari selanjutnya, membuat summary + menaikkan hari
@app.post("/reset_day")
def reset_day() -> dict:
    game_state = load_json("game_state.json")

    saved_summary = summarize_day_simple()

    current_day = int(game_state.get("current_day", 1))
    game_state["current_day"] = current_day + 1
    game_state["story_stage"] = f"day_{current_day + 1}"

    if game_state["current_day"] >= 4:
        game_state["identity_stage"] = "questioning_identity"
    elif game_state["current_day"] >= 2:
        game_state["identity_stage"] = "learning_past_self"

    save_json("game_state.json", game_state)

    return {
        "message": "Day reset complete.",
        "current_day": game_state["current_day"],
        "story_stage": game_state["story_stage"],
        "identity_stage": game_state.get("identity_stage", "empty_shell"),
        "summary_saved": saved_summary,
    }


#endpoint untuk mereset semua data json ke kondisi awal
@app.post("/reset_all")
def reset_all() -> dict:
    for filename, default_data in DEFAULT_FILES.items():
        save_json(filename, default_data)

    return {"message": "All JSON save data has been reset."}
