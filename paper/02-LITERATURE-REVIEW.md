# 2 Literature Review — draft v3 enhanced (2026-08-07)

> Scope rule: this section cites ONLY references from the DOI-verified
> register (PAPER-STRUCTURE.md). Author-year citation style follows the
> author's published papers. All DOIs listed at the end of this file.

---

This review synthesizes four streams of research: (i) measured productivity
effects of generative AI, (ii) multi-agent and ensemble generation methods,
(iii) LLM-as-a-judge evaluation methodology, and (iv) open-science methods
for economic measurement. We then integrate these streams with our own prior
work on personas and efficiency metrics to articulate the research gap that
motivates this study.

## 2.1 Productivity effects of generative AI

### 2.1.1 Measured gains in knowledge work

Three controlled studies establish that generative AI raises knowledge-work
productivity, but they also reveal that the gains are conditional and
bounded. Noy and Zhang (2023) randomized 444 mid-level professionals to
ChatGPT-assisted and control arms on professional writing tasks: assistance
reduced completion time by 0.8 standard deviations and raised output quality
by 0.4 standard deviations, with the largest quality gains among initially
lower-performing workers — a compression of the performance distribution.
Brynjolfsson, Li, and Raymond (2023) observed 5,179 customer-support agents
using a generative assistant in the field and found a 14% average
productivity increase, concentrated among novice and low-skilled workers
(+34%), consistent with the model diffusing behaviors of high-ability agents
across the workforce.

A critical limitation unites these studies: both treat the model as a
*given, single-agent capability*. The unit of analysis is one model call,
not an orchestrated system. The professional-writing and customer-support
tasks they study are also relatively closed-form: the desired output is
well-specified (a support response, a draft document), and quality can be
partially verified against ground truth. Open-ended strategic tasks — the
domain of this paper — have no verifiable correct answer, which changes both
the nature of the "frontier" and the applicability of the productivity
gains documented above.

### 2.1.2 The jagged frontier and its boundary

The boundary of these gains is the central caution. Dell'Acqua et al.
(2023) ran a field experiment with 758 consultants on realistic professional
problems and documented a "jagged technological frontier": inside the model's
capability boundary, consultants completed 12.2% more tasks, 25.1% faster,
with 40% higher quality; outside it, consultants using the model were 19
percentage points less likely to produce correct solutions than controls.
Two productive behavioral strategies emerged ("centaurs" dividing work at
the boundary, "cyborgs" interleaving with the model), but neither changed
the location of the boundary itself.

The jagged frontier concept is especially consequential for open-ended tasks.
In closed-form domains (arithmetic, code, support scripts), the boundary is
sharp: a solution is either correct or not. In open-ended business strategy,
the boundary is diffuse — there is no single correct answer, only better or
worse responses. This diffuseness creates a fundamental ambiguity: when a
cheap model produces a plausible but suboptimal strategy, the user may not
know they are "outside the frontier" until the solution fails in deployment.
The open question this paper addresses is whether *orchestration structure*
can shift the effective capability frontier for these open-ended tasks —
and at what cost.

## 2.2 Multi-agent systems, reasoning, and inference-time compute

### 2.2.1 From chain-of-thought to structured reasoning

The modern reasoning literature begins with the observation that language
models solve complex problems better when they generate intermediate
reasoning steps. Wei et al. (2022) introduced chain-of-thought (CoT)
prompting: appending exemplars that show step-by-step reasoning before the
final answer elicited comparable reasoning in the model, dramatically
improving performance on arithmetic, commonsense, and symbolic reasoning
tasks. The CoT paradigm reframed language-model inference from
single-shot generation to *structured multi-step deliberation* — a
conceptual shift that enabled the orchestration methods reviewed below.

CoT's direct descendant in the accuracy–cost tradeoff space is
self-consistency. Wang et al. (2023) showed that sampling a diversity of
reasoning paths from a single model and taking a majority vote over final
answers improves arithmetic, commonsense, and symbolic reasoning well beyond
CoT decoding alone. The result establishes the general principle that
parallel sampled calls can be converted into accuracy. Its direct corollary
— that accuracy is bought at a multiplicative cost in calls and tokens —
is rarely priced against the alternative of a single stronger model.

### 2.2.2 Interactive deliberation: debate, tree search, and agent loops

Moving beyond independent sampling, recent work has explored *interactive*
structures in which model instances influence each other. Liang et al.
(2024) showed that multiple LLM instances proposing answers, critiquing each
other's responses, and refining their own over debate rounds improves
factuality and reasoning on arithmetic and knowledge benchmarks, encourages
divergent thinking, and reliably converges to shared answers. Yao et al.
(2023a) extended the reasoning structure from linear chains to branching
trees: Tree of Thoughts treats each reasoning step as a node in a search
graph, allowing the model to explore multiple reasoning paths, backtrack
from dead ends, and select the most promising branch — deliberate problem
solving rather than single-path generation.

These works demonstrate that structure (sampling, aggregation, critique
loops, tree search) adds quality beyond a single call. What they do not
provide is a cost-matched factorial comparison: prior multi-agent studies
report quality gains without measuring dollars, and without comparing
orchestrated cheap models against an un-orchestrated frontier model on
identical problems. The substitution claim — that structure can stand in
for model tier — is therefore assumed, not tested.

### 2.2.3 The test-time compute hypothesis

A nascent theoretical framework reframes the model-tier-versus-structure
tradeoff as an allocation problem. Snell et al. (2024) demonstrated that
scaling inference-time computation (more tokens, verifier-based search,
iterative refinement) can be more effective than scaling model parameters
for improving performance on reasoning benchmarks. Their compute-optimal
curve predicts that for any fixed problem difficulty, there exists an
optimal allocation between training compute (model size) and inference
compute (test-time search). Below that optimum, a smaller model with more
inference compute outperforms a larger model with less; above it, the
larger model wins.

This framework is the closest theoretical grounding for the "orchestration
economics" claim, but it remains limited in three ways that motivate our
study. First, Snell et al. measure *verifiable* reasoning tasks (math,
code) where a verifier can score intermediate steps; open-ended business
strategy has no verifier. Second, their test-time compute is
*search-based* (sampling + scoring), whereas the multi-agent literature
uses *structural* compute (builder-critic-refiner pipelines, debate rounds)
— the two may have different cost-quality curves. Third, and most
fundamentally, their analysis is in units of FLOPs, not dollars: the
practitioner facing an API bill cannot spend FLOPs. A dollar-matched
empirical test is missing.

### 2.2.4 Self-refinement and the limits of iterative improvement

The final reasoning structure relevant to this study is self-refinement:
a model critiquing and revising its own output. Shinn et al. (2023)
introduced Reflexion, in which a language agent maintains a reflective
memory of past failures and uses verbal reinforcement learning to improve
subsequent trials. On coding and decision-making tasks, Reflexion
outperformed single-shot baselines and even standard CoT by learning from
its own errors.

Self-refinement raises a hypothesis directly tested in our Study 2: if a
cheap model's initial output is below the frontier, can a cheap refinement
pass close the gap? The multi-agent and self-refinement literatures imply
that iterative improvement should raise quality. But they do not tell us
whether the improvement is sufficient to reach parity with a frontier model
that was not itself refined — the marginal comparison that determines
substitution. Nor do they tell us *why* refinement succeeds or fails on
open-ended tasks. Our qualitative coding protocol (Section 3.6.5) is
designed to answer this mechanistic question.

## 2.3 LLM-as-a-judge evaluation methodology

Because our outcomes are open-ended business solutions, evaluation itself is
a design object. Zheng et al. (2023) established LLM-as-a-judge as a
scalable evaluation paradigm, showing strong agreement between strong judge
models and human preferences on pairwise comparison tasks, while documenting
three systematic biases that threaten validity: position bias (preferring
the candidate presented first), verbosity bias (preferring longer outputs),
and self-enhancement bias (preferring outputs from the same model family as
the judge). Their mitigations — swapping candidate order, controlled
few-shot examples, length normalization — inform our blinding and
order-shuffling protocol.

The self-enhancement bias is particularly acute for multi-agent studies. If
the generator and judge share model architecture, the judge may reward the
generator's stylistic conventions rather than substantive quality. Verga et
al. (2024) extended the single-judge design into a jury: a Panel of LLM
evaluators (PoLL) composed of several smaller models from different families
correlated better with human judgments than a single large judge, at lower
cost, while mitigating the self-preference bias that afflicts same-family
evaluation. Our evaluation framework inherits this logic directly: three
judges from families disjoint from all generators, each under three frozen
prompt variants, scoring blind to cell and family. This design is especially
important for detecting the "persona penalty" hypothesized in this study —
a stylistic shift that a same-family judge might reward while a
disjoint-family jury penalizes.

## 2.4 Open-science methods and economic measurement

The fourth stream supplies the discipline this paper applies. Nosek et al.
(2018) argue that preregistration distinguishes confirmatory from
exploratory analysis, converting transparency into credibility; our ten
protocols and their amendments were all registered before the corresponding
computations ran. Steegen et al. (2016) show that conclusions can vary
across reasonable analytic choices and recommend reporting a multiverse of
analyses; our price-assumption panel (three blended input/output ratios)
and pre-registered robustness battery implement this idea. Sandve et al.
(2013) codify reproducible computational research — versioned scripts,
recorded steps, stable environments — which our token ledger and frozen
configuration files follow.

Two statistical practices complete the foundation. Albers and Lakens
(2018) demonstrate that effect sizes estimated from pilots are unstable and
bias follow-up power analyses, so pilot data must never anchor confirmatory
claims; accordingly, our pilot informed only feasibility gates (G1/G2), never
the main analysis. Lakens (2013) makes the case for reporting effect sizes
with confidence intervals to support cumulative science; we report Welch's d
with bootstrap intervals throughout. Cohen's (1960) κ coefficient provides
our inter-rater and coder-agreement metric.

Finally, measuring the economics of inference requires separating quantity
from price. Diewert (1976) formalized the decomposition of value changes
into price and quantity components in index-number theory; we apply the same
logic by storing tokens (quantity) and multiplying by a frozen price vector,
so every reported dollar is reproducible and re-priceable. Tomlinson et al.
(2024) quantify the environmental footprint of generative tasks, reinforcing
that inference cost — economic and environmental — is a first-order design
variable rather than an implementation detail.

## 2.5 Integration: from persona economics to orchestration economics

Our own prior work supplies the immediate empirical background. In a
cross-architecture evaluation of cultural personas across seven large
language models, persona effectiveness followed a contingency model rather
than a universal rule, and the Efficiency Gain Ratio (EGR) showed that small
models with personas achieved superior performance at 40–88% lower cost
(Hariri, 2026b). The same line of work measured creativity with multi-judge
panels over thousands of generated business solutions, establishing
Novelty as the best-agreed creativity dimension (Hariri, 2025a), and showed
that team composition effects are contingent on task verifiability
(Hariri, 2025b).

Integrating the four streams above with this lineage yields a precise gap
and three pre-registered hypotheses, each grounded in the literature:

**Substitution hypothesis (H1):** The test-time compute framework (Snell et
al., 2024) predicts that structure can substitute for model tier at the
cheap end of the compute-optimal curve. We test this prediction with a
factorial tier × structure design, priced in dollars, on open-ended tasks
where no verifier exists. If the hypothesis holds, cheap teams should
approach frontier-solo quality at a fraction of the cost.

**Persona hypothesis (H2):** Our prior work (Hariri, 2026b) showed that
cultural personas shift quality within single-model cells. We extend this
to teams: if personas amplify structural rigor, the persona effect should be
larger for team structures than for solo structures. If personas primarily
add stylistic variation without substance, the persona-loaded cells should
be Pareto-dominated by their no-persona twins.

**Refinement hypothesis (H3):** The self-refinement literature (Shinn et
al., 2023) suggests that a cheap critique-and-revise pass can recover
quality gaps. We test whether a frozen, add-only refiner can close the
residual gap between orchestrated cheap outputs and frontier outputs — and
whether the mechanism is additive coverage (more structure) or compressed
insight (better density).

The experiment in Section 3 tests all three hypotheses, priced. The
qualitative coding protocol (Section 3.6.5) is designed to distinguish the
two mechanisms implied by H3: "orchestration buys coverage, the frontier
wins on density" is the falsifiable prediction derived from the literature
review above.

---

## References (all DOI-verified 2026-08-07)

- Albers, C., & Lakens, D. (2018). When power analyses based on pilot data
  are biased: Inaccurate effect size estimators and follow-up bias.
  *Journal of Experimental Social Psychology*, 74, 187–195.
  DOI: 10.1016/j.jesp.2017.09.004
- Brynjolfsson, E., Li, D., & Raymond, L. R. (2023). *Generative AI at Work*
  (NBER Working Paper No. 31161). DOI: 10.3386/w31161
- Cohen, J. (1960). A coefficient of agreement for nominal scales.
  *Educational and Psychological Measurement*, 20(1), 37–46.
  DOI: 10.1177/001316446002000104
- Dell'Acqua, F., McFowland III, E., Mollick, E. R., Lifshitz-Assaf, H.,
  Kellogg, K., Rajendran, S., Krayer, L., Candelon, F., & Lakhani, K. R.
  (2023). *Navigating the jagged technological frontier: Field experimental
  evidence of the effects of AI on knowledge worker productivity and quality*
  (HBS Working Paper No. 24-013). DOI: 10.2139/ssrn.4573321
- Diewert, W. E. (1976). Exact and superlative index numbers. *Journal of
  Econometrics*, 4(2), 115–145. DOI: 10.1016/0304-4076(76)90009-9
- Hariri, Y. (2025a). *LLM-Creativity* [dataset and paper]. Zenodo.
  DOI: 10.5281/zenodo.17407392
- Hariri, Y. (2025b). *LLM Team Composition Paradox* [dataset and paper].
  Zenodo. DOI: 10.5281/zenodo.17490945
- Hariri, Y. (2026b). *Doing More with Less: How Cultural Personas Bridge the
  Cost-Performance Gap in LLMs*. Zenodo. DOI: 10.5281/zenodo.19533619
- Lakens, D. (2013). Calculating and reporting effect sizes to facilitate
  cumulative science: A practical primer for t-tests and ANOVAs.
  *Frontiers in Psychology*, 4, 863.
  DOI: 10.3389/fpsyg.2013.00863
- Liang, T., He, Z., Jiao, W., Wang, X., Wang, Y., Wang, R., Yang, Y.,
  Shi, S., & Tu, Z. (2024). Encouraging divergent thinking in large language
  models through multi-agent debate. In *Proceedings of the 2024 Conference on
  Empirical Methods in Natural Language Processing* (pp. 17889–17904).
  DOI: 10.18653/v1/2024.emnlp-main.992  (arXiv preprint: arXiv:2305.19118)
- Nosek, B. A., Ebersole, C. R., DeHaven, A. C., & Mellor, D. T. (2018). The
  preregistration revolution. *PNAS*, 115(11), 2600–2606.
  DOI: 10.1073/pnas.1708274114
- Noy, S., & Zhang, W. (2023). Experimental evidence on the productivity
  effects of generative artificial intelligence. *Science*, 381(6654),
  187–192. DOI: 10.1126/science.adh2586
- Sandve, G. K., Nekrutenko, A., Taylor, J., & Hovig, E. (2013). Ten simple
  rules for reproducible computational research. *PLoS Computational
  Biology*, 9(10), e1003285. DOI: 10.1371/journal.pcbi.1003285
- Shinn, N., Cassano, F., Berman, E., Gopinath, A., Narasimhan, K., & Yao, S.
  (2023). Reflexion: Language agents with verbal reinforcement learning.
  In *Advances in Neural Information Processing Systems 36 (NeurIPS 2023)*,
  pp. 8634–8652. (arXiv preprint: arXiv:2303.11366)
- Snell, C., Lee, J., Xu, K., & Kumar, A. (2024). Scaling LLM test-time
  compute optimally can be more effective than scaling model parameters.
  arXiv:2408.03314. DOI: 10.48550/arXiv.2408.03314
- Steegen, S., Tuerlinckx, F., Gelman, A., & Vanpaemel, W. (2016). Increasing
  transparency through a multiverse analysis. *Perspectives on Psychological
  Science*, 11(5), 702–712. DOI: 10.1177/1745691616658637
- Tomlinson, B., Black, R. W., Patterson, D. J., & Torrance, A. W. (2024).
  The carbon emissions of writing and illustrating are lower for AI than for
  humans. *Scientific Reports*, 14, 3732.
  DOI: 10.1038/s41598-024-54271-x
- Verga, P., Hofstätter, S., Althammer, S., Su, Y., Piktus, A.,
  Arkhangorodsky, A., Xu, M., White, N., & Lewis, P. (2024). Replacing judges
  with juries: Evaluating LLM generations with a panel of diverse models.
  arXiv:2404.18796. DOI: 10.48550/arXiv.2404.18796
- Wang, X., Wei, J., Schuurmans, D., Le, Q., Chi, E., Narang, S.,
  Chowdhery, A., & Zhou, D. (2023). Self-consistency improves chain of thought
  reasoning in language models. In *Proceedings of the Eleventh International
  Conference on Learning Representations* (ICLR 2023).
  (arXiv preprint: arXiv:2203.11171)
- Wei, J., Wang, X., Schuurmans, D., Bosma, M., Ichter, B., Xia, F., Chi, E.,
  Le, Q., & Zhou, D. (2022). Chain-of-thought prompting elicits reasoning in
  large language models. In *Advances in Neural Information Processing Systems
  35 (NeurIPS 2022)*, pp. 24824–24837.
  (arXiv preprint: arXiv:2201.11903)
- Yao, S., Yu, D., Zhao, J., Shafran, I., Griffiths, T. L., Cao, Y., &
  Narasimhan, K. (2023). Tree of thoughts: Deliberate problem solving with
  large language models. In *Advances in Neural Information Processing Systems
  36 (NeurIPS 2023)*. (arXiv preprint: arXiv:2305.10601)
- Zheng, L., Chiang, W.-L., Sheng, Y., Zhuang, S., Wu, Z., Zhuang, Y.,
  Lin, Z., Li, Z., Li, D., Xing, E. P., Zhang, H., Gonzalez, J. E., &
  Stoica, I. (2023). Judging LLM-as-a-judge with MT-Bench and Chatbot Arena.
  In *Advances in Neural Information Processing Systems 36 (NeurIPS 2023)*,
  Datasets and Benchmarks Track. (arXiv preprint: arXiv:2306.05685)
