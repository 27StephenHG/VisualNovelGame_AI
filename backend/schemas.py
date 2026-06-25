from __future__ import annotations

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)


class Analysis(BaseModel):
    intent: str
    important: bool


class EmotionState(BaseModel):
    trust: int
    stability: int
    emotion: str


class ChatResponse(BaseModel):
    reply: str
    analysis: Analysis
    emotion: EmotionState
    memory_saved: str
    current_day: int


class StateResponse(BaseModel):
    game_state: dict
    emotion_state: EmotionState
