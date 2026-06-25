from fastapi import FastAPI
from pydantic import BaseModel
import requests
import json

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

# memuat parameter si clanker
def load_parameter():
    with open("memory/parameter.json", "r") as f:
        return json.load(f)

# menyimpan parameter si clanker
def save_parameter(parameter):
    with open("memory/parameter.json", "w") as f:
        json.dump(parameter, f, indent=4)

@app.post("/chat")
def chat(request: ChatRequest):

    player_message = request.message

    parameter = load_parameter()

    trust = parameter["trust"]
    stability = parameter["stability"]
    emotion = parameter["emotion"]

    prompt = f"""
You are Clanker.

You are an AI recreation of the protagonist's dead wife.

Current emotional state:
{emotion}

Trust level:
{trust}

Mental stability:
{stability}

Speak emotionally and naturally.

Player:
{player_message}
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "phi3",
            "prompt": prompt,
            "stream": False
        }
    )

    ai_response = response.json()["response"]

    return {
        "response": ai_response
    }