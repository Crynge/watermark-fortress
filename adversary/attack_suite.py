from __future__ import annotations

from watermark_fortress.analysis.attacks import ATTACKS, run_attack


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Run a deterministic adversarial rewrite against a watermarked string.")
    parser.add_argument("attack", choices=sorted(ATTACKS.keys()))
    parser.add_argument("text")
    args = parser.parse_args()
    sys.stdout.write(run_attack(args.attack, args.text))
