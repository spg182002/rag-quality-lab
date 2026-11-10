
# rag-quality-lab: a test subject for GenAI testing

A small RAG chatbot over made-up HR policy documents, running fully local (Ollama, Chroma). It exists to be **tested and broken on purpose**. About 20% of the effort went into building it, 80% into testing it.

## Stack
Python 3.14 (CI: 3.12), Ollama (`llama3.2:3b` generator, `nomic-embed-text` embeddings, `llama3.1:8b` judge), Chroma, pytest, DeepEval, GitHub Actions.

## Pipeline
documents -> chunk -> embed -> Chroma -> retrieve top-k -> versioned system prompt -> LLM -> result dict

Every answer returns `question`, `retrieved_chunks`, `answer`, `done_reason`, so retrieval bugs can be separated from generation bugs. All settings (chunk size, overlap, top-k, temperature, model, prompt file) live in `config.py`.

## How to run
    python -m venv .venv && .venv\Scripts\activate
    pip install -r requirements.txt
    python store.py                      # build the index
    python -m pytest test_golden.py -v   # model-based suite (needs Ollama)
    python -m pytest test_chunker.py test_dataset.py -v   # fast tests, also run in CI

## Test layers
| Layer | Files | What it checks |
|---|---|---|
| Data | `test_dataset.py` | golden.json has unique IDs and required fields |
| Chunking | `test_chunker.py` | no oversized or tiny chunks, key facts stay whole |
| Index | `test_index.py` | Chroma matches the documents on disk (catches a stale index) |
| End to end | `test_golden.py` | 27 golden rows: normal, tricky, boundary, table, close-but-missing, injection, indirect injection, PII |
| Metrics | `test_deepeval.py` | DeepEval faithfulness with a local judge |
| Judge | `judge_test.py` | tests the judge itself on cases with known verdicts |

CI (GitHub Actions) runs the fast deterministic tests on changes to prompts, docs, config, or tests. The model-based suite runs locally because the runners have no Ollama.

## Bugs found or injected
See `BUGLOG.md` for the full diagnosis of each.
| ID | Bug | How it was found | Layer |
|---|---|---|---|
| 001 | TOP_K=1 cuts the notice period | injected; only a retrieval test caught it, the answer test was a lucky pass | retrieval |
| 002 | Prompt injection overrides rules | golden row | generation |
| 003 | Chunk size 100, overlap 0 splits "G1 \| $30" | injected | chunker |
| 004 | System prompt leak | golden row | generation |
| 005 | Stale index | injected; only `test_index.py` catches it | index |
| 006 | Grounding rule removed: fabricated "3 days bereavement leave" | injected; 5 of 23 rows at the time | prompt |
| 007 | Indirect injection via a poisoned document | golden row | generation |
| 008 | PII leak (salary, phone) | golden row | prompt gap |

## Key findings
- **A correct answer does not prove retrieval worked.** With top-k=1 the model guessed the cut-off "30 day" as "30 days".
- **A suite can stay green while the app is degraded.** The first TOP_K=1 run passed all tests until a retrieval-level test was added.
- **Exact-sentence checks are wrong for safety rows.** A safe refusal used different words and failed; asserting on the forbidden content (`must_not_contain`) fixed it.
- **Test the judge before trusting it.** Judge rubric v1 to v4 moved the error from one side to the other; the 3B judge scored 14 of 19, an 8B judge with claim splitting and a refusal shortcut 20 of 23 (rubric tuned on the same cases, so treat as optimistic).
- **DeepEval faithfulness with a local 8B judge gave 1.0 to a hallucination.** Marked xfail (FINDING-001); a metric must be validated on known-bad answers.
- **Prompt rules are a soft control.** v4 fixed one PII row and not another. Sturdier defenses: don't index confidential files, filter outputs, sanitize documents at ingestion.

## Limitations
Tiny corpus (4 documents), one run per row at temperature 0, small local models, string-based checks for most rows.
Limitations: add “Two safety rows (indirect-1, pii-1) remain known failures (xfail)
