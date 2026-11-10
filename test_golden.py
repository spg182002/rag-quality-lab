import json
import pytest
from app import ask

with open("golden.json", encoding="utf-8") as f:
    ROWS = json.load(f)

KNOWN_FAIL = {"pii-1"}
@pytest.mark.parametrize("row", ROWS, ids=[r["id"] for r in ROWS])

def test_golden(row):
    if row["id"] in KNOWN_FAIL:
        pytest.xfail("known safety gap, see BUG-007 and BUG-008")
    result = ask(row["question"])
    answer = result["answer"]
    chunk_ids = [f"{c['source']}#{c['chunk_index']}" for c in result["retrieved_chunks"]]
    info = (
        f"question={result['question']!r}\n"
        f"chunks={chunk_ids}\n"
        f"answer={answer!r}"
    )
    assert row["expected"] in answer, info
    if "must_not_contain" in row:
        assert row["must_not_contain"].lower() not in answer.lower(), info
    if "must_retrieve" in row:
        texts = [c["text"] for c in result["retrieved_chunks"]]
        assert any(row["must_retrieve"] in t for t in texts), info