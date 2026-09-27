"""Step 2 - LLM-as-judge, for answers with no single 'correct' string.

Retrieval you can grade with '==' . An open-ended answer you can't. So a SEPARATE model call
grades it against a rubric. Useful, but see the honesty note: the judge is itself an LLM and can
be wrong or biased - anchor it with a strict rubric, and spot-check the judge against humans.
"""
from _eval import judge

CASES = [
    {"question": "What causes a 502 from nginx?",
     "answer": "nginx got no valid response from its upstream - the backend is down, overloaded, or misconfigured.",
     "rubric": "Must say a 502 means the upstream/backend did not respond correctly. Must NOT invent a specific cause."},
    {"question": "What causes a 502 from nginx?",
     "answer": "It's always a DNS problem on port 5432.",     # wrong + invented
     "rubric": "Must say a 502 means the upstream/backend did not respond correctly. Must NOT invent a specific cause."},
]

for c in CASES:
    result = judge(c["question"], c["answer"], c["rubric"])
    print(f"\nQ: {c['question']}\nA: {c['answer']}")
    print(f"  score: {result.get('score')}  reason: {result.get('reason')}")

print("\nA good judge scores the first answer high and the second low. Keep the rubric strict "
      "and remember the judge is an LLM too - spot-check it.")
