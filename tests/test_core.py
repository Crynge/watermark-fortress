from watermark_fortress.core.adaptive_watermark import AdaptiveWatermarker


def test_embed_and_detect_roundtrip() -> None:
    engine = AdaptiveWatermarker()
    envelope = engine.embed("Because important systems must remain robust, however, their provenance should stay visible.")
    report = engine.detect(envelope.text, envelope.manifest)
    assert report.verdict in {"fortified", "contested"}
    assert report.matched_placements >= 1


def test_battle_healing_improves_or_matches_post_attack_confidence() -> None:
    engine = AdaptiveWatermarker()
    battle = engine.battle(
        "Because important systems must remain robust, however, their provenance should stay visible.",
        "mixed_pressure",
    )
    assert battle.detection_healed.confidence >= battle.detection_after.confidence
