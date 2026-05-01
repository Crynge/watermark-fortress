from __future__ import annotations

import hashlib
import json
from uuid import uuid4

from watermark_fortress.analysis.attacks import ATTACKS, run_attack

from .channels import checksum, embed_lexical, embed_punctuation, embed_zero_width, normalize_text
from .controller import AdaptiveController
from .models import BattleResult, ChannelScore, DetectionReport, WatermarkEnvelope, WatermarkManifest, utc_now


class AdaptiveWatermarker:
    def __init__(self, secret: str = "fortress-lab-secret", controller: AdaptiveController | None = None) -> None:
        self.secret = secret
        self.controller = controller or AdaptiveController()

    def embed(self, text: str, profile_id: str = "adaptive-fortress", weights: dict[str, float] | None = None) -> WatermarkEnvelope:
        effective_weights = weights or self.controller.snapshot()
        working = text
        placements = []
        working, lexical_placements = embed_lexical(working, self.secret, effective_weights["lexical"])
        placements.extend(lexical_placements)
        working, punctuation_placements = embed_punctuation(working, self.secret, effective_weights["punctuation"])
        placements.extend(punctuation_placements)
        working, zero_width_placements = embed_zero_width(working, self.secret, effective_weights["zero_width"])
        placements.extend(zero_width_placements)
        manifest = WatermarkManifest(
            signature_id=f"sig-{uuid4().hex[:10]}",
            profile_id=profile_id,
            source_checksum=checksum(normalize_text(text)),
            issued_at=utc_now(),
            channel_weights=effective_weights,
            placements=placements,
        )
        return WatermarkEnvelope(text=working, manifest=manifest)

    def detect(self, text: str, manifest: WatermarkManifest) -> DetectionReport:
        channel_buckets: dict[str, list[tuple[bool, str]]] = {}
        matched = 0
        tamper_flags: list[str] = []

        for placement in manifest.placements:
            expected_match = placement.expected_surface in text or placement.evidence_window in text
            fallback_match = placement.fallback_surface in text
            matched += int(expected_match)
            channel_buckets.setdefault(placement.channel, []).append(
                (
                    expected_match,
                    "expected surface survived"
                    if expected_match
                    else "marker collapsed into fallback" if fallback_match else "marker and fallback both missing",
                )
            )

        channel_scores: list[ChannelScore] = []
        for channel, observations in channel_buckets.items():
            expected_count = len(observations)
            matched_count = sum(1 for ok, _ in observations if ok)
            survival_rate = matched_count / expected_count if expected_count else 0.0
            confidence = round(min(0.99, 0.2 + survival_rate * 0.75), 3)
            notes = sorted({detail for _, detail in observations})
            if survival_rate < 0.35:
                tamper_flags.append(f"{channel} channel collapsed below resilience threshold")
            channel_scores.append(
                ChannelScore(
                    channel=channel,
                    expected_count=expected_count,
                    matched_count=matched_count,
                    survival_rate=round(survival_rate, 3),
                    confidence=confidence,
                    notes=notes,
                )
            )

        total = len(manifest.placements)
        confidence = round(sum(score.confidence * score.expected_count for score in channel_scores) / max(total, 1), 3)
        if confidence >= 0.8:
            verdict = "fortified"
        elif confidence >= 0.52:
            verdict = "contested"
        else:
            verdict = "broken"
        return DetectionReport(
            verdict=verdict,
            confidence=confidence,
            matched_placements=matched,
            total_placements=total,
            channel_scores=channel_scores,
            tamper_flags=tamper_flags,
        )

    def battle(self, text: str, attack_name: str) -> BattleResult:
        if attack_name not in ATTACKS:
            raise KeyError(f"Unknown attack '{attack_name}'.")

        original = self.embed(text)
        attacked_text = run_attack(attack_name, original.text)
        detection_before = self.detect(original.text, original.manifest)
        detection_after = self.detect(attacked_text, original.manifest)
        next_weights = self.controller.evolve(detection_after)
        healed = self.embed(attacked_text, profile_id="adaptive-healed", weights=next_weights)
        detection_healed = self.detect(healed.text, healed.manifest)
        return BattleResult(
            original=original.to_dict(),
            attacked={
                "attack": attack_name,
                "text": attacked_text,
                "checksum": hashlib.sha256(attacked_text.encode("utf-8")).hexdigest()[:16],
            },
            healed=healed.to_dict(),
            detection_before=detection_before,
            detection_after=detection_after,
            detection_healed=detection_healed,
            next_weights=next_weights,
        )

    @staticmethod
    def serialize_manifest(manifest: WatermarkManifest) -> str:
        return json.dumps(manifest.to_dict(), indent=2)
