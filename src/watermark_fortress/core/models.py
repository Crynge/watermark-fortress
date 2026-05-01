from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ChannelPlacement:
    channel: str
    anchor: str
    expected_surface: str
    fallback_surface: str
    evidence_window: str
    strength: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class WatermarkManifest:
    signature_id: str
    profile_id: str
    source_checksum: str
    issued_at: str
    channel_weights: dict[str, float]
    placements: list[ChannelPlacement] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["placements"] = [placement.to_dict() for placement in self.placements]
        return payload


@dataclass
class WatermarkEnvelope:
    text: str
    manifest: WatermarkManifest

    def to_dict(self) -> dict[str, Any]:
        return {"text": self.text, "manifest": self.manifest.to_dict()}


@dataclass
class ChannelScore:
    channel: str
    expected_count: int
    matched_count: int
    survival_rate: float
    confidence: float
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DetectionReport:
    verdict: str
    confidence: float
    matched_placements: int
    total_placements: int
    channel_scores: list[ChannelScore]
    tamper_flags: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "verdict": self.verdict,
            "confidence": self.confidence,
            "matched_placements": self.matched_placements,
            "total_placements": self.total_placements,
            "channel_scores": [score.to_dict() for score in self.channel_scores],
            "tamper_flags": self.tamper_flags,
        }


@dataclass
class BattleResult:
    original: dict[str, Any]
    attacked: dict[str, Any]
    healed: dict[str, Any]
    detection_before: DetectionReport
    detection_after: DetectionReport
    detection_healed: DetectionReport
    next_weights: dict[str, float]

    def to_dict(self) -> dict[str, Any]:
        return {
            "original": self.original,
            "attacked": self.attacked,
            "healed": self.healed,
            "detection_before": self.detection_before.to_dict(),
            "detection_after": self.detection_after.to_dict(),
            "detection_healed": self.detection_healed.to_dict(),
            "next_weights": self.next_weights,
        }
