from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from benchmark.sweep import RESULTS_JSON, run_benchmark
from watermark_fortress.core.adaptive_watermark import AdaptiveWatermarker
from watermark_fortress.core.models import ChannelPlacement, WatermarkManifest

from .schemas import BattleRequest, BattleResponse, DetectRequest, DetectResponse, EmbedRequest, EmbedResponse, OverviewResponse

ROOT = Path(__file__).resolve().parents[3]
SAMPLE_TEXT = (
    "Because high-risk moderation flows run under scrutiny, however, important provenance cues should therefore remain resilient."
)

app = FastAPI(title="Watermark Fortress API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

watermarker = AdaptiveWatermarker()


def _load_results() -> dict[str, Any]:
    if not RESULTS_JSON.exists():
        return run_benchmark()
    return json.loads(RESULTS_JSON.read_text(encoding="utf-8"))


def _manifest_from_dict(payload: dict[str, Any]) -> WatermarkManifest:
    return WatermarkManifest(
        signature_id=payload["signature_id"],
        profile_id=payload["profile_id"],
        source_checksum=payload["source_checksum"],
        issued_at=payload["issued_at"],
        channel_weights=payload["channel_weights"],
        placements=[ChannelPlacement(**placement) for placement in payload["placements"]],
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "watermark-fortress-api"}


@app.get("/api/overview", response_model=OverviewResponse)
def overview() -> OverviewResponse:
    payload = _load_results()
    return OverviewResponse(
        repo_name="watermark-fortress",
        narrative=(
            "An adaptive watermarking benchmark and operations stack that compares a static baseline "
            "against a self-healing controller across deterministic adversarial rewrites."
        ),
        attacks=payload["attacks"],
        benchmark_summary=payload["summary"],
        latest_cases=payload["cases"][:6],
        example_text=SAMPLE_TEXT,
        channel_defaults=watermarker.controller.snapshot(),
    )


@app.post("/api/embed", response_model=EmbedResponse)
def embed(request: EmbedRequest) -> EmbedResponse:
    envelope = watermarker.embed(request.text, profile_id=request.profile_id)
    return EmbedResponse(text=envelope.text, manifest=envelope.manifest.to_dict())


@app.post("/api/detect", response_model=DetectResponse)
def detect(request: DetectRequest) -> DetectResponse:
    manifest = _manifest_from_dict(request.manifest)
    report = watermarker.detect(request.text, manifest)
    return DetectResponse(report=report.to_dict())


@app.post("/api/battle", response_model=BattleResponse)
def battle(request: BattleRequest) -> BattleResponse:
    result = watermarker.battle(request.text, request.attack)
    return BattleResponse(battle=result.to_dict())


@app.post("/api/benchmark/run")
def benchmark_run() -> dict[str, Any]:
    return run_benchmark()
