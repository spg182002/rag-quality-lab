import json
from collections import Counter

with open("golden.json", encoding="utf-8") as f:
    ROWS = json.load(f)

REQUIRED = ["id", "question", "expected", "source", "category"]


def test_ids_are_unique():
    counts = Counter(r["id"] for r in ROWS)
    duplicates = [i for i, n in counts.items() if n > 1]
    assert not duplicates, f"duplicate ids: {duplicates}"


def test_rows_have_required_fields():
    for r in ROWS:
        for field in REQUIRED:
            assert field in r, f"row {r.get('id')!r} is missing {field!r}"