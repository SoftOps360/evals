"""Eval harness - test your AI system like software. Two kinds of check:

  1. Retrieval eval (no LLM): does the right runbook come back for each question?
     A dataset of (question -> expected_runbook) + a pass rate. Fully deterministic.
  2. LLM-as-judge (needs a model): grade an open-ended answer 0..1 against a rubric.
     Use a *separate* model call as a grader when there's no single 'correct' string.

Why bother: "it looked right once" is not a test. An eval set lets you change a prompt or a
retriever and SEE whether quality went up or down - and gate CI so a regression can't merge.
"""
import json
from _rag import build_chunks, TfidfIndex

_INDEX = None


def index():
    global _INDEX
    if _INDEX is None:
        _INDEX = TfidfIndex().fit(build_chunks("runbooks"))
    return _INDEX


def load_cases(path="evalset.jsonl"):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def run_retrieval_eval(cases):
    results = []
    for c in cases:
        hits = index().search(c["question"], 1)
        got = hits[0][1]["source"] if hits else None
        score = hits[0][0] if hits else 0.0
        results.append({**c, "got": got, "score": round(score, 3),
                        "pass": got == c["expected_runbook"]})
    return results


def accuracy(results):
    return sum(r["pass"] for r in results) / len(results) if results else 0.0


def judge(question, answer, rubric):
    """LLM-as-judge: a second model call grades the answer. Returns {'score': float, 'reason': str}."""
    from _llm import ask_json   # lazy: retrieval eval needs no LLM
    system = (
        "You are a STRICT grader. Given a QUESTION, an ANSWER, and a RUBRIC, return JSON "
        '{"score": <float 0..1>, "reason": "<short>"}. 1.0 = fully meets the rubric, 0.0 = fails. '
        "Penalize hallucination or claims not supported by the rubric heavily."
    )
    return ask_json(f"QUESTION: {question}\nANSWER: {answer}\nRUBRIC: {rubric}", system=system)
