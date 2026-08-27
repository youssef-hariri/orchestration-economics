# A4 Qualitative Analysis — Waves 1+2 (EXPLORATORY)

Amendment A4 | inductive thematic analysis, grounded-theory style (Braun & Clarke 2006;
Charmaz 2006) | explanatory sequential mixed-methods follow-up to the locked interim-2
quantitative results.

- **Coders (open coding, blinded, temperature 0):** deepseek-v4-flash + GLM-5.2
- **Adjudicator (axial synthesis, RQ answers):** meta-llama/Llama-3.3-70B
- **Sample:** Wave 1 n=30 (W1a CTP winners 10, W1b FSN baseline 10, W1c gpt/gemini CTP
  median 10) + Wave 2 n=20 (W2a matched frontier baselines 10, W2b RQ4 persona/no-persona
  twin pairs 10). Total 50 transcripts, 100 open codings, 4 adjudicator calls.
- **Artifacts:** `runs/qual/sample_wave{1,2}.json`, `runs/logs/qual_codes_wave{1,2}.jsonl`,
  `results/qual_themes.json` (all synthesis generations retained for audit).

## 1. Reliability (honestly reported)

### 1.1 Open coding (Waves 1–2)
- Lexical Jaccard of code names between coders: 0.021 per run / 0.021 overall
  (deepseek 528 unique names, zhipu 436, union 944). This is a FLOOR: open coding uses
  free wording, so near-zero lexical overlap is expected and is not by itself evidence of
  disagreement. Semantic convergence is instead assessed at synthesis (both coders
  repeatedly surfaced the same discourse phenomena — metaphors, rhetorical questions,
  staged rollouts, cultural framing — under different labels).

### 1.2 Closed re-coding pass (A4.6) — Cohen's kappa
A 12-item analyst-frozen codebook (4 process themes' subdimensions + key discourse codes,
grounded in Wave 1–2 observations) was applied independently by both coders to all 50
transcripts (temperature 0, blinded). 99/100 codings completed; run 3887/deepseek stayed
unparseable after 6 attempts (long claude winner transcript — output truncation) and is
audited out. Kappa computed on 49 paired transcripts, 588 binary decisions:

- **Pooled Cohen's kappa = 0.774** (percent agreement 89.8%) — above the 0.70 threshold
  required by protocol 02.
- Per-item κ: inductive/exploratory 0.935, reflective opening 1.000, cultural
  contextualization 1.000, staged implementation 0.787, deductive framework 0.766,
  authority citation 0.767, risk quantification 0.741 — all acceptable.
- Below 0.70 (reported, not hidden): conditional logic 0.624, global-local balance 0.656,
  rhetorical questions 0.595, metaphor 0.492, collaborative framing 0.470. These five are
  the subjective style codes; claims relying on them (RQ2's metaphor/collaborative-tone
  claims, RQ3's global-local claim) are downgraded to "moderate-reliability evidence" in
  the paper, per standard practice (Krippendorff recommends caution below 0.667).
- Machine output: `results/qual_kappa.json`; raw: `runs/logs/qual_closed_wave12.jsonl`;
  harness: `code/qual_a4_closed.py`.

## 2. Content-level themes (synthesis v1, 944 codes → 10 themes)

Cultural Adaptation; Communication & Collaboration; Risk Management; Innovation &
Experimentation; Leadership & Governance; Technology & Digitalization; Sustainability &
CSR; Customer-Centricity; Organizational Culture; Talent Management.
Assessment: these are largely PROBLEM-DOMAIN content, not discriminative between
conditions — as expected, since all outputs answer the same business problems.

## 3. Process/style themes (synthesis v2, from discourse-level codes)

1. **Structured Reasoning** — deductive frameworks, dimensional categorization,
   conditional logic, rhetorical questioning as scaffolding.
2. **Exploratory Approach** — philosophical openings, inductive/abductive moves,
   metaphorical framing, external authority citation.
3. **Cultural Sensitivity** — cultural practice references, feedback-style adaptation,
   local translation of vocabulary.
4. **Collaborative Tone** — team-vs-individual focus, explicit authorization of
   empowerment, reframing the core problem.

## 4. Answers to research questions (final synthesis, Waves 1+2, pair-matched)

### RQ1/RQ2 — Why and how do persona-loaded cheap teams beat frontier singles? (confidence: high)
Winning persona-team answers (W1a), on the SAME problems, differ from frontier singles
(W2a) in: exploratory/abductive reasoning; cultural sensitivity and contextualization;
collaborative tone; metaphors, rhetorical questions and speculative framing; more
contextualized, nuanced language. Evidence: runs 3887, 4250 (claude CTP), 2311 (gemini CTP)
against their matched frontier baselines.

### RQ3 — Why kimi/claude yes, gpt/gemini no? (confidence: medium)
kimi/claude winners balance global–local needs, use decentralized governance framings,
and prioritize contextualization. gpt/gemini persona-team non-responders (W1c) instead
lean on explicit communication charters, centralized single-source-of-truth, and
structured decision logging — a mechanistic style that does not convert team structure
into judged quality. Evidence: runs 3887 (claude) vs 1357 (gpt).

### RQ4 — Why do personas raise Novelty but cut Usefulness/Elaboration? (confidence: high)
Persona loading shifts the text toward exploratory/speculative language, metaphors and
rhetorical questions — raising judged novelty — while the added ambiguity and
subjectivity cut practical depth and detail. Evidence: twin pairs, runs 2400 vs 1775,
3435 vs 1776 (kimi). This converges with the pilot-era QUALITATIVE-NOTES finding
(persona → shorter, more indirect style).

## 5. Saturation decision

The adjudicator returned `stop_sampling=false`, but the three themes it flagged as "new"
(exploratory/abductive reasoning; cultural sensitivity/contextualization; decentralized
governance) duplicate or extend Wave-1 themes 2–3. Analyst decision: sampling stopped
after Wave 2 on grounds of redundancy; residual uncertainty documented rather than
hidden. A Wave 3 remains feasible at low cost if the paper needs it.

## 6. Status

EXPLORATORY — informs the paper's discussion only; generates hypotheses for future
pre-registered studies; cannot alter the interim-2 decision (A2 §4 clause extended to
A3/A4). Closed re-coding for κ is DONE (pooled κ = 0.774, §1.2). Remaining optional
hardening: A4.5 deductive verification pass with protocol 02's six themes; sample
extension toward protocol 02's original 176-output target if reviewers require it.
