"""run_evals.py - the eval suite as a CI gate. Exits non-zero if accuracy drops below THRESHOLD.

Put this in CI so a prompt or retriever change that HURTS quality can't merge. That's the whole
value of evals: turn 'trust me, it's better' into a number the pipeline enforces.
"""
import sys
from _eval import load_cases, run_retrieval_eval, accuracy

THRESHOLD = 0.70   # ship only if retrieval is at least this good

cases = load_cases("evalset.jsonl")
results = run_retrieval_eval(cases)
acc = accuracy(results)

fails = [r for r in results if not r["pass"]]
print(f"Retrieval eval: {acc:.0%} ({len(cases) - len(fails)}/{len(cases)}), threshold {THRESHOLD:.0%}")
for r in fails:
    print(f"  FAIL  want={r['expected_runbook']}  got={r['got']}  | {r['question']}")

if acc < THRESHOLD:
    print(f"\nBELOW THRESHOLD - failing the build.")
    sys.exit(1)
print("\nOK - meets the bar.")
sys.exit(0)
