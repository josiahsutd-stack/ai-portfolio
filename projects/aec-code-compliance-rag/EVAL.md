# Retrieval Evaluation

This project includes a 51-case synthetic retrieval and abstention evaluation set plus an optional Singapore public-source evaluation set. It does not establish production accuracy. It measures retrieval quality, citation coverage, PDF-backed citation behavior, source metadata handling, no-evidence handling, and unsupported-scope handling before real use.

## Run The Evaluation

From the repository root:

```bash
python projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py
```

Optional Singapore public-source evaluation:

```bash
python projects/aec-code-compliance-rag/scripts/download_public_sources.py
python projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py --corpus public
```

This writes:

- `demo_outputs/evaluation_manifest.json`
- `demo_outputs/retrieval_eval_summary.json`
- `demo_outputs/retrieval_eval_report.md`
- `demo_outputs/retrieval_ablation_summary.json`
- `demo_outputs/retrieval_ablation_report.md`
- `demo_outputs/failure_analysis.md`
- `demo_outputs/accessible_route_answer.md`
- `demo_outputs/no_answer_failure_case.md`
- `demo_outputs/sample_answer_accessible_route.md`
- `demo_outputs/sample_answer_no_evidence.md`

The public-source command writes the same artifact set under:

```text
projects/aec-code-compliance-rag/demo_outputs/public_sources/
```

## Local Service Contract Evaluation

Run the service evaluator separately:

```bash
python projects/aec-code-compliance-rag/evaluate_service.py
```

It performs 12 deterministic in-process ASGI checks over the synthetic corpus: public liveness, readiness, fail-closed authentication, request-ID propagation, grounded answers, no-evidence status, request validation, ranked retrieval, default payload redaction, audit-log request IDs, and route/error metrics.

Current artifact-backed result: 12/12 local service contract checks passed; 9 requests were observed before the metrics response.

Generated evidence:

- [`demo_outputs/service_contract_summary.json`](demo_outputs/service_contract_summary.json)
- [`demo_outputs/service_contract_report.md`](demo_outputs/service_contract_report.md)

This contract suite does not start an external listener. It provides no evidence about cloud deployment, TLS, secret management, multiple workers, load capacity, availability, penetration resistance, incident response, privacy compliance, or user traffic.

## Evaluation Data

Evaluation cases live in:

```text
projects/aec-code-compliance-rag/eval/eval_cases.jsonl
projects/aec-code-compliance-rag/eval/public_eval_cases.jsonl
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

The synthetic dataset supports deterministic regression checks. The public-source dataset checks whether the same pipeline can ingest and retrieve from official Singapore public documents such as BCA Accessibility, URA GFA, NEA COPEH, SCDF Fire Code, LTA interface references, PUB drainage/sewerage references, and NParks greenery/tree-conservation references. Neither dataset is a benchmark for a real compliance product.

## Current Public-Source Snapshot

The committed snapshot was generated on 18 July 2026 after 15 official-source payloads passed HTTP and file-type validation. The versioned artifacts identify the exact source inventory, document corpus, and eval set with SHA-256 fingerprints.

| Measure | Result |
| --- | ---: |
| Documents | `15` |
| Cases | `24` |
| Direct / paraphrase / no-evidence / professional-review | `15 / 6 / 2 / 1` |
| Hybrid Hit@1 | `0.952` |
| Hybrid MRR | `0.976` |
| Paraphrase MRR | `0.917` |
| Citation coverage | `0.968` |
| Grounding check rate | `0.905` |
| No-answer accuracy | `1.000` |

The correct source appears within the top four for every answerable case, but this does not mean every retrieved chunk contains every expected phrase. Two paraphrase cases miss one expected phrase at top four and are retained in the versioned failure analysis.

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
| `answer_sentence_support_rate` | Share of generated answer sentences that pass deterministic citation-support checks. |
| `unsupported_sentence_rate` | Share of generated answer sentences flagged as unsupported by the deterministic citation checker. |
| `retrieval_hit_at_1` / `retrieval_hit_at_3` | Whether the expected source appears early in the retrieved result list. |
| `no_answer_accuracy` | Whether absent-evidence questions correctly return a `no_evidence` status. Candidate retrieval may still be logged for diagnosis. |
| `unsupported_scope_accuracy` | Whether live-code, jurisdiction, or professional-review questions are refused with the expected status. |

Because the corpus is synthetic and contains overlapping topics, `precision_at_k` is less important than status accuracy, hit@3, citation coverage, and failure analysis.

Retrieval metrics are averaged over answerable cases. Status accuracy, no-answer accuracy, and unsupported-scope accuracy are averaged over their relevant case types, so professional-review refusals do not reduce retrieval recall.

## Retrieval Mode Ablation

The evaluation script also compares four local retrieval modes over the same cases:

- `tfidf`: transparent lexical vector baseline.
- `bm25`: transparent lexical ranking baseline.
- `dense_lsa`: local dense baseline using TF-IDF projected with latent semantic analysis.
- `hybrid`: default app mode combining TF-IDF, BM25, and a lightweight rerank boost.

The ablation artifacts are meant to show retrieval evaluation discipline. They are not a claim that the best synthetic-mode score will transfer to real compliance documents.

Optional modes `semantic` and `hybrid_cross_encoder` are exposed in the app and assistant boundary, but they require `requirements-embeddings.txt` and local model downloads. The committed evaluation artifacts use portable modes that reproduce without a GPU or model cache.

## What The Current Eval Catches

- Numeric criteria retrieval, such as `1200 mm`, `850 mm`, and `12 mm`.
- Section targeting for accessibility, fire compartment, daylight, planning, and drawing QA questions.
- Whether citations preserve chunk IDs and section metadata.
- Whether PDF extraction preserves source filename, section heading, and page-aware citation metadata.
- Whether source manifest metadata and source filters are covered by regression tests.
- Whether authority/document inference keeps named-agency questions inside the intended BCA, URA, NEA, SCDF, LTA, PUB, or NParks source family.
- Whether retrieval-mode changes improve or degrade recall, hit@3, MRR, and status accuracy.
- Whether retrieval can support answer generation without paid APIs.
- Whether no-answer, unsupported-scope, prompt-injection, and professional-review questions avoid invented compliance requirements.
- Whether Singapore public-source retrieval can find authority-specific documents across BCA, URA, NEA, SCDF, LTA, PUB, and NParks without committing the downloaded PDFs to Git.
- Whether paraphrased public-source questions still rank the expected document early.
- Whether project-specific questions abstain when only generic public references are available.
- Whether committed results match a fingerprinted source inventory, corpus, and eval set.

## Known Failure Modes

- Questions that require a real jurisdiction, code year, or amendment cannot be answered from the synthetic corpus.
- The public-source corpus uses official public downloads, but it does not verify amendments, authority interpretations, project-specific applicability, or professional sign-off.
- The public eval has only 24 authored cases and no independent domain-expert labels.
- Two current paraphrase cases retrieve the expected source but miss one expected phrase in the top-four chunks.
- TF-IDF can miss semantically related wording if key terms are absent from the query.
- Citation coverage only checks expected terms in retrieved evidence; it is not full answer faithfulness.
- The grounding check is lexical and section-based; it is not a semantic entailment model.
- PDF ingestion is text-based and page-aware, but it does not reconstruct tables, OCR scanned pages, or reason over layout geometry.

## Better Evaluation Next

- Add independently reviewed clause/page targets and multi-document cases where precision matters.
- Add citation-faithfulness checks from answer sentence to supporting chunk.
- Add Singapore amendment-refresh and superseded-document tests.
- Compare optional embedding and cross-encoder modes on the same fingerprinted public snapshot.
- Track no-result rate and low-confidence answer rate over a larger eval set.
- Exercise the service behind a real reverse proxy with identity-aware authorization, fault injection, concurrency/load tests, durable telemetry, and explicit latency/error objectives.
