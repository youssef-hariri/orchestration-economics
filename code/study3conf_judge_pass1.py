#!/usr/bin/env python3
"""Protocol 16 judging — non-DeepSeek pass (zhipu + meta only).

Scheduling rule (OSF zkm8v / D44 precedent): DeepSeek judges only in off-peak
windows (weekday: UTC 16:30-00:30; weekend: all day Beijing). This wrapper does
NOT modify the frozen judge_v2.py on disk; it restricts the in-memory judge
list for this pass. judge_v2 resumes by (runId, judge, variant), so the
DeepSeek pass tonight and the final catch-up pass (for the last kimi solution)
fill the remainder against the same output file.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "code"))
import judge_v2  # noqa: E402

judge_v2.judges = [j for j in judge_v2.judges if j["family"] != "deepseek"]
print("judging pass: judges =", [j["family"] for j in judge_v2.judges], flush=True)

sys.argv = ["judge_v2", "--store", str(ROOT / "runs/study3conf/study3conf_store.json"),
            "--out", str(ROOT / "runs/study3conf/study3conf_judgments.jsonl")]
judge_v2.main()
