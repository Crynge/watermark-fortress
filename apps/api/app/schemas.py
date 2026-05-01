from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class EmbedRequest(BaseModel):
    text: str
    profile_id: str = "adaptive-fortress"


class DetectRequest(BaseModel):
    text: str
    manifest: dict[str, Any]


class BattleRequest(BaseModel):
    text: str
    attack: str


class OverviewResponse(BaseModel):
    repo_name: str
    narrative: str
    attacks: list[str]
    benchmark_summary: dict[str, Any]
    latest_cases: list[dict[str, Any]]
    example_text: str
    channel_defaults: dict[str, float]


class EmbedResponse(BaseModel):
    text: str
    manifest: dict[str, Any]


class DetectResponse(BaseModel):
    report: dict[str, Any]


class BattleResponse(BaseModel):
    battle: dict[str, Any]
