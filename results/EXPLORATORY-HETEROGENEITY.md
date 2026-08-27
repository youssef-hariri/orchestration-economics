# EXPLORATORY HETEROGENEITY & ROBUSTNESS REPORT (Study-1 re-analysis)

**Date:** 2026-08-22 · **Decision:** DESIGN-DECISIONS D44 · **Trail:** MANIFEST Entry 53
**Status: EXPLORATORY / POST-HOC — NOT pre-registered.** All analyses re-use frozen Study-1 artifacts
(1,900 completed runs; neutral-persona cells C-S-N / C-T-N / F-S-N = 760 analyzed runs). No new API calls.
Any headline use requires confirmation on the reserved out-of-sample set (Fresh_Case_1–10).
Artifacts: `code/exploratory_heterogeneity.py` → `results/exploratory_heterogeneity.json`.

Motivation (session findings that triggered this battery): the team effect is domain-contingent
(marketing +0.004 vs finance −0.106 vs frontier solo) and tracks the family capability gap
(Pearson r = −0.978, Spearman ρ = −1.000 across 5 families).

---

## A1. Reliability and downside risk — do teams reduce variance? (Hansen & Salamon 1990; Brown & Forsythe 1974)

Brown–Forsythe test, team (C-T-N) vs cheap solo (C-S-N) run-level composites, per family:

| Family | SD team | SD solo | p |
|---|---|---|---|
| claude | 0.208 | 0.213 | 0.473 |
| gemini | 0.238 | 0.245 | 0.885 |
| gpt | 0.148 | 0.138 | 0.936 |
| kimi | 0.176 | 0.154 | 0.327 |
| qwen | 0.173 | 0.197 | 0.493 |

**Pooled verdict:** no significant variance reduction by teams overall. The ensemble-variance
hypothesis is NOT supported at the family level.

**Downside risk (pooled):** P(composite < 4.0): C-S-N 2.81% → C-T-N 1.75% → F-S-N 1.05%;
10th percentile: 4.200 / 4.267 / 4.309. Teams halve the cheap-solo bad-output rate but remain
below frontier — a monotone, mild downside improvement.

**Domain-level exception:** in **marketing_communications** team variance is significantly LOWER than
solo (SD 0.127 vs 0.172, Brown–Forsythe p = 0.020). No other domain significant (all p ≥ 0.147).
The domain where teams win on the MEAN (A0 session analysis) is also the domain where they win on
RELIABILITY — convergent evidence that marketing-type tasks are the natural habitat of teams.

## A2. Difficulty moderation (Borenstein et al. 2009)

Team effect per problem (C-T-N − F-S-N) regressed on problem difficulty (mean composite across all
runs), n = 19 problems: Pearson r = +0.153 (p = 0.532), Spearman ρ = +0.105 (p = 0.668).

**Verdict: NULL.** The team effect does not vary with problem difficulty — though the observed
difficulty range is narrow (4.21–4.73; hardest BP28 finance, easiest BP14). A genuine test of the
"structure helps on hard problems" hypothesis needs the fresh-cases wave.

## A3. Length-controlled ANCOVA (Zheng et al. 2023; Dubois et al. 2024; Westfall et al. 2014)

LMM: composite ~ log(tokens) + cell + (1|family) + (1|problem):

| Coefficient | Estimate | p |
|---|---|---|
| Intercept (C-S-N) | 4.232 | <0.001 |
| C-T-N vs C-S-N | −0.018 | 0.400 |
| F-S-N vs C-S-N | **+0.078** | <0.001 |
| log(tokens) | +0.031 | 0.014 |

**Key finding:** raw team-vs-solo advantage is +0.026 (4.531 − 4.505); after controlling log(tokens)
it drops to −0.018 and is non-significant — **the team's measured edge over cheap solo is explained by
output length (verbosity)** (the sign flip from +0.026 to −0.018 lies inside a non-significant
coefficient, p = 0.400 — do not over-read it as a "real negative"). In contrast, the frontier
advantage (+0.081 raw) survives length control essentially intact (+0.078, p < 0.001) —
**the frontier edge is capability, not verbosity**. Judges do reward length (+0.031 per log-token,
p = 0.014), confirming the documented length-bias channel.

**Measurement caveat (binding for reporting):** composite quality is judged on VISIBLE FULL TEXT
(`totalTokensUsed` is the pipeline accounting, not the judged artifact — see D33 artifact lineage).
Team structure mechanically produces longer visible answers (handoffs/elaboration), so length control
partially controls for the mechanism under study. The correct reading is the asymmetry itself:
structure's measured gain rides on produced volume; the frontier tier's gain does not. If a
length-normalized judgment instrument is ever fielded, re-run this contrast.

## A4. Latency economics — the third axis

| Cell | Cost φ=0.5 | Latency | Quality | Quality per $·minute |
|---|---|---|---|---|
| C-S-N | $0.01936 | 47.2 s | 4.505 | **295.8** |
| C-T-N | $0.07340 | 131.7 s | 4.531 | 28.1 |
| F-S-N | $0.08352 | 94.8 s | 4.586 | 34.7 |

All three cells are on the tri-objective (cost, latency, quality) Pareto frontier — no dominated cell.
But: **frontier solo is ~29% FASTER than the cheap team** (94.8 s vs 131.7 s) while also higher quality;
teams buy nothing on the time axis at these concurrency levels, and cheap solo is 8–10× more efficient
on the composite quality-per-$-minute metric. Orchestration's economic case is cost-only, not speed.

## A5. Dimensional decomposition by domain (Holm 1979, 30 tests)

No test survives Holm correction (weak: 3–4 problems/domain). Descriptively, the largest negative
team deltas are ALL on Novelty: product_innovation −0.229, finance −0.221, hr −0.146, strategy −0.136,
operations −0.116. Tentative reading: multi-agent structure **erodes novelty** in analytical domains
while (per session table A0) gaining elaboration/usefulness in communicative ones. Requires fresh-case
replication before any claim.

## A6. Family rank stability across domains (Kendall & Babington Smith 1939)

Kendall's W over family quality rankings across 6 domains:
- **C-T-N (teams): W = 0.922** — family team rankings are nearly invariant across domains
  (kimi > qwen > gpt > gemini > claude holds almost everywhere).
- F-S-N (frontier solo): W = 0.665 — frontier rankings are moderately domain-dependent.

**Reading:** which family's TEAM is best is a property of the family (capability-gap regime), not of
the domain; which frontier model is best shifts somewhat with task type.

## A7. Judge reliability by domain (Shrout & Fleiss 1979; 9 raters = 3 judges × 3 variants)

| Domain | n runs | ICC(3,1) | ICC(3,k=9) |
|---|---|---|---|
| marketing_communications | 159 | 0.523 | 0.908 |
| strategy_market_entry | 120 | 0.522 | 0.908 |
| operations_supply_chain | 120 | 0.509 | 0.903 |
| finance_business_models | 120 | 0.433 | 0.873 |
| product_innovation | 119 | 0.346 | 0.827 |
| hr_organization | 118 | 0.235 | **0.734** |

**Reading:** measurement reliability is itself domain-heterogeneous. The 9-rater composite clears the
0.80 group-level convention everywhere except hr_organization (0.734), where judges disagree most —
domain effects touching HR should be interpreted with extra caution. Single-rater agreement is
moderate (0.24–0.52), consistent with a multi-judge panel design.

---

## Consolidated reading (exploratory)

1. **Teams are NOT more reliable on average** (A1), but they are in marketing — mean win + variance
   win converge on communicative tasks.
2. **The team-vs-cheap-solo measured edge is length-explained; the frontier edge is not** (A3) —
   the sharpest robustness result of the battery and a must-report for reviewers (with the
   A3 measurement caveat: length is partly the mechanism, not only a confound).
3. **Teams lose on latency** (A4); the orchestration case is strictly a cost argument.
4. **Difficulty does not moderate the team effect** within our narrow difficulty band (A2, null).
5. **Team superiority ranks are family-stable across domains** (A6, W = 0.922) — family choice is the
   bigger lever than domain routing of families.
6. **HR judgments are the noisiest measurement channel** (A7).

---

# PART II — PERSONA EXTENSION (D45, Entry 54)

Uses the full 2×2×2 coverage: all 8 cells × 5 families (1,900 runs; cheap-tier
comparisons n = 285/cell, frontier-solo n = 190/cell).

## P1. Do personas raise Cultural Sensitivity?

**No.** Pooled persona effects (P − N, problem-level paired, Holm over 20 tests):
solo-cheap −0.049 (p_holm = 0.98), solo-frontier −0.006 (n.s.), team-cheap −0.043 (n.s.),
team-frontier −0.098 (n.s.). By domain: all 12 cells non-significant (range −0.27 to +0.20).
**Author clarification (2026-08-22):** personas were designed as a general
cultural-perspective injection, NOT specifically to raise this judged dimension — so this is
"no spillover into the judged cultural dimension," not a design failure. (Descriptively the
only positive pockets are finance/operations solo, both n.s.)

## P2. Is the novelty/usefulness trade-off domain-specific?

**For solo, it is uniform; for teams, personas flip sign on novelty.**

| Config | Novelty (every domain) | Usefulness (every domain) |
|---|---|---|
| solo-cheap | **+0.36 to +0.57** in all 6 domains | −0.96 to −1.10 in all 6 domains |
| team-cheap | **−0.08 to −0.35** in all 6 domains | −0.20 to −0.51 in all 6 domains |

Solo personas buy a consistent novelty gain at a consistent usefulness price — no domain
where the trade-off flips. But in TEAMS, personas no longer add novelty (they subtract it
everywhere) while their usefulness cost shrinks ~3×. Structure and persona strongly interact:
the ANCOVA interaction terms (P3) are team×persona = −0.693 on Novelty and +0.711 on
Usefulness (both p < 0.001). Teams squash the persona novelty gain while rescuing most of
the usefulness loss — i.e., under a team, personas have no upside left.

## P3. Length-controlled persona ANCOVA (cheap tier, LMM with structure × persona)

| Term | Composite | Novelty | Usefulness | Cultural Sens. |
|---|---|---|---|---|
| persona main | −0.250*** | **+0.465*** | −0.984*** | −0.031 n.s. |
| team × persona | +0.061* | −0.693*** | +0.711*** | −0.006 n.s. |

**The persona novelty gain survives length control intact (+0.465, p < 0.001)** — unlike the
team edge (A3), the persona effect is a genuine stylistic/cognitive effect, not verbosity.
The composite persona penalty also survives (−0.250). Cultural Sensitivity remains a null.

## P4. Judge reliability: neutral vs persona answers (Shrout & Fleiss ICC)

| Condition | n runs | ICC(3,1) | ICC(3,9) |
|---|---|---|---|
| neutral | 946 | 0.555 | 0.918 |
| persona | 946 | **0.608** | **0.933** |

Persona answers do NOT split the panel — judge agreement is slightly HIGHER on stylized
answers. Persona findings are not measured noisier.

## P5. Persona effect on variance (Brown–Forsythe)

Personas roughly DOUBLE outcome variance (all p ≈ 0): solo SD 0.232 → 0.397; team SD
0.211 → 0.348; significant in every domain (SD jumps of +0.15 to +0.22). Personas are a
high-variance injector: more spread in both directions, less predictable output quality.

## Persona consolidated reading (exploratory)

1. **Personas produce no spillover into judged Cultural Sensitivity** (P1) — and per author
   clarification they were not designed solely for it; they are a perspective injection,
   whose measurable footprint is novelty, not this dimension.
2. **The persona novelty gain is real** — survives length control (+0.465***), uniform across
   domains — **but exists only in solo pipelines** (P2/P3).
3. **Teams neutralize personas' only upside** and cut their usefulness cost — persona+team
   is dominated by neutral team on novelty, usefulness, and composite alike.
4. **Personas double output variance** (P5) — a reliability tax on top of the usefulness cost.
5. Judges handle stylized answers fine (P4), so these results are not a measurement artifact.
6. **Practical rule emerging:** if novelty is the goal, use persona + cheap SOLO and accept
   the usefulness hit + variance; never combine personas with teams; and don't deploy
   personas expecting cultural sensitivity.

## Limitations & reporting obligations

- Exploratory, post-data-contact; label as such in the paper (D44 binding clause; Nosek et al. 2018).
- A5/A2 underpowered (3–4 problems/domain; 19 problems); A6 W is descriptive at 6 domains.
- Confirmatory replication reserved for Fresh_Case_1–10 (pre-registered out-of-sample set).
