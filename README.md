# Episode 18 — Evals: Do You Trust It?

You built an AI system. How do you *know* it's correct — and know it *stayed* correct after you
changed a prompt? You test it, like any other software. This episode builds an **eval harness**:
a dataset of cases, a score, and a **CI gate** so a change that hurts quality can't merge.

Evals are rarely taught and hugely valuable — "it looked right once" is not a test.

## Two kinds of check

**1. Retrieval eval (deterministic, no LLM).**
A dataset of `question → expected_runbook`. Run retrieval, compare, compute a **pass rate**.
Our sample set scores **80% (8/10)** — and the two failures are the *same vocabulary-mismatch
paraphrases* from Episode 10. The eval doesn't just give a number; it points at **where** the
system is weak.

**2. LLM-as-judge (for open-ended answers).**
When there's no single correct string, a **separate model call grades** the answer against a
rubric (0..1). Useful — but the judge is itself an LLM, so anchor it with a strict rubric and
spot-check it against humans.

## Files

| File | What it does | Needs a key? |
|------|--------------|--------------|
| `evalset.jsonl` | The dataset: 10 `question → expected_runbook` cases. | — |
| `_eval.py` | The harness: `run_retrieval_eval`, `accuracy`, `judge`. | judge only |
| `01_retrieval_eval.py` | Per-case PASS/FAIL + accuracy. | no |
| `run_evals.py` | **The gate** — exits non-zero below the threshold (put it in CI). | no |
| `02_llm_judge.py` | Grade open-ended answers with a rubric. | yes |

## Run it

```bash
pip install -r requirements.txt
python 01_retrieval_eval.py     # PASS/FAIL table + accuracy (no key)
python run_evals.py             # CI gate: exit 1 if below threshold (no key)
python 02_llm_judge.py          # LLM-as-judge (needs a key)
```

Wire `run_evals.py` into CI (like Ep16's config check). If someone changes the retriever or a
prompt and accuracy drops below `THRESHOLD`, the build fails — a regression can't sneak in.

## How it was verified

The retrieval eval is deterministic and **runs here**: **80% (8/10)**, with the two failures
being the vocabulary-mismatch cases (consistent with Ep10), and the gate exits 0 at the 70%
threshold. The numbers are real, not staged. The LLM-as-judge path is standard `ask_json`
(needs a key to run live).

## Honesty & limits (please keep these in the video)

- **An eval set is a sample, not proof.** 80% on ten cases isn't "80% correct in prod" — grow
  the set with real failures you hit, and weight the cases that matter most.
- **The judge is an LLM too.** LLM-as-judge is convenient but fallible and can be gamed by
  confident wording. Keep rubrics strict, and periodically compare the judge to human grades.
- **Deterministic checks first.** Where you *can* grade with `==` or a keyword/retrieval match,
  do — it's cheaper, faster, and not itself an AI you have to trust.
- **Evals guard regressions, they don't guarantee correctness.** Passing the suite means "no
  worse than before on these cases", which is exactly why you keep adding cases.
- **Non-determinism.** LLM outputs vary run to run; for judge-based scores, average over a few
  runs or pin temperature, and treat small score wobbles as noise.
