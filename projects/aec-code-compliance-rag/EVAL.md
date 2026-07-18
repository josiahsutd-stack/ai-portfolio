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
- `demo_outputs/retrieval_uncertainty_summary.json`
- `demo_outputs/retrieval_uncertainty_report.md`
- `demo_outputs/retrieval_uncertainty_intervals.svg`
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

## Local Reliability Evaluation

Run the bounded workload separately:

```bash
python projects/aec-code-compliance-rag/evaluate_service_reliability.py
```

The evaluator warms the hybrid index, sends 48 synthetic-corpus queries with maximum concurrency 8, reads query-specific objectives, reconstructs the app against the same SQLite file, and checks that process counters reset while durable request telemetry remains.

Current artifact-backed result: 14/14 reliability checks passed; 48/48 responses returned 200, 0 server errors were observed, P95 was at or below 500 ms, and 48 durable query rows survived app reconstruction.

Generated evidence:

- [`demo_outputs/service_reliability_summary.json`](demo_outputs/service_reliability_summary.json)
- [`demo_outputs/service_reliability_report.md`](demo_outputs/service_reliability_report.md)

Exact wall-clock P95 is printed at runtime but not committed because it is machine-dependent. The versioned result records only whether the fixed 500 ms local budget passed. This is one warmed in-process workload, not network load, sustained capacity, uptime, availability, or production-SLO evidence.

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

## Fixed-Case Uncertainty

The evaluator reports 95% Wilson intervals for binary case outcomes, fixed-seed 10,000-resample percentile-bootstrap intervals for mean metrics, and paired-bootstrap deltas over matching answerable case IDs. The sampling unit is one authored evaluation case.

| Measure | Point | 95% interval | Support | Method |
| --- | ---: | ---: | ---: | --- |
| Hybrid Hit@1 | `0.952` | `[0.773, 0.992]` | `21` answerable cases | Wilson score |
| Hybrid MRR | `0.976` | `[0.929, 1.000]` | `21` answerable cases | Percentile bootstrap |
| Citation coverage | `0.968` | `[0.921, 1.000]` | `21` answerable cases | Percentile bootstrap |
| Grounding check | `0.905` | `[0.711, 0.973]` | `21` answerable cases | Wilson score |
| No-answer accuracy | `1.000` | `[0.342, 1.000]` | `2` no-evidence cases | Wilson score |
| Review/unsupported routing | `1.000` | `[0.207, 1.000]` | `1` case | Wilson score |

Hybrid versus BM25 MRR delta is `0.012` with a 95% paired interval of `[0.000, 0.036]`; `inconclusive_interval_includes_zero`. Their Hit@1 and citation coverage are identical on all 21 answerable cases. Hybrid has a positive fixed-set MRR delta over TF-IDF, but that comparison still describes only this authored snapshot.

The intervals quantify sensitivity to resampling these fixed authored cases. They do not measure independent-label quality, expert agreement, corpus currency, project applicability, or performance on future questions. The perfect 2/2 no-answer point estimate is therefore reported with its wide interval, not presented as certainty.

Generated evidence: [`retrieval_uncertainty_report.md`](demo_outputs/public_sources/retrieval_uncertainty_report.md), [`retrieval_uncertainty_summary.json`](demo_outputs/public_sources/retrieval_uncertainty_summary.json), and [`retrieval_uncertainty_intervals.svg`](demo_outputs/public_sources/retrieval_uncertainty_intervals.svg).

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

The ablation artifacts are meant to show retrieval evaluation discipline. The sorted point-estimate table is not evidence that one mode is generally superior; the paired uncertainty report is the interpretation surface for mode differences. None of these results is expected to transfer automatically to real compliance questions.

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
- Hit@1, grounding, no-answer, and review-routing intervals are wide at the current support sizes.
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
- Expand the public set with independent labels, report annotation disagreement, and narrow the no-answer and paraphrase intervals before making broader accuracy claims.
- Exercise the service behind a real reverse proxy with identity-aware authorization, fault injection, network load tests, distributed telemetry, and deployment-specific latency/error objectives.
