from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from watermark_fortress.analysis.attacks import ATTACKS, run_attack
from watermark_fortress.analysis.defense_metrics import summarize_cases
from watermark_fortress.core.adaptive_watermark import AdaptiveWatermarker
from watermark_fortress.core.controller import AdaptiveController

ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / "data" / "demo_corpus.jsonl"
RESULTS_JSON = ROOT / "results" / "benchmark_summary.json"
RESULTS_PDF = ROOT / "results" / "report.pdf"


def load_corpus() -> list[dict[str, str]]:
    return [json.loads(line) for line in DATASET_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]


def run_case(sample: dict[str, str], attack: str) -> dict[str, Any]:
    adaptive = AdaptiveWatermarker(controller=AdaptiveController())
    baseline = AdaptiveWatermarker(controller=AdaptiveController(weights={"lexical": 0.6, "punctuation": 0.4, "zero_width": 1.6}))

    adaptive_original = adaptive.embed(sample["text"])
    adaptive_attacked_text = run_attack(attack, adaptive_original.text)
    adaptive_after = adaptive.detect(adaptive_attacked_text, adaptive_original.manifest)
    next_weights = adaptive.controller.evolve(adaptive_after)
    adaptive_healed = adaptive.embed(adaptive_attacked_text, weights=next_weights)
    adaptive_healed_report = adaptive.detect(adaptive_healed.text, adaptive_healed.manifest)

    baseline_original = baseline.embed(sample["text"], profile_id="baseline-static")
    baseline_attacked_text = run_attack(attack, baseline_original.text)
    baseline_after = baseline.detect(baseline_attacked_text, baseline_original.manifest)

    return {
        "sample_id": sample["id"],
        "attack": attack,
        "adaptive": {
            "after_confidence": adaptive_after.confidence,
            "after_verdict": adaptive_after.verdict,
            "healed_confidence": adaptive_healed_report.confidence,
            "healed_verdict": adaptive_healed_report.verdict,
            "next_weights": next_weights,
        },
        "baseline": {
            "after_confidence": baseline_after.confidence,
            "after_verdict": baseline_after.verdict,
        },
    }


def generate_pdf(summary: dict[str, Any]) -> None:
    RESULTS_PDF.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(RESULTS_PDF), pagesize=letter, topMargin=42, bottomMargin=42)
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "FortressTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=22,
        textColor=HexColor("#0F2538"),
        spaceAfter=10,
    )
    body = ParagraphStyle(
        "FortressBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=HexColor("#1E364B"),
    )
    story = [
        Paragraph("Watermark Fortress Technical Benchmark", title),
        Paragraph(
            "This report summarizes a demo sweep comparing a static watermark baseline against the adaptive, self-healing fortress controller across deterministic adversarial rewrites.",
            body,
        ),
        Spacer(1, 16),
    ]
    rows = [
        ["Metric", "Value"],
        ["Samples", str(summary["sample_count"])],
        ["Adaptive mean after attack", str(summary["adaptive_after_mean"])],
        ["Adaptive mean after healing", str(summary["adaptive_healed_mean"])],
        ["Baseline mean after attack", str(summary["baseline_after_mean"])],
        ["Healing lift", str(summary["healing_lift"])],
        ["Fortress lift over baseline", str(summary["fortress_lift_over_baseline"])],
    ]
    table = Table(rows, colWidths=[220, 150])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), HexColor("#0B1E2D")),
                ("TEXTCOLOR", (0, 0), (-1, 0), HexColor("#F8FBFF")),
                ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#C5D6E6")),
                ("BACKGROUND", (0, 1), (-1, -1), HexColor("#F2F7FB")),
                ("TEXTCOLOR", (0, 1), (-1, -1), HexColor("#102332")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("PADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 18))
    story.append(Paragraph("Attack Breakdown", styles["Heading2"]))
    for attack, metrics in summary["attack_breakdown"].items():
        story.append(
            Paragraph(
                f"<b>{attack}</b>: adaptive after={metrics['adaptive_after']}, healed={metrics['adaptive_healed']}, baseline after={metrics['baseline_after']}",
                body,
            )
        )
        story.append(Spacer(1, 8))
    doc.build(story)


def run_benchmark() -> dict[str, Any]:
    samples = load_corpus()
    cases = [run_case(sample, attack) for sample in samples for attack in ATTACKS]
    summary = summarize_cases(cases)
    payload = {
        "summary": summary,
        "cases": cases,
        "attacks": sorted(ATTACKS.keys()),
    }
    RESULTS_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    generate_pdf(summary)
    return payload


if __name__ == "__main__":
    run_benchmark()
