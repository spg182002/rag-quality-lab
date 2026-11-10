import os
os.environ["DEEPEVAL_TELEMETRY_OPT_OUT"] = "YES"

import pytest

from deepeval.metrics import FaithfulnessMetric
from deepeval.test_case import LLMTestCase
from app import ask
from deepeval_judge import OllamaJudge

JUDGE = OllamaJudge()


def run(question):
    result = ask(question)
    case = LLMTestCase(
        input=question,
        actual_output=result["answer"],
        retrieval_context=[c["text"] for c in result["retrieved_chunks"]],
    )
    metric = FaithfulnessMetric(threshold=0.7, model=JUDGE, async_mode=False)
    metric.measure(case)
    print(f"\nSCORE={metric.score} question={question!r}\nANSWER={result['answer']!r}\nREASON={metric.reason}")
    return metric, result


def test_faithful_answer_scores_high():
    metric, result = run("How many sick days do I get?")
    assert metric.score >= 0.7, f"score={metric.score} reason={metric.reason} answer={result['answer']!r}"


def test_notice_period_faithful():
    metric, result = run("What is the notice period?")
    assert metric.score >= 0.7, f"score={metric.score} reason={metric.reason} answer={result['answer']!r}"

@pytest.mark.xfail(reason="local 8B judge accepts hallucinations (FINDING-001)")
def test_hallucinated_answer_scores_low():
    result = ask("How many days of bereavement leave do I get?")
    case = LLMTestCase(
        input="How many days of bereavement leave do I get?",
        actual_output="Full-time employees get 3 days of bereavement leave.",
        retrieval_context=[c["text"] for c in result["retrieved_chunks"]],
    )
    metric = FaithfulnessMetric(threshold=0.7, model=JUDGE, async_mode=False)
    metric.measure(case)
    print(f"\nSCORE={metric.score}\nREASON={metric.reason}")
    assert metric.score < 0.7, f"judge accepted a hallucination, score={metric.score}"