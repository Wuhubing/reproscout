"""Independent implementation of the original CORE-Bench prediction-interval rule.

Reference: siegelz/core-bench benchmark/evaluations.py at the commit in tasks.py.
No benchmark code is imported or invoked. See docs/research-references.md.
"""

from __future__ import annotations

import math
from statistics import mean, stdev

from scipy.stats import t


def score_answers(answers: dict, reference_runs: list[dict], questions: dict) -> dict:
    if not reference_runs or not reference_runs[0]:
        raise ValueError("Reference answers must be nonempty")
    verdicts = {}
    for qid, question in questions.items():
        expected = reference_runs[0][question]
        supplied = answers.get(qid, {}).get("value")
        correct = False
        if isinstance(expected, (int, float)):
            values = [float(run[question]) for run in reference_runs]
            if len(values) < 2 or not all(math.isfinite(v) for v in values):
                raise ValueError("Numeric scoring requires at least two finite reference runs")
            width = (
                float(t.ppf(0.975, len(values) - 1))
                * stdev(values)
                * math.sqrt(1 + 1 / len(values))
            )
            try:
                number = float(str(supplied).replace("%", ""))
                correct = (
                    math.isfinite(number) and mean(values) - width <= number <= mean(values) + width
                )
            except (ValueError, TypeError):
                pass
        elif isinstance(expected, list):
            correct = supplied == expected
        else:
            correct = supplied is not None and str(supplied).lower() == str(expected).lower()
        verdicts[qid] = bool(correct)
    return {
        "scorer": "reproscout-original-core-prediction-interval-v1",
        "question_correct": verdicts,
        "correct_questions": sum(verdicts.values()),
        "total_questions": len(verdicts),
        "solved": bool(verdicts) and all(verdicts.values()),
        "policy": "Exact question mapping; no punctuation normalization or rounding adjustment.",
    }
