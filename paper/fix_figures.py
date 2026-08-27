#!/usr/bin/env python3
"""Fix duplicate headers and insert missing Figure 4."""

with open("research/orchestration-economics/paper/FULL-PAPER-DRAFT.md", "r") as f:
    content = f.read()

# Fix duplicate section headers
content = content.replace("## 3.2 Models evaluated\n\n## 3.2 Models evaluated", "## 3.2 Models evaluated", 1)
content = content.replace("## 4.2 The persona penalty\n\n## 4.2 The persona penalty", "## 4.2 The persona penalty", 1)

# Insert Figure 4 after §4.4 Key Takeaway
old4 = "**Key Takeaway:** A $0.002 refinement pass recovers most of the\nfrontier gap on average, never achieves paired superiority over the\nfrontier.\n\n## 4.5 Study 2 — qualitative mechanism"
new4 = "**Key Takeaway:** A $0.002 refinement pass recovers most of the\nfrontier gap on average, never achieves paired superiority over the\nfrontier.\n\n![Figure 4. Study 2: Refinement Probe Results](figures/fig4_gap_recovery.png)\n\n## 4.5 Study 2 — qualitative mechanism"
content = content.replace(old4, new4, 1)

with open("research/orchestration-economics/paper/FULL-PAPER-DRAFT.md", "w") as f:
    f.write(content)

print("Cleanup completed.")
