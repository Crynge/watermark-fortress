from __future__ import annotations

from statistics import mean
from typing import Any


def summarize_cases(cases: list[dict[str, Any]]) -> dict[str, Any]:
    adaptive_after = [case["adaptive"]["after_confidence"] for case in cases]
    adaptive_healed = [case["adaptive"]["healed_confidence"] for case in cases]
    baseline_after = [case["baseline"]["after_confidence"] for case in cases]
    attacks = sorted({case["attack"] for case in cases})

    attack_breakdown: dict[str, dict[str, float]] = {}
    for attack in attacks:
        attack_cases = [case for case in cases if case["attack"] == attack]
        attack_breakdown[attack] = {
            "adaptive_after": round(mean(case["adaptive"]["after_confidence"] for case in attack_cases), 3),
            "adaptive_healed": round(mean(case["adaptive"]["healed_confidence"] for case in attack_cases), 3),
            "baseline_after": round(mean(case["baseline"]["after_confidence"] for case in attack_cases), 3),
        }

    return {
        "sample_count": len(cases),
        "adaptive_after_mean": round(mean(adaptive_after), 3),
        "adaptive_healed_mean": round(mean(adaptive_healed), 3),
        "baseline_after_mean": round(mean(baseline_after), 3),
        "healing_lift": round(mean(adaptive_healed) - mean(adaptive_after), 3),
        "fortress_lift_over_baseline": round(mean(adaptive_healed) - mean(baseline_after), 3),
        "attack_breakdown": attack_breakdown,
    }
