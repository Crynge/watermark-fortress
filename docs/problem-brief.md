# Problem Brief

## Chosen direction

This repo takes the **watermark robustness** path rather than the broader containment path because it is:

- measurable
- benchmark-friendly
- deployable as a near-term library and service layer

## Research signals

These sources informed the scope and framing:

1. NDSS 2026: [Character-Level Perturbations Disrupt LLM Watermarks](https://www.ndss-symposium.org/wp-content/uploads/2026-s138-paper.pdf)
   - Shows small character-level perturbations can break fixed watermark detectors under restrictive attacker budgets.
2. ICLR 2026 OpenReview: [Catch-22: Pareto Frontier for Detectability and Robustness in LLM Watermarking](https://openreview.net/forum?id=pAeEzS4LwS)
   - Frames robustness and detectability as a tradeoff frontier rather than a free lunch.
3. 2026 watermark survey coverage: [Watermarking techniques for large language models: a survey](https://link.springer.com/article/10.1007/s10462-025-11474-6)
   - Useful for understanding the wider design space and failure modes.

## Design stance

`watermark-fortress` deliberately treats watermarking as a **persistent contest**:

- fixed channels are fragile
- per-channel evidence matters
- runtime adaptation is a first-class mechanism
- red-team attack harnesses are part of the product, not an afterthought
