# DeeWaanAI — Research → Product Feature Map
**Version 1.0 — 2026-08-31 · Evidence base: Studies 1–2, confirmatory wave (OSF), Study 3 (Protocol 13), Study 3 replication (Protocol 16)**
*All findings below are pre-registered, frozen-data results from the orchestration-economics research program (paper v13). This document maps each finding to a platform feature, its user-facing benefit, and its evidence strength — for product, beta-testing, and marketing use.*

---

## 1. Routing & Model Selection

| Research finding | Evidence | Platform feature | User benefit |
|---|---|---|---|
| Cheap solo ≈ 98% frontier quality at 23% of cost (TEGR 6.15) | Replicated (wave, 10 families) | **Default cheap-solo start** for new tasks | Users start at the highest-ROI config automatically |
| Frontier team orchestration destroys value (3.5× cost, ~0 gain) | Replicated (wave W1/W2) | **Guardrail: warn/block frontier-tier teams** | Prevents users paying 3.5× for nothing |
| Family moderation is real but doesn't transport for mid-tier (Protocol 16: 2/5 gates) | Confirmatory, pre-registered | **Benchmark-as-Routing**: cheap per-deployment probe ($0.01–0.73/solution) tests the user's model on their problem type, then routes | Routing decisions based on the user's actual model + task, not a stale lookup table |
| Kimi benefits from pipelines (d = +1.25, replicates); Claude does not (d = −1.90, replicates) | Confirmatory, extremes replicate | **Seeded routing defaults** for probed-similar cases; extremes safe to pre-route | Instant sensible default; probe only where uncertain |

## 2. Pipeline Design (Auto-Designer)

| Research finding | Evidence | Platform feature | User benefit |
|---|---|---|---|
| Design authorship negligible (4/5 families) — cheap models design as well as frontier | Study 3 Contrast A | **Self-design default**: cheap model designs its own pipeline; no frontier design fee | Users save the frontier design pass ($) at zero quality cost |
| Auto-designed > human-designed pipelines (5/5 families); 98.9–100% include feedback loops; 5.3–6.2 steps | Study 3 Contrast B | **Auto-designer as flagship feature** (free roles, up to 7 steps, critic-gated loops) | Better-than-hand-crafted pipelines from problem text alone |
| Kimi designer-stage fragility (22% attrition in Study 3; fixed-prompt robustness varies) | Study 3 + Protocol 16 | **Designer fallback**: template/frontier-authored design fallback for fragile designers | Reliability where the cheap designer fails |

## 3. Refinement

| Research finding | Evidence | Platform feature | User benefit |
|---|---|---|---|
| $0.002 refinement pass recovers up to 64% of the frontier gap — but never beats it | Protocol 09, confirmatory | **One-click refinement pass** with honest framing | Cheap quality lift; marketed as risk mitigation, not frontier replacement |

## 4. Personas

| Research finding | Evidence | Platform feature | User benefit |
|---|---|---|---|
| Persona penalty d = −0.691: personas add cost and degrade quality | Study 1 + wave | **Personas removed as quality default**; kept only as style/tone option, clearly labeled | Users stop paying for a feature that hurts output |

## 5. Quality Communication (Marketing/Beta)

| Research finding | Evidence | Platform feature | User benefit |
|---|---|---|---|
| Orchestration buys *coverage*; frontier wins on *density* | Qual. coding, κ = 0.824 | **Task-type guidance** in onboarding: "completeness → pipeline; concise strategy → frontier solo" | Sets correct expectations; reduces churn from mismatched use |
| All claims trace to pre-registered, frozen-data studies with disclosed failures (W3–W5 fail, R2–R4 fail) | Full program | **Evidence-linked marketing**: every product claim cites its study/gate | Credibility with technical buyers; "we publish our negative results too" |

---

## Messaging rules (from the research discipline itself)
1. **Never claim a static routing table** — Protocol 16 killed it. Say: "we benchmark *your* model on *your* task."
2. **Personas are style, not quality.** Never market them as a quality lever.
3. **Refinement = bounded improvement.** "Recovers most of the gap," never "matches frontier."
4. **Lead with the extremes** (they replicate): cheap-tier substitution ROI, frontier-solo for density.
5. **Disclose the loop**: platform = research instrument; research = product logic. It's a differentiator, not a liability.

*Next review: after any new model family is onboarded (probe-driven, per benchmark-as-routing method).*
