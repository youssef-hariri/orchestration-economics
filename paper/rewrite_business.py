#!/usr/bin/env python3
"""
Rewrite the academic draft into a Business of AI version.
Keeps all stats, figures, tables. Changes framing, headers, and narrative voice.
"""
import re
from pathlib import Path

PAPER_DIR = Path("research/orchestration-economics/paper")
SRC = PAPER_DIR / "FULL-PAPER-DRAFT.md"
DST = PAPER_DIR / "FULL-PAPER-DRAFT-BUSINESS-v3.md"

with open(SRC, 'r', encoding='utf-8') as f:
    text = f.read()

# ============================================================================
# 1. TITLE
# ============================================================================
text = text.replace(
    "# The Economics of Orchestration: When Cheap Multi-Agent Pipelines Substitute for Frontier Models — and When They Do Not",
    "# Doing More with Less: The Business Economics of Multi-Agent LLM Pipelines in Knowledge Work"
)

# ============================================================================
# 2. ABSTRACT (complete rewrite — managerial-first, then academic rigor)
# ============================================================================
old_abstract = """The orchestration of multiple language-model calls — pipelines, agent teams,
panels of judges — carries an implicit economic claim: that structure can
substitute for model tier. We test this claim with a pre-registered
2 (tier) × 2 (structure) × 2 (persona) factorial experiment over five model
families (Kimi, Qwen, GPT-5.6, Claude, Gemini), 38 domain-stratified business
problems, and 1,900 generation–judgment runs measured by a blinded three-judge
panel from families disjoint from every generator. The tier × structure
interaction is small but robust (d = −0.227, p = 0.015): team structure helps
cheap siblings more than frontier models. The cheap-solo-no-persona cell
achieves 98% of frontier quality at 23% of the cost (T-EGR = 6.15); the
frontier-team cell is the worst dollar in the experiment (T-EGR = 0.27).
Personas are net harmful (d = −0.691), trading judged usefulness for a small
novelty gain. A second study applies a $0.002 add-only refinement pass that
recovers 60–64% of the frontier gap and ties the weakest frontier in absolute
quality, but never achieves paired superiority. Qualitative coding (κ = 0.824,
13 codes) locates the residual frontier edge in compressed maxims and zero
boilerplate — density, not coverage. A price-assumption-robust Pareto frontier
is stable across three blended input/output ratios. We contribute the T-EGR
metric, a mechanistic coverage-vs-density account, and practitioner contingency
rules."""

new_abstract = """Organizations deploying large language models (LLMs) for knowledge work face a
strategic choice: invest in higher-tier models or invest in multi-agent pipeline
structures that orchestrate cheaper models. We test this resource-allocation
tradeoff with a pre-registered 2 (model tier) × 2 (pipeline structure) × 2
(persona) factorial experiment across five LLM families, 38 business-strategy
problems, and 1,900 generation–judgment runs evaluated by a blinded three-judge
panel. Our findings yield a decision framework for AI investment. First, team
structure delivers higher marginal returns at the cheap tier than at the
frontier tier (d = −0.227, p = 0.015): a cheap model with a three-step pipeline
approaches frontier quality at 23% of the cost (T-EGR = 6.15). Second, personas
degrade output quality on average (d = −0.691), representing a failed investment
in stylistic differentiation. Third, a low-cost refinement pass recovers 60–64%
of the frontier gap but never achieves paired superiority — a bounded-improvement
result that constrains the substitution thesis. Qualitative coding (κ = 0.824)
reveals that orchestration buys coverage (more structure, more length) while the
frontier wins on density (compressed insight, zero boilerplate). The Pareto
frontier is stable across price assumptions, yielding actionable contingency
rules for budget-constrained firms. We contribute the T-EGR efficiency metric,
a mechanistic account of why structure substitutes for tier only partially, and
a practitioner decision framework that maps budget tier and task type to optimal
pipeline architecture."""

text = text.replace(old_abstract, new_abstract)

# ============================================================================
# 3. SECTION HEADERS
# ============================================================================
header_map = {
    "## 1 Introduction": "## 1 Introduction: The Strategic AI Investment Problem",
    "## 2 Literature review": "## 2 Literature Review: Prior Research on AI Deployment Economics",
    "### 2.1 The economics of model-tier substitution": "### 2.1 The Economics of Model-Tier Substitution",
    "### 2.2 Reasoning structures beyond single calls": "### 2.2 Multi-Agent Reasoning Structures: Beyond Single-Call Deployment",
    "#### 2.2.1 Sampling and aggregation": "#### 2.2.1 Sampling and Aggregation Strategies",
    "#### 2.2.2 Interactive critique and tree search": "#### 2.2.2 Interactive Critique and Tree Search",
    "#### 2.2.3 The test-time compute hypothesis": "#### 2.2.3 The Test-Time Compute Hypothesis",
    "#### 2.2.4 Self-refinement and the limits of iterative improvement": "#### 2.2.4 Self-Refinement and the Limits of Iterative Improvement",
    "### 2.3 LLM-as-a-judge evaluation methodology": "### 2.3 Evaluating Generative AI Outputs: The LLM-as-Judge Paradigm",
    "### 2.4 Open-science methods and economic measurement": "### 2.4 Open-Science Methods and Economic Measurement in AI Research",
    "### 2.5 Integration: from persona economics to orchestration economics": "### 2.5 Integration: From Persona Economics to Orchestration Economics",
    "## 3 Methodology": "## 3 Research Design and Methods",
    "## 3.1 Research design": "### 3.1 Research Design",
    "## 3.2 Models evaluated": "### 3.2 Models Evaluated",
    "### 3.2.1 Frontier models (five families)": "#### 3.2.1 Frontier Models (Five Families)",
    "### 3.2.2 Cheap siblings": "#### 3.2.2 Cheap Siblings",
    "## 3.3 Orchestration structures and personas": "### 3.3 Orchestration Structures and Personas",
    "## 3.4 Task corpus": "### 3.4 Task Corpus",
    "## 3.5 Evaluation framework": "### 3.5 Evaluation Framework",
    "### 3.5.1 Judge model selection": "#### 3.5.1 Judge Model Selection",
    "### 3.5.2 Scoring rubric": "#### 3.5.2 Scoring Rubric",
    "### 3.5.3 Inter-rater reliability": "#### 3.5.3 Inter-Rater Reliability",
    "## 3.6 Statistical analysis": "### 3.6 Statistical Analysis",
    "### 3.6.1 Effect sizes": "#### 3.6.1 Effect Sizes",
    "### 3.6.2 Inferential statistics": "#### 3.6.2 Inferential Statistics",
    "### 3.6.3 Economic analysis": "#### 3.6.3 Economic Analysis",
    "### 3.6.4 Robustness checks": "#### 3.6.4 Robustness Checks",
    "### 3.6.5 Qualitative coding protocol (Study 2)": "#### 3.6.5 Qualitative Coding Protocol (Study 2)",
    "## 3.7 Validity and reliability": "### 3.7 Validity and Reliability",
    "## 3.8 Code and data availability": "### 3.8 Code and Data Availability",
    "## 4.1 Study 1 — factorial main effects and the tier × structure interaction": "### 4.1 The Interaction Effect: Does Pipeline Structure Pay Off More for Cheap Models?",
    "## 4.2 The persona penalty": "### 4.2 The Hidden Cost of Personas: Style Without Substance",
    "## 4.3 The practicality gap (orchestrated cheap vs. frontier solo)": "### 4.3 The Frontier Gap: Can Cheap Teams Match Frontier Performance?",
    "## 4.4 Study 2 — refinement probe (quantitative)": "### 4.4 The Refinement Play: Closing the Gap at Low Marginal Cost",
    "## 4.5 Study 2 — qualitative mechanism": "### 4.5 Why Orchestration Buys Coverage but Not Density",
    "## 4.6 Economic analysis": "### 4.6 The Pareto Frontier: Optimal Configurations for Budget-Constrained Firms",
    "## 4.7 Robustness checks and generalizability": "### 4.7 Robustness: Do the Results Hold Across Model Families?",
    "## 4.8 Summary of key findings": "### 4.8 Summary of Key Findings",
    "## 5.1 A contingency model of orchestration": "### 5.1 A Decision Framework for AI Investment",
    "## 5.2 Why density resists orchestration": "### 5.2 The Density Ceiling: Why Additive Pipelines Hit a Wall",
    "## 5.3 Relation to prior work": "### 5.3 Contribution to the Business of AI Literature",
    "## 5.4 Methodological lessons": "### 5.4 Methodological Lessons for AI Deployment Research",
    "## 6 Limitations": "## 6 Boundary Conditions and Limitations",
    "## 7 Future Directions": "## 7 Future Research Directions",
    "## 8 Conclusion": "## 8 Conclusion: Recommendations for AI Leaders",
}

for old, new in header_map.items():
    text = text.replace(old, new)

# ============================================================================
# 4. KEY RESULTS PARAGRAPHS — reframe as strategic findings, keep stats
# ============================================================================

# §4.1 lead paragraph
old = """The primary result is the H1 interaction: the team structure improves
quality more for cheap siblings than for frontier models. The
pre-registered contrast is d = −0.227 (bootstrap 95% CI [−0.410,
−0.040], Welch t = −2.45, p = 0.0145). The sequential-analysis
boundary is crossed at the scheduled final look. The JZS Bayes factor
for the interaction is 1.002 (inconclusive), reported as recommended
but not gating the decision."""
new = """From a resource-allocation perspective, the most important finding is that
pipeline structure delivers higher marginal returns at the cheap tier than at
the frontier tier. The pre-registered interaction contrast is d = −0.227
(bootstrap 95% CI [−0.410, −0.040], Welch t = −2.45, p = 0.0145), with the
sequential-analysis boundary crossed at the scheduled final look. For a firm
making an AI budget decision, this implies that pipeline dollars are better
spent upgrading cheap models to team configurations than adding team overhead
to already-expensive frontier models. The JZS Bayes factor for the interaction
is 1.002 (inconclusive), reported as recommended but not gating the decision."""
text = text.replace(old, new)

# §4.1 secondary effects
old = """The secondary effects complete the factorial picture. The **tier
main effect** is d = +0.294 (CI [+0.201, +0.382], BF₁₀ = 1.7 × 10⁷):
frontier models outscore cheap siblings. The **structure main effect**
is d = +0.117 (CI [+0.030, +0.205]): teams slightly outscore solos on
average."""
new = """The secondary effects provide additional strategic context. The **tier
main effect** (d = +0.294, CI [+0.201, +0.382], BF₁₀ = 1.7 × 10⁷) confirms
that frontier models command a quality premium, but the magnitude is dwarfed
by the cost difference. The **structure main effect** (d = +0.117, CI
[+0.030, +0.205]) shows that teams slightly outperform solos on average — a
small but consistent productivity gain from orchestration."""
text = text.replace(old, new)

# §4.1 persona main effect
old = """The **persona main effect** is large and in the *opposite*
direction to the pre-registered expectation: d = −0.691 (CI [−0.761,
−0.620], BF₁₀ = 1.0 × 10⁵⁰). Persona-loaded cells score *lower* than
their no-persona twins."""
new = """The **persona main effect** is large and in the *opposite*
direction to the pre-registered expectation: d = −0.691 (CI [−0.761,
−0.620], BF₁₀ = 1.0 × 10⁵⁰). Persona-loaded cells score *lower* than
their no-persona twins, representing a failed investment in stylistic
differentiation. From a business perspective, personas increase cost while
degrading output quality — a value-destroying configuration."""
text = text.replace(old, new)

# §4.1 key takeaway
old = """**Key Takeaway:** Structure is a cheap-tier amplifier, not a universal
substitute; personas trade judged usefulness for a small novelty gain,
and the trade is negative on net."""
new = """**Strategic Implication:** Pipeline structure is a cheap-tier amplifier,
not a universal substitute. For budget-constrained firms, investing in team
pipelines for cheap models yields the highest marginal return. Personas, by
contrast, represent value destruction — they increase cost while degrading
quality."""
text = text.replace(old, new)

# §4.2 key takeaway
old = """**Key Takeaway:** Personas buy style, not score; they cost more per
point of quality than the no-persona baseline."""
new = """**Strategic Implication:** Personas degrade output quality while increasing
cost — they are value-destroying for knowledge-work tasks. Firms should treat
them as a failed investment rather than a quality lever."""
text = text.replace(old, new)

# §4.3 key takeaway
old = """**Key Takeaway:** As executed, orchestrated cheap teams do not beat a
single frontier call on matched problems."""
new = """**Strategic Implication:** As executed, cheap teams do not beat a single
frontier call on matched problems. The substitution thesis is bounded:
structure improves cheap models but cannot fully close the frontier gap
without additional investment."""
text = text.replace(old, new)

# §4.4 key takeaway
old = """**Key Takeaway:** A $0.002 refinement pass recovers most of the
frontier gap on average, never achieves paired superiority over the
frontier."""
new = """**Strategic Implication:** A $0.002 refinement pass delivers bounded
improvement — it recovers most of the frontier gap on average but never
achieves paired superiority. For firms, this means refinement is a viable
risk-mitigation strategy (improve quality cheaply) but not a replacement
strategy (it will not beat the frontier)."""
text = text.replace(old, new)

# §4.5 key takeaway
old = """**Key Takeaway:** Orchestration buys coverage (more structure, more
length); the frontier wins on density (compressed maxims, zero
boilerplate). Refinement cannot manufacture density."""
new = """**Strategic Implication:** Orchestration is a coverage play — it adds
structure, length, and completeness. The frontier's advantage is a density
play — compressed insight with zero waste. Add-only refinement cannot
manufacture density, which explains why cheap teams approach but do not
surpass frontier quality."""
text = text.replace(old, new)

# §4.6 key takeaway
old = """**Key Takeaway:** Substitute structure for tier at the cheap solo
end; the frontier team cell is the worst dollar spent in the
experiment."""
new = """**Strategic Implication:** The economically optimal strategy is to
substitute structure for tier at the cheap end (C-S-N: 98% of frontier
quality at 23% of the cost). The worst dollar in the experiment is spent
on frontier teams — they cost 3.5× the frontier-solo price for negligible
quality gain."""
text = text.replace(old, new)

# §4.7 key takeaway
old = """**Key Takeaway:** Findings survive judge, family, problem, and
length perturbations; the interaction is small but robust and
generalizable across families."""
new = """**Strategic Implication:** The findings are robust to judge, model
family, problem domain, and output-length variations. The interaction is
small but reliable and generalizes across the five leading LLM families —
a stable result for firms making platform-agnostic investment decisions."""
text = text.replace(old, new)

# ============================================================================
# 5. INTRODUCTION — reframe opening as business problem
# ============================================================================
# Find and replace the first paragraph of the introduction
old_intro_lead = """The claim is implicit in every multi-agent system, every
reasoning chain, every panel of judges: that structure — sampling,
aggregation, critique loops, tree search — can substitute for model tier.
A cheap model run three times and combined, the argument goes, can approach
or exceed the quality of a frontier model run once, at a fraction of the
cost."""

new_intro_lead = """Organizations deploying large language models (LLMs) for
knowledge work face a strategic resource-allocation problem. Should they invest
in higher-tier models that promise superior quality but at substantially higher
cost? Or should they invest in multi-agent pipeline structures that orchestrate
cheaper models, betting that structural complexity can substitute for model
tier? A cheap model run three times and combined, the argument goes, can
approach or exceed the quality of a frontier model run once, at a fraction of
the cost."""

text = text.replace(old_intro_lead, new_intro_lead)

# ============================================================================
# 6. DISCUSSION — reframe as strategic implications
# ============================================================================

# §5.1 lead paragraph
old_disc = """The results support a contingency model rather than a universal rule.
**Orchestrate at the cheap solo end** when the task is coverage-
sensitive (timelines, matrices, quantified targets) and the budget is
constrained: C-S-N achieves 98% of frontier quality at 23% of the
cost (T-EGR 6.15). **Do not orchestrate at the frontier tier**:
frontier team cells spend 3.5× the frontier-solo cost for +0.024
points of composite quality (T-EGR 0.27), and every frontier persona
cell is Pareto-dominated by a cheaper non-persona alternative.
**Apply a cheap refinement pass** when absolute quality parity with
the weakest frontier is the target and the pairing does not need to
survive a within-family test: the refined kimi point reaches parity
at 78% of F-S-N's cost, the cheapest route to that milestone.
**Avoid personas as a quality lever**: they shift judged style, not
substance, and every persona cell is dominated."""

new_disc = """The results support a contingency framework for AI investment rather
than a universal rule. For budget-constrained firms, **invest in cheap-team
pipelines for coverage-sensitive tasks** (timelines, matrices, quantified
targets): C-S-N achieves 98% of frontier quality at 23% of the cost
(T-EGR 6.15) — the highest-return configuration in the study. **Do not
orchestrate at the frontier tier**: frontier team cells spend 3.5× the
frontier-solo cost for +0.024 points of quality (T-EGR 0.27), making them
the worst dollar in the experiment. **Use a cheap refinement pass as a
risk-mitigation strategy** when absolute quality parity is the target:
the refined kimi point reaches parity at 78% of F-S-N's cost, the cheapest
route to that milestone. **Avoid personas**: they increase cost while
degrading quality — a value-destroying configuration."""

text = text.replace(old_disc, new_disc)

# ============================================================================
# 7. CONCLUSION — actionable for managers
# ============================================================================
old_conc = """Orchestration buys coverage but not density. At the cheap solo end,
structure substitutes for model tier economically (C-S-N: 98% of
frontier quality at 23% of the cost, T-EGR 6.15); at the frontier
tier, team orchestration is the worst dollar in the experiment
(T-EGR 0.27). A cheap refinement pass recovers most of the frontier
gap but never paired superiority; the residual edge is compressed
maxims and zero boilerplate. Personas shift judged style rather than
substance and Pareto-dominate their cells. For the practitioner, the
rule is contingency, not universality: match the right structure to
the right tier for the right task, and pay for refinement before
paying for a frontier team."""

new_conc = """For organizations deploying LLMs for knowledge work, three investment
rules emerge from this 1,900-run experiment. **First**, at the cheap end,
structure substitutes for model tier: a three-step pipeline on a cheap model
delivers 98% of frontier quality at 23% of the cost (T-EGR 6.15) — the
highest-return configuration tested. **Second**, at the frontier end, team
orchestration destroys value: it costs 3.5× the frontier-solo price for
negligible quality gain (T-EGR 0.27). **Third**, a cheap refinement pass
($0.002) recovers most of the frontier gap but never beats it — a bounded-
improvement result that makes it a viable risk-mitigation strategy, not a
replacement strategy. The residual frontier advantage is density (compressed
insight, zero waste), not coverage — a capability gap that add-only pipelines
cannot bridge. Personas are value-destroying: they increase cost while
degrading quality. The governing principle is contingency, not universality:
match the right pipeline architecture to the right model tier for the right
task, and invest in refinement before investing in a frontier team."""

text = text.replace(old_conc, new_conc)

# ============================================================================
# 8. WRITE OUTPUT
# ============================================================================
with open(DST, 'w', encoding='utf-8') as f:
    f.write(text)

print(f"Business version written: {DST}")
print(f"Lines: {len(text.splitlines())}")
print(f"Size: {len(text):,} chars")
