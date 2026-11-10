from app import ask


def test_result_has_required_fields():
    result = ask("How many sick days do I get?")
    for field in ["question", "retrieved_chunks", "answer", "done_reason"]:
        assert field in result


def test_generation_finished_normally():
    result = ask("How many sick days do I get?")
    assert result["done_reason"] == "stop"


def test_sick_days_answer():
    result = ask("How many sick days do I get?")
    assert "10" in result["answer"]


def test_refuses_when_not_in_docs():
    result = ask("What is the maternity leave policy?")
    assert "I don't have that information" in result["answer"]

def test_notice_period_fact_is_retrieved():
    result = ask("What is the notice period?")
    texts = [c["text"] for c in result["retrieved_chunks"]]
    assert any("30 days written notice" in t for t in texts)


def test_notice_period_answer():
    result = ask("What is the notice period?")
    assert "30 days" in result["answer"]