# Audit

## Scope

Audit target: `watermark-fortress`

The audit covers:

- Python watermark core
- adversary attack suite
- benchmark sweep and report generation
- FastAPI control plane
- React dashboard
- browser smoke and screenshot generation

## Required checks

- editable Python install
- benchmark generation
- backend tests
- frontend lint
- frontend production build
- browser smoke over live local servers

## Verification commands

```bash
python -m pip install -e .[dev]
npm install
python benchmark/sweep.py
python -m pytest tests -q
npm run lint:web
npm run build:web
python -m playwright install chromium
python C:/Users/samee/.codex/skills/webapp-testing/scripts/with_server.py --server "python serve_api.py --port 8011" --port 8011 --server "npm --workspace apps/web run dev -- --host 127.0.0.1 --port 5174" --port 5174 -- powershell -Command "$env:FORTRESS_WEB_URL='http://127.0.0.1:5174/?apiBase=http://127.0.0.1:8011'; python tests\web_smoke.py"
```

## Results

- `python benchmark/sweep.py`: passed and regenerated `results/benchmark_summary.json` plus `results/report.pdf`
- `python -m pytest tests -q`: passed with `4/4`
- `npm run lint:web`: passed
- `npm run build:web`: passed
- `npm run audit`: passed
- browser smoke over live local API + web servers: passed

## Artifacts

- screenshots:
  - `tests/artifacts/fortress-overview.png`
  - `tests/artifacts/fortress-battle.png`
- report bundle:
  - `results/benchmark_summary.json`
  - `results/report.pdf`
