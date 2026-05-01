# Architecture

## Goal

`watermark-fortress` is built to answer one question:

> When watermarking is pushed through cheap, noisy, real-world rewrites, can an adaptive controller recover enough provenance signal to beat a static baseline?

## System map

```text
Corpus -> Fortress embedder -> Signed manifest -> Attack suite
     -> Detector -> Channel survival scores -> Adaptive controller
     -> Re-embed / self-heal -> Benchmark sweep -> PDF + dashboard
```

## Major layers

### `src/watermark_fortress/core`

- `channels.py`: keyed multi-channel embedding transforms
- `controller.py`: adaptive channel-weight updates
- `adaptive_watermark.py`: orchestration for embed, detect, and battle
- `models.py`: dataclass contract surface

### `adversary/attack_suite.py`

Deterministic red-team harness for:

- character perturbation
- Unicode scrubbing
- punctuation flattening
- whitespace collapse
- lexical rewrite
- combined mixed-pressure attacks

### `benchmark/sweep.py`

Runs the benchmark across the demo corpus and produces:

- `results/benchmark_summary.json`
- `results/report.pdf`

### `apps/api`

FastAPI control plane exposing:

- `/api/overview`
- `/api/embed`
- `/api/detect`
- `/api/battle`
- `/api/benchmark/run`

### `apps/web`

React/TypeScript dashboard for:

- benchmark summary review
- attack matrix exploration
- live battle execution
- before / after / healed inspection

## Why manifests exist

This repo intentionally uses a signed placement manifest rather than pretending blind detection is solved. That keeps the benchmark honest:

- we can measure channel survival directly
- we can attribute failure to a specific mechanism
- we can evolve the controller with visible evidence instead of binary guesses

## What “self-healing” means here

Self-healing does not mean the original watermark magically survives every rewrite. It means:

1. detect damage
2. score which channels survived
3. adapt channel weights
4. re-issue a stronger watermark on the attacked text

That is a runtime operational model, not a static watermark proof.
