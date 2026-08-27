# Protocol-12 Confirmatory Replication Wave — Results Report

**Date:** 2026-08-24 · **Pre-registration:** OSF jg49x · **Protocol:** `DeeWaanAI-Next/protocols/12-PROTOCOL-WAVE-CONFIRMATORY-REPLICATION.md`
**Frozen analysis script:** `code/analyze_wave.py` (sha256 `94729d02…f5da8f9a`, untouched) · **Executed via:** disclosed wrapper `code/run_wave_analysis.py` (D52)
**Results artifacts:** `results/wave_analysis.json` (primary price vector) · `results/wave_analysis_minimax_promo.json` (D46 sensitivity)

---

## 1. Headline

| Gate | Test | Result | Verdict |
|---|---|---|---|
| W1 | Pooled team effect (C-S-N → C-T-N), LMM | coef **+0.0167**, p = 0.00647 | **PASS** |
| W2 | Upgrade threshold (C-T-N → F-S-N), LMM | coef **+0.0912**, p < 0.0001 | **PASS** |
| W3 | Domain contingency (3a interaction + 3b directional) | χ² = −45.5, p = 1.0 · signs 5/6 | **FAIL** |
| W4 | Capability-gap mechanism (family-level r) | r = −0.2445, p = 0.526 | **FAIL** |
| W5 | Marketing variance advantage (Brown–Forsythe) | p = 0.990, sd_team > sd_solo | **FAIL** |
| W6 | Economics (quality/$·min, T-EGR, Pareto) | F-S-N 47.3 > C-T-N 18.7; T-EGR(C-S-N) = 3.92 | **PASS** |
| W7 | Judge reliability ICC(3,1) by domain (audit, no gate) | 0.480 – 0.629 (ICC(3,k) 0.892–0.939) | — |

**Upgrade-gate consequence (binding, Protocol 12 §1):** the three Study-1 EXPLORATORY findings put through the gate — domain contingency, the capability-gap mechanism (Study-1 r = −0.978), and the marketing variance advantage — all FAIL their pre-registered confirmatory tests and **remain labeled exploratory** in the paper. The core claims (team effect exists but is small; frontier solo beats cheap teams on quality; cheap solo dominates on cost-efficiency) **replicate out-of-sample** on fresh problems and an expanded family universe.

This is exactly the outcome a pre-registered gate exists to produce: the exploratory battery did not survive contact with new data, and no post-hoc relabeling is permitted in either direction (D47).

## 2. Data base

- **Stimuli:** 30 fresh problems (6 domains × 5; Fresh_Case set, zero Study-1 overlap, D49).
- **Design:** 9 generator families × 3 cells (C-S-N, C-T-N, F-S-N), cheap reps 3 / frontier reps 2.
- **Judging:** frozen panel (deepseek-chat, zai-org/GLM-5.2, Llama-3.3-70B) × 3 verbatim variants, blind, temp 0 → 9 scores per run; composite = mean of 9 × 5 dimension scores. 18,450/18,450 unique judge keys completed (4 resumable passes; transient DNS/402 errors backfilled).
- **Analyzed n:** 2,050 judged runs across 9 families.

### Completion shortfalls (disclosed per Protocol §5.4 / §7)

| Family | Planned | Judged | Status |
|---|---|---|---|
| claude, gpt, gpt-oss, gemma, mistral, qwen, thinkingmachines | 240 each | 240 each | complete |
| minimax | 240 | 236 | 9 F-S-N quarantined (single-think-block outputs) and re-run; 5 re-runs netted short of plan after empty-content losses; remainder disclosed |
| kimi | 240 | 134 | Moonshot credit exhaustion mid-wave (Entry 62); 6 empty F-S-N pending; remainder deferred until top-up |
| gemini | 240 | 0 | provider-side outage regime all window (throttled → tok=0 even at c=1 probe); deferred to next window, probe-first re-admission (Entry 61) |

Shortfalls are provider force majeure, not analytic exclusions. W4 still had 9 families with all three cells present and ran at full power (n = 9 ≥ 8 minimum; power for ρ = 0.80 at n = 9 is 0.768). No imputation was performed; gemini contributions are missing-by-provider.

## 3. Gate details

### W1 — pooled team effect (PASS)
LMM `comp ~ cell` (reference C-S-N), cells C-S-N/C-T-N, n = 1,550, groups = family. C-T-N coefficient **+0.0167** (p = 0.00647). Direction, significance, and small magnitude all replicate Study-1: cheap teams beat cheap solo, but the margin is modest on the composite.

### W2 — upgrade threshold (PASS)
Same LMM, cells C-T-N/F-S-N, n = 1,272, reference C-T-N. F-S-N coefficient **+0.0912** (p < 0.0001) — ~5.5× the team effect. Frontier solo remains decisively better than cheap teams on quality out-of-sample; the "when to upgrade" claim holds.

### W3 — domain contingency (FAIL)
- **3a (interaction):** LMM `comp ~ logtok + cell*domain` vs reduced (no interaction), LRT. χ² = **−45.506** (negative), p = 1.0 → FAIL. A negative REML-LRT statistic here reflects the numerical-fallback RE structure (see §5): the reduced model's single variance component absorbed dispersion the full model split across terms; REML log-likelihoods under differing RE structures are not strictly comparable. The interaction provides no evidence of improvement, which is the conservative reading anyway.
- **3b (directional):** per-domain C-T-N − F-S-N with Holm correction: signs matched Study-1 in **5/6** domains, but the pre-registered gate required ≥ 4 matches AND marketing as strongest positive AND finance as strongest negative. **Marketing flipped sign** (Δ = −0.0830, Holm p = 0.0063, vs Study-1 +0.0037): on fresh problems, frontier solo beat cheap teams in marketing too. Finance was the strongest negative as predicted (Δ = −0.1204), but with NO positive domain, the conjunctive gate fails.
- Per-domain effects (all negative = frontier solo wins everywhere): finance −0.1204 (p_holm 0.097), hr −0.0992 (0.002), marketing −0.0830 (0.006), operations −0.0815 (0.097), product −0.0392 (0.216), strategy −0.0928 (0.147).

**Interpretation:** Study-1's "marketing is the domain where cheap teams rival frontier solo" was a sample-specific fluctuation. The wave shows a uniform frontier advantage across domains. Domain contingency stays exploratory and must be labeled as such.

### W4 — capability-gap mechanism (FAIL)
9 complete families (≥ 8 required). Family-level capability gap (F-S-N − C-S-N mean composite) vs team effect (C-T-N − C-S-N): Pearson r = **−0.2445** (p = 0.526), Spearman ρ = −0.0333 (p = 0.932), against Study-1's r = −0.978 (n = 5). The mechanism does not replicate; the Study-1 correlation was almost certainly an n = 5 artifact. Power caveat: n = 9 detects ρ = 0.80 at 76.8% — an effect anywhere near the Study-1 magnitude would very likely have been seen; the true effect, if any, is small.

### W5 — marketing variance advantage (FAIL)
Brown–Forsythe (marketing, C-T-N vs C-S-N): p = 0.990, sd_team = 0.290 vs sd_solo = 0.274 — no variance reduction, direction reversed. Pooled across domains: p = 0.752 (reported without gate). The "teams reduce downside variance" story does not replicate; downside rates (< 4.0) are near-identical across cells in every domain.

### W6 — economics (PASS)
Primary price vector (D23 list prices, PHI = 0.5 blend):

| Cell | Cost/run | Latency | Quality | Quality/$·min | T-EGR vs F-S-N |
|---|---|---|---|---|---|
| C-S-N | $0.01541 | 85 s | 4.4714 | 204.7 | **3.918** |
| C-T-N | $0.06575 | 219 s | 4.4870 | 18.7 | 0.922 |
| F-S-N | $0.06176 | 94 s | 4.5733 | 47.3 | 1.000 |

Pareto frontier (cost, latency, quality): **{C-S-N, F-S-N}** — C-T-N is dominated: it costs as much as frontier solo, takes 2.3× longer, and lands 0.086 composite points lower. Gate condition (F-S-N quality/$·min > C-T-N's AND F-S-N on Pareto) holds. The economic ordering replicates exactly: cheap solo for volume economics, frontier solo for quality, and cheap multi-agent teams are the dominated middle on fresh problems.

**Sensitivity (D46 minimax promo vector):** all gates unchanged; W6 costs shift to $0.01485 / $0.06275 / $0.06042, T-EGR 3.978 / 0.945, Pareto unchanged. Conclusions are robust to the minimax pricing scenario.

### W7 — judge reliability (audit)
ICC(3,1) by domain across the 9-rater composite matrix: marketing 0.480, hr 0.544, finance 0.557, operations 0.595, strategy 0.602, product 0.629; ICC(3,k) (panel mean) 0.892–0.939. Single-rater agreement is moderate, panel-mean reliability high — same regime as Study-1, supporting the use of 9-score composites.

## 4. What this means for the paper

1. **Headline claims (confirmed, out-of-sample):** (i) cheap multi-agent teams produce a small but real quality gain over cheap solo (+0.017); (ii) frontier solo beats cheap teams decisively on quality (+0.091); (iii) the cost-quality frontier is bimodal — cheap solo (T-EGR ≈ 3.9) and frontier solo — with cheap teams dominated at current list prices.
2. **Demoted to exploratory (failed the gate):** domain contingency (marketing exception), capability-gap correlation, marketing variance advantage. Per the binding upgrade rule these may appear only in an exploratory section with the gate failure reported alongside.
3. **Honest framing:** the wave increased evidential value precisely by failing the exploratory gates; reporting the failures is the contribution (OSC 2015; Camerer et al. 2018).

## 5. Deviations and disclosures (complete list)

1. **LMM numerical fallback (D52).** The pre-registered dual variance-component RE structure was numerically singular on the imbalanced panel (`LinAlgError` at the first fit). A disclosed runtime wrapper (`code/run_wave_analysis.py`, sha256 embedded in the outputs) substituted a cross-validated single-vc (problem) structure under a pre-declared rule: both single-vc fits must converge with bit-identical fixed effects (rtol 1e-6; observed identical to 16 digits), sticky for all four LMM calls. The frozen script was not modified. Fixed-effect specifications, alphas, and gate directions were unchanged. The W3a negative χ² is disclosed alongside the REML comparability caveat. Grounding: Nosek et al. 2018 (disclosed deviation); Bates et al. 2015 (doi:10.18637/jss.v067.i01); Matuschek et al. 2017 (doi:10.1016/j.jml.2017.01.001).
2. **Provider shortfalls:** gemini 0/240 (outage, deferred, probe-first re-admission); kimi 134/240 (credit exhaustion; author policy: continue other families); minimax 236/240. Entries 61–62.
3. **Instrumentation near-miss (Entry 63):** the reasoning-strip regex was saved empty by tooling; caught and rebuilt from string parts BEFORE any judge call; no judged text was altered.
4. **Quarantines/re-runs:** 9 minimax single-think-block F-S-N outputs quarantined and re-run (runIds 7157–7165); 5 claude empty frontier responses recovered (7152–7156); 6 kimi F-S-N remain empty-pending.
5. **Judging backfill:** 4 resumable passes; 27 orphan judgments map to quarantined runIds and join to nothing (excluded from analysis automatically).
6. **W4 ran despite kimi imbalance:** kimi's 3 cells were all present (58/52/24 judged), satisfying the pre-registered "complete family" definition; the imbalance is disclosed here rather than excluding kimi post-hoc.

## 6. Deferred items (next window)

- **gemini lane (240 runs):** probe at c=1 first; on success ramp at low cap; judge incrementally (judge_v2.py resumes).
- **kimi lane (100 runs + 6 empties):** after Moonshot top-up; same Moonshot-direct routing to preserve within-family homogeneity (Together migration rejected, Entry 62).
- After backfill, re-run the wrapper; gate outcomes are expected to be stable (current verdicts rest on 9 complete families), and any change will be reported as an update, not a silent revision.

## 7. Reproducibility pointer

```bash
cd research/orchestration-economics
/usr/local/bin/python3 code/run_wave_analysis.py          # primary
/usr/local/bin/python3 code/run_wave_analysis.py --promo  # D46 sensitivity
```
Inputs: `runs/logs/wave_run_ledger.json` + `runs/logs/wave_judgments.jsonl` + `data/problems/fresh_domain_map_wave.json` + `config/price_vector*.json` + `config/model_registry.json`. All artifacts committed; frozen scripts byte-identical to their pre-judging hashes.

---

# UPDATE 2026-08-28 — Wave completed to 2,400/2,400 (all 10 families); gates re-run; pattern unchanged

This is an **update**, not a revision: the 2026-08-24 report above stands as the record of the
9-family interim analysis; this section reports the completed panel per Protocol 12 §6
("any change will be reported as an update"). Frozen `analyze_wave.py` untouched; executed via
the same disclosed D52 wrapper.

## U1. What changed since 2026-08-24

- **gemini 0/240 → 240/240.** The "provider outage" was diagnosed as the free-tier daily cap
  (429 `generate_requests_per_model_per_day`, limit 150/model/day); resolved by the author's
  Google billing upgrade. Probe-first re-admission per the Entry-61 rule (Fresh_Case_3 at c=1,
  8/8 clean), then the remainder at c=10: 232/232, zero throttled.
- **kimi 134/240 → 240/240.** Moonshot recharge restored the cheap cells (Moonshot-direct,
  homogeneity preserved). **Author-directed routing deviation (D53):** kimi F-S-N completed via
  Together serverless `moonshotai/Kimi-K3` (pipeline 73), superseding the Entry-62 deferral;
  same pinned model version and parameters; the 30 F-S-N runs from 08-23 remain Moonshot-direct;
  route membership is auditable per run in the ledger.
- **Judging:** resumed to **0 pending** (21,762 unique keys; 27 quarantine orphans join to
  nothing). Two disclosed infrastructure events: a local Python SSL/cert failure (no scores
  recorded; relaunched under the managed runtime) and a Together 402 credit-exhaustion mid-pass
  (author recharged; 402 calls never record; backfilled by resume).
- **Analyzed n: 2,418 judged runs, 10/10 families with all three cells present.**

## U2. Gate outcomes on the complete panel (primary price vector, α = 0.05)

| Gate | Interim (9 families, 2026-08-24) | Complete (10 families, 2026-08-28) | Verdict |
|---|---|---|---|
| W1 team effect | +0.0167, p = 0.006 | **+0.0168, p = 0.00217** | PASS (unchanged) |
| W2 upgrade threshold | +0.0912, p < 0.0001 | **+0.0745, p < 0.0001** | PASS (unchanged) |
| W3 domain contingency | χ² = −45.5, signs 5/6 | χ² = −47.5, p = 1.0; signs 5/6; still no positive domain | FAIL (unchanged) |
| W4 capability-gap | r = −0.2445 (n = 9) | **r = −0.2141, p = 0.553; ρ = −0.067 (n = 10)**; power for ρ = 0.80 now 0.828 | FAIL (unchanged) |
| W5 marketing variance | p = 0.990, reversed | p = 0.795, sd_team 0.2722 > sd_solo 0.2626; pooled p = 0.618 | FAIL (unchanged) |
| W6 economics | T-EGR 3.918/0.922; Pareto {C-S-N, F-S-N} | C-S-N $0.0145/4.479/231.9 · C-T-N $0.0616/4.496/21.2 · F-S-N $0.0599/4.575/40.6; T-EGR **4.044/0.956**; Pareto {C-S-N, F-S-N} | PASS (unchanged) |
| W7 judge ICC(3,1) | 0.480–0.629 | 0.471–0.622 | audit (unchanged regime) |

**Upgrade-gate consequence (binding, unchanged):** the three Study-1 exploratory findings
(domain contingency, capability-gap mechanism, marketing variance advantage) REMAIN EXPLORATORY.
The core claims — small real team effect, decisive frontier-solo quality advantage, bimodal
cost-quality frontier with cheap teams as the dominated middle — now replicate out-of-sample on
the FULL pre-registered family universe (10/10) and stimulus set (30/30).

**Sensitivity (D46 promo vector):** gate pattern identical; T-EGR 4.11/0.98; Pareto unchanged.

## U3. Additional disclosures

1. The D52 LMM fallback fired on all 4 calls again — now on a BALANCED panel, showing the
   dual-vc singularity is structural to this design (imbalance was not the sole cause). Per-call
   disclosure in `lmm_numerical_fallback_disclosure` of both results JSONs; W3a's negative
   χ² carries the same REML comparability caveat.
2. kimi F-S-N empties (platform content loss, tok≈9–10k len=0, both routes) recovered over five
   resume passes; final run 2026-08-28 (runId 7631). No scored output was ever empty.
3. W2's point estimate moved +0.0912 → +0.0745 with gemini (a large-gap family) added and kimi
   completed — reported as the updated estimate; the interim value remains quoted in §3 as the
   9-family record.
