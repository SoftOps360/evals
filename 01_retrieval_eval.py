"""Step 1 - the retrieval eval. No LLM, no key. Deterministic pass/fail per case + accuracy.

Read the FAIL lines: the two that miss are paraphrases with no shared words (Episode 10's point).
The eval doesn't just give a number - it tells you exactly WHERE the system is weak.
"""
from _eval import load_cases, run_retrieval_eval, accuracy

cases = load_cases("evalset.jsonl")
results = run_retrieval_eval(cases)

for r in results:
    mark = "PASS" if r["pass"] else "FAIL"
    print(f"  {mark}  {r['score']:.2f}  got={r['got']:<28} want={r['expected_runbook']:<28} | {r['question'][:42]}")

acc = accuracy(results)
print(f"\nRetrieval accuracy: {acc:.0%}  ({sum(r['pass'] for r in results)}/{len(results)})")
print("The two failures are vocabulary-mismatch paraphrases - exactly what embeddings (Ep10) fix. "
      "An eval turns 'seems fine' into a number you can improve and defend.")
