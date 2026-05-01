# Contributing

## Identity

Project owner and primary maintainer: **Sameer Alam**.

## Development expectations

- Keep benchmark outputs reproducible.
- Prefer deterministic attack logic over opaque randomness.
- Add tests for any new channel or attack.
- Update `results/report.pdf` and `results/benchmark_summary.json` whenever the scoring logic changes.

## Local workflow

```bash
python -m pip install -e .[dev]
npm install
npm run audit
```
