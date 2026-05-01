from __future__ import annotations

from dataclasses import dataclass, field

from .models import DetectionReport


@dataclass
class AdaptiveController:
    weights: dict[str, float] = field(
        default_factory=lambda: {
            "lexical": 1.0,
            "punctuation": 0.78,
            "zero_width": 0.62,
        }
    )

    def snapshot(self) -> dict[str, float]:
        return dict(self.weights)

    def evolve(self, report: DetectionReport) -> dict[str, float]:
        for channel_score in report.channel_scores:
            current = self.weights.get(channel_score.channel, 0.5)
            if channel_score.survival_rate >= 0.7:
                current += 0.12
            elif channel_score.survival_rate <= 0.35:
                current -= 0.14
            else:
                current += 0.03
            self.weights[channel_score.channel] = round(min(max(current, 0.2), 1.9), 3)
        return self.snapshot()
