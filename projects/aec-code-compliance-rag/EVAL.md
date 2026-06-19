# Retrieval Evaluation

This project includes a 50-case synthetic retrieval and abstention evaluation set for reviewer inspection. The goal is not to claim production accuracy. The goal is to show how retrieval quality, citation coverage, no-evidence handling, and unsupported-scope handling are measured before real use.

## Run The Evaluation

From the repository root:

```bash
python projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py
```

This writes:

- `demo_outputs/retrieval_eval_summary.json`
- `demo_outputs/retrieval_eval_report.md`
- `demo_outputs/failure_analysis.md`
- `demo_outputs/accessible_route_answer.md`
- `demo_outputs/no_answer_failure_case.md`
- `demo_outputs/sample_answer_accessible_route.md`
- `demo_outputs/sample_answer_no_evidence.md`

## Evaluation Data

Evaluation cases live in:

```text
projects/aec-code-compliance-rag/eval/eval_cases.jsonl
```

Each case includes:

- `id`
- `case_type`
- `question`
- `expected_status`
- `expected_source`
- `expected_section`
- `expected_clause_ids`
- `expected_terms`
- `expected_no_answer`
- `notes`

The dataset is synthetic and useful for regression checks and reviewer clarity, not for benchmarking a real compliance product.

## Metrics

| Metric | Meaning |
| --- | --- |
| `recall_at_k` | Whether the expected source appears in the top-k retrieved chunks. |
| `precision_at_k` | Share of retrieved chunks that come from the expected source. |
| `hit_rate` | Binary retrieval success per case, averaged across cases. |
| `mean_reciprocal_rank` | Whether the first relevant result appears early in the ranked list. |
| `section_hit_rate` | Whether the expected section appears in the retrieved chunks. |
| `citation_coverage` | Share of expected terms present in the retrieved evidence. |
| `grounding_check_rate` | Lightweight check that retrieved evidence includes expected terms and section. |
| `status_accuracy` | Whether answer status matches `answered`, `no_evidence`, `unsupported_scope`, or `needs_professional_review`. |
| `citation_check_pass_rate` | Whether deterministic citation coverage checks pass for generated answers. |
| `retrieval_hit_at_1` / `retrieval_hit_at_3` | Whether the expected source appears early in the retrieved result list. |
| `no_answer_accuracy` | Whether absent-evidence questions correctly return no retrieved support. |
| `unsupported_scope_accuracy` | Whether live-code, jurisdiction, or professional-review questions are refused with the expected status. |

Because the corpus is synthetic and contains overlapping topics, `precision_at_k` is less important than status accuracy, hit@3, citation coverage, and failure analysis.

## What The Current Eval Catches

- Numeric criteria retrieval, such as `1200 mm`, `850 mm`, and `12 mm`.
- Section targeting for accessibility, fire compartment, daylight, planning, and drawing QA questions.
- Whether citations preserve chunk IDs and section metadata.
- Whether retrieval can support answer generation without paid APIs.
- Whether no-answer, unsupported-scope, prompt-injection, and professional-review questions avoid invented compliance requirements.

## Known Failure Modes

- Questions that require a real jurisdiction, code year, or amendment cannot be answered from the synthetic corpus.
- TF-IDF can miss semantically related wording if key terms are absent from the query.
- Citation coverage only checks expected terms in retrieved evidence; it is not full answer faithfulness.
- The grounding check is lexical and section-based; it is not a semantic entailment model.
- The demo corpus has synthetic page markers rather than PDF-derived pages.

## Better Evaluation Next

- Add negative questions where the correct behavior is no answer.
- Add paraphrased questions to stress semantic retrieval.
- Add multi-document cases where precision matters.
- Add citation-faithfulness checks from answer sentence to supporting chunk.
- Add jurisdiction and version metadata cases.
- Track no-result rate and low-confidence answer rate over a larger eval set.
