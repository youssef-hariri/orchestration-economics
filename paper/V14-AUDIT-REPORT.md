# V14 Audit Report — Orchestration Economics DBA Thesis

**Date:** 2026-09-05
**Source (read-only, preserved):** `FULL-PAPER-DRAFT-BUSINESS-v13_with_figures/FULL-PAPER-DRAFT-BUSINESS-v13.tex`
**Target (all edits):** `FULL-PAPER-DRAFT-BUSINESS-v14_with_figures/FULL-PAPER-DRAFT-BUSINESS-v14.tex`
**Compiler:** TeX Live 2024 `pdflatex` (`/Library/TeX/texbin/pdflatex`), two passes
**Scope:** Business-reader narrative restructure of v13 into a DBA thesis. Plain-English surface on narrative sections; statistical substrate untouched.

---

## 1. Guardrail Summary

| Guardrail | Requirement | Result |
|-----------|-------------|--------|
| **G1** | Numerical invariance — only H1/H2 may change | ✅ PASS |
| **G2** | Disclosure preservation (D52/D53/D58, A5–A8, AI/COI) | ✅ PASS |
| **G3** | Cross-reference cascade — 0 undefined refs | ✅ PASS |
| **G4** | Recompile gate — overfull reduced, >250pt tables fixed | ✅ PASS |
| **G5** | Versioning + changelog | ✅ PASS (this report) |

**Build health:** 41 pages · 0 undefined references · 0 missing figures · 0 undefined citations · 7 overfull hboxes (worst 24.8pt) · 0 underfull vboxes.

---

## 2. G1 — Numerical Invariance

A multiset diff of every numeric token (`[-+]?\d+(?:\{,\}\d+)*(?:\.\d+)?`) was run across v13 and v14.

- **Total numeric tokens:** v13 = 1,427 · v14 = 1,484 (+57).
- **Distinct statistical values dropped:** none. The only distinct value present in v13 and absent from v14 is `-20`, which is a fragment of the **v13 header comment date** `2026-08-20` (metadata, not a statistic).
- **Distinct values newly introduced:** `-09` (fragment of the new header date `2026-09-05`), `4.6`, `7.6` (the two `p{}` **column widths** in the redesigned summary table). None are statistics.

Every other delta is a *count* change of a value that still appears in both drafts, fully attributable to the four intended edit classes below. No computed result was altered, rounded, or removed.

### 2.1 The two intended harmonizations

| ID | Location | v13 | v14 |
|----|----------|-----|-----|
| **H1** | Abstract + Conclusion (wave count) | "2,400 runs" / "2,400-run replication wave" | "2,400 planned; **2,418 analyzed** runs" (matches body `n = 2{,}418`) |
| **H2** | Conclusion opening scope | "this 1,900-run experiment and its 2,400-run replication wave" | names **all four** bases: Study 1 (1,900) · Protocol 12 wave (2,418 analyzed) · Study 3 (544 completed) · Protocol 16 (441 completed) |

Token effect: `2{,}400` 4→3 (H2 removed the conclusion instance); `2{,}418` 3→5 (H1 abstract + H2 conclusion); `544` 1→2 and `441` 3→4 (H2 conclusion). All consistent with the body values verified at `tex:84, 92, 115, 218, 1195, 1211, 1384, 1503`.

### 2.2 Increases = re-citations, not new statistics

The new **§6 Managerial Implications** re-cites existing body figures only (no new computation): `98 / 23 / 6.15` (C-S-N), `98.8 / 88 / 1.49` (C-T-N), `353 / 0.27 / 3.5×` (F-T-N), `$0.002 / 78%` (refinement), `0.24× / 2–3.5×` (Study 3 family economics), `4 of 5` families, `10` families, `2 of 5` Protocol 16 gates. Each matches its source in §4–§5.

### 2.3 Abstract streamlining (intended)

Abstract: 502 → 459 words. It **dropped only protocol-number labels** `11`, `13`, `16` (recast as the Study 1/2/3 decision journey per the plan) and **added** the Study labels, `2,418` (H1), and the `3.5×` frontier-team framing. All statistical *values* in the v13 abstract (−0.227, −0.691, +0.017, +0.075, +0.85, +1.25, −1.90, −3.15, 0.824, 0.002, 6.15, 1.49, 0.24, 64, 98, 23, 88, 1,900, 441, 570, …) are preserved in v14.

**G1 verdict:** the only numeric changes are H1, H2, Managerial-Implications re-citations, header-date metadata, and two table column widths. ✅

---

## 3. G2 — Disclosure Preservation

| Disclosure | Present | Evidence (v14 line) |
|------------|:-------:|---------------------|
| **D52** singular dual-vc LMM fallback + REML caveat | ✅ | `singular` ×2, `REML` ×1, `D52` ×2 (wave design, ~1199) |
| **D53** Kimi Together.ai routing deviation | ✅ | `Together.ai` ×2, `D53` ×2 (~1201) |
| **D58** Study 3 attrition confound | ✅ | `D58` ×1, `attrition` ×5 (Study 3 design ~1384; Protocol 16 ~1503) |
| **A5–A8** registered-but-unexecuted arms | ✅ | `A5`×3, `A6`×1, `A7`×5, `A8`×1 |
| **AI-assisted research / DeeWaanAI COI** | ✅ | `\subsection{AI-Assisted Research Disclosure}` `sec:ai-disclosure` (784); DeeWaanAI relationship + transparency note (837–842, 2042–2053) |

All disclosures survive verbatim in substance. ✅

---

## 4. G3 — Cross-Reference Cascade

The Results reorder, the new §6, and the section renumbering (Limitations 6→7, Future 7→8, Conclusion 8→9) shift every downstream reference. After two `pdflatex` passes:

- **Undefined references: 0**
- **Undefined citations: 0**
- New label `sec:managerial` resolves (referenced from the Intro roadmap).
- New label `fig:study3-family-domain` resolves.
- New `\cref{sec:future}` in the Study 2 replication-scope note resolves.

✅

---

## 5. G4 — Recompile Gate & Overfull Boxes

| Metric | v13 | v14 |
|--------|-----|-----|
| Pages | 41 | 41 |
| Overfull hboxes (total) | 9 | **7** |
| Worst overfull | **750.6pt** (`tab:summary-findings`) | **24.8pt** (inherited paragraph) |
| 2nd worst | 255.5pt (`tab:managerial`) | 20.9pt |
| 3rd worst | 88.1pt (`\texttt` model names) | 20.7pt |

**Fixes applied:**
- `tab:summary-findings` (750pt): converted from all-fixed `tabularx {l l c}` to a plain `tabular` with three ragged-right wrapping columns `p{7.6cm} / p{4.6cm} / p{2.2cm}` in `\footnotesize` (sum < 16cm text width).
- `tab:managerial` (255pt): converted to `tabularx` with a ragged-right `p{3.4cm}` first column and a stretching wrapping `X` last column, in `\small`.
- 88pt box: wrapped the "Lower-Tier Siblings" paragraph (long unbreakable `\texttt` model names) in `sloppypar` — formatting only, zero text change.

The 7 residual boxes are all ≤24.8pt paragraph-level items, several inherited verbatim from v13. ✅

---

## 6. Citation Spot-Check

All four items flagged in `CITATION-AUDIT-REPORT.md` are correct in v14:

| Reference | Audit finding | v14 state |
|-----------|---------------|-----------|
| Albers & Lakens (2018) | wrong DOI | ✅ `10.1016/j.jesp.2017.09.004` + full subtitle (2060–2065) |
| Liang et al. | wrong year/venue | ✅ `LiangEtAl2024`, *EMNLP 2024*, ACL DOI `10.18653/v1/2024.emnlp-main.992` (2160–2167) |
| Tomlinson et al. (2024) | arXiv DOI, journal pending | ✅ journal DOI `10.1038/s41598-024-54271-x` (2219–2224) |
| Dell'Acqua et al. (2023) | "Lifshitz, H." | ✅ "Lifshitz-Assaf, H." (2096–2097) |

✅

---

## 7. Figure Inventory Resolution

- **Reality:** the v14 directory holds **15 PNGs, no PDFs**. `pdflatex` consumes PNG directly, so PDF versions are not required to compile.
- **fig23** (`fig23_study3_family_domain.png`) was an **orphan** in v13 (present, never embedded). v14 **embeds it in §4.3** (Study 3 family-specific economics) with a caption and label `fig:study3-family-domain`.
- All **15 figures** are now embedded (14 in v13 + fig23).
- **`Additional_figures_needed.md` corrected:** the false claim "44 files (22 PNG + 22 PDF); all 22 embedded" replaced with the true 15-PNG inventory; §5 crosswalk rewritten to v14 compiled order; supplementary figs 11–18 clarified as script-only (not in the paper directory).
- **`FIGURE-SELECTION-GUIDE.md` updated:** fig23 added to the priority table, given a full spec entry, and added to the closing crosswalk.

✅

---

## 8. Changelog — What Changed and Why

### Structure (Phase B)
1. **Results recast into a 3-act buyer's decision journey** with a roadmap paragraph naming the escalating question. Study 1 = §4.1 (interaction, persona penalty, frontier gap, **Pareto/robustness/exploratory moved up**, wave §4.1.7); Study 2 = §4.2 (refinement ceiling, coverage-vs-density mechanism); Study 3 = §4.3 (+ Protocol 16 §4.3.1); Summary = §4.4.
2. **Replication waves attached to their acts** (Protocol 12 → Study 1; Protocol 16 → Study 3) as the "can I bet on this?" assurance layer, not separate plot points.
3. **Block move executed byte-exact via Python** (106-line refinement/Pareto regroup) — zero transcription risk on statistics.

### Accessibility layer (Phase C) — narrative sections only; Methodology untouched
4. **Abstract rewritten** to the 3-act skeleton (Study 1/2/3 bolded, money-first, registry metadata to clause tails); H1 applied.
5. **Intro roadmap** fixed: "both studies" → the three-study decision journey; adds `\cref{sec:managerial}`.
6. **New §6 Managerial Implications** (DBA-standard): Investment Ladder (sequenced budget rule), Operating Model (benchmark-and-route), Risk Register (persona/density/replication risk), Build-versus-Buy sourcing decision. Every claim money-first, statistic-second.
7. **Conclusion H2** scope fix (names all four empirical bases).
8. **Study 2 replication-scope honesty note** added: states plainly that Study 2, unlike Studies 1 and 3, was not carried into a confirmatory wave, and is framed as mechanistic explanation, not out-of-sample-confirmed economics.
9. Strategic-Implication / Key-Takeaway boxes confirmed present at every Results subsection.

### Formatting & assets (Phase D)
10. Both >250pt tables fixed; 88pt `\texttt` box fixed (see §5).
11. fig23 embedded; figure docs corrected (see §7).
12. Section banner comments renumbered (Managerial = 6, Limitations = 7, Future = 8, Conclusion = 9).

---

## 9. Final Section Order (v14)

1 Introduction · 2 Literature Review · 3 Methodology · 4 Results (3 acts + Summary) · 5 Discussion · **6 Managerial Implications (new)** · 7 Limitations · 8 Future Directions · 9 Conclusion · Appendix A Executive Summary for Practitioners · References.

---

## 10. Remaining Minor Items (non-blocking)

- 7 residual overfull hboxes ≤24.8pt, several inherited from v13 (long `\cref`/math sequences). Cosmetic; safe to leave or tune later.
- Supplementary figures 11–18 remain script-only (flagged, not generated) per plan out-of-scope.
- **Not committed** — per instruction, no `git commit`/`push` was performed.

**Overall verdict: v14 builds clean, preserves every statistic and disclosure verbatim, applies only the two intended harmonizations (H1/H2), and delivers the DBA business-reader narrative restructure. Ready for author review.**
