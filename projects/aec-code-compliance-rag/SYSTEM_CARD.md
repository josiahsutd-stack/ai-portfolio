# System Card

## Intended Use

Local portfolio demonstration of source-grounded document retrieval, citation, abstention, and service-boundary patterns for AEC guidance.

## Not Intended For

Legal advice, code compliance approval, engineering sign-off, architectural sign-off, construction authorization, or jurisdictional interpretation.

## Data

The default corpus contains synthetic markdown documents, a generated text-based PDF addendum, and a source manifest created for this repository. An optional workflow downloads official public Singapore documents locally and records resolved URLs, hashes, and corpus fingerprints. Neither corpus contains client or private-project records.

## Evaluation

The synthetic eval suite includes answerable, paraphrased, multi-clause, PDF-backed, source-metadata, no-evidence, unsupported-scope, prompt-injection, and professional-review cases. A separate in-process ASGI suite checks 12 local service behaviors, including fail-closed authentication, readiness, request tracing, redacted logs, and process-local metrics.

## Data Handling

The local service redacts question and response payloads in SQLite by default. Raw payload storage must be explicitly enabled. This is a review-oriented default, not a privacy certification or a substitute for retention, access-control, consent, deletion, or incident-response policies.

## Known Risks

Local retrieval baselines can miss semantic matches or retrieve plausible but wrong sections. Citation coverage checks are not full factual verification. The shared API key is not identity-aware authorization, and the in-process service evaluation does not establish external-deployment security, reliability, or scale.
