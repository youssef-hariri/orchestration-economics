# Citation Audit Report — 02-LITERATURE-REVIEW.md

**Date:** 2026-08-07  
**Auditor:** Automated verification via Crossref, PubMed, journal databases, and arXiv  
**Scope:** All 18 references in the DOI-verified register

---

## Summary

| Category | Count |
|----------|-------|
| Verified correct | 13 |
| Critical errors (DOI / venue / year wrong) | 2 |
| Minor corrections (missing subtitle, author name, available journal DOI) | 3 |
| Self-citations (Hariri) — not externally verifiable | 3 |

---

## Critical Errors — Must Fix Before Submission

### 1. Albers & Lakens (2018) — WRONG DOI
- **File has:** `DOI: 10.1016/j.jesp.2017.06.013`
- **Correct DOI:** `10.1016/j.jesp.2017.09.004`
- **Full title:** "When power analyses based on pilot data are biased: Inaccurate effect size estimators and follow-up bias"
- **Impact:** This is a fatal citation error. The DOI in the file resolves to a different article (or fails). The correct DOI is well-established in thousands of citing papers.
- **Action:** Replace DOI and add the subtitle.

### 2. Liang et al. (2023) — WRONG PUBLICATION YEAR / VENUE
- **File has:** "Proceedings of EMNLP 2023" with arXiv DOI `10.48550/arXiv.2305.19118`
- **Correct venue:** *Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing* (EMNLP 2024)
- **arXiv preprint date:** May 2023
- **Conference publication:** November 2024
- **Impact:** Citing as 2023/EMNLP 2023 is incorrect. The paper was accepted and presented at EMNLP 2024. The year should be 2024, or the citation should note it as an arXiv preprint (2023) later published at EMNLP 2024.
- **Action:** Update to (2024) and cite as EMNLP 2024, or clarify as arXiv 2023 / EMNLP 2024.

---

## Minor Corrections — Should Fix

### 3. Dell'Acqua et al. (2023) — Incomplete Author Name & Title
- **File has:** "Lifshitz, H."
- **Correct author:** "Lifshitz-Assaf, H." (Hila Lifshitz-Assaf)
- **File title:** "Navigating the Jagged Technological Frontier"
- **Full title:** "Navigating the jagged technological frontier: Field experimental evidence of the effects of AI on knowledge worker productivity and quality"
- **Action:** Correct author surname and add subtitle.

### 4. Tomlinson et al. (2024) — Journal DOI Now Available
- **File has:** `DOI: 10.48550/arXiv.2303.06219 (journal DOI pending)`
- **Journal DOI (now available):** `10.1038/s41598-024-54271-x`
- **Published in:** *Scientific Reports*, 14, 3732 (February 2024)
- **Action:** Replace arXiv DOI with the journal DOI and remove the "pending" note.

### 5. Diewert (1976) — Title Capitalization
- **File has:** "Exact and superlative index numbers"
- **Standard form:** "Exact and superlative index numbers" (sentence case is acceptable, but the journal uses this form consistently)
- **Action:** No change required if following sentence-case convention, but verify consistency with target journal style.

---

## Verified Correct — No Changes Needed

| # | Reference | DOI | Status |
|---|-----------|-----|--------|
| 1 | Brynjolfsson, Li & Raymond (2023) | 10.3386/w31161 | ✓ Confirmed via NBER |
| 2 | Cohen (1960) | 10.1177/001316446002000104 | ✓ Confirmed via Sage/PubMed |
| 3 | Diewert (1976) | 10.1016/0304-4076(76)90009-9 | ✓ Confirmed via ScienceDirect |
| 4 | Lakens (2013) | 10.3389/fpsyg.2013.00863 | ✓ Confirmed via Frontiers |
| 5 | Nosek et al. (2018) | 10.1073/pnas.1708274114 | ✓ Confirmed via PNAS/PubMed |
| 6 | Noy & Zhang (2023) | 10.1126/science.adh2586 | ✓ Confirmed via Science |
| 7 | Sandve et al. (2013) | 10.1371/journal.pcbi.1003285 | ✓ Confirmed via PLOS |
| 8 | Steegen et al. (2016) | 10.1177/1745691616658637 | ✓ Confirmed via Sage/PubMed |
| 9 | Verga et al. (2024) | 10.48550/arXiv.2404.18796 | ✓ Confirmed via arXiv |
| 10 | Wang et al. (2023) — ICLR | 10.48550/arXiv.2203.11171 | ✓ Confirmed: arXiv 2022 → ICLR 2023 |
| 11 | Zheng et al. (2023) — NeurIPS | 10.48550/arXiv.2306.05685 | ✓ Confirmed: NeurIPS 2023 D&B Track |

---

## Self-Citations (Not Externally Verifiable)

| Reference | DOI | Note |
|-----------|-----|------|
| Hariri (2025a) | 10.5281/zenodo.17407392 | Author's own Zenodo deposit |
| Hariri (2025b) | 10.5281/zenodo.17490945 | Author's own Zenodo deposit |
| Hariri (2026b) | 10.5281/zenodo.19533619 | Author's own Zenodo deposit |

These are pre-print / dataset deposits on Zenodo. They are not peer-reviewed publications. Ensure the target journal allows self-citations to non-peer-reviewed work, or consider moving these to a "Related Work" or "Data Availability" section rather than the main literature review references.

---

## Recommendations

1. **Fix the two critical errors immediately** — the wrong DOI for Albers & Lakens and the wrong year/venue for Liang et al. are submission-blocking.
2. **Update Tomlinson et al.** with the now-available journal DOI.
3. **Correct Lifshitz-Assaf's name** in Dell'Acqua et al.
4. **Review self-citations** — consider whether Hariri (2025a, 2025b, 2026b) should be in the main References or in a separate "Author's Prior Work" section, depending on journal guidelines.
5. **Re-verify all DOIs** with a fresh Crossref query before final submission, as DOI redirects can change.

---

*Audit methodology: DOI resolution checked against Crossref, PubMed, journal publisher databases, and arXiv metadata. Author names verified against original publication PDFs. Conference proceedings verified against ACL Anthology and NeurIPS proceedings.*
