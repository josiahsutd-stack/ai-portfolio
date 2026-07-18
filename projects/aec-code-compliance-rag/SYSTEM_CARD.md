# System Card

## Intended Use

Local portfolio demonstration of source-grounded document retrieval, citation, abstention, and service-boundary patterns for AEC guidance.

## Not Intended For

Legal advice, code compliance approval, engineering sign-off, architectural sign-off, construction authorization, or jurisdictional interpretation.

## Data

The default corpus contains synthetic markdown documents, a generated text-based PDF addendum, and a source manifest created for this repository. An optional workflow downloads official public Singapore documents locally and records resolved URLs, hashes, and corpus fingerprints. Neither corpus contains client or private-project records.

## Evaluation

The synthetic eval suite includes answerable, paraphrased, multi-clause, PDF-backed, source-metadata, no-evidence, unsupported-scope, prompt-injection, and professional-review cases. A separate in-process ASGI suite checks 12 local service behaviors. A fixed 48-query concurrent workload checks P95/error budgets and verifies that bounded payload-free telemetry survives app reconstruction.

## Data Handling

The local service redacts question and response payloads in SQLite by default. Raw query-log payload storage must be explicitly enabled. Request telemetry retains the bounded request ID for correlation but excludes arbitrary headers, query strings, questions, and bodies; it is bounded to 5,000 rows by default. These are review-oriented controls, not privacy certification or substitutes for access-control, consent, deletion, or incident-response policies.

## Known Risks

Local retrieval baselines can miss semantic matches or retrieve plausible but wrong sections. Citation coverage checks are not full factual verification. The shared API key is not identity-aware authorization, and the in-process service evaluations do not establish external-deployment security, sustained reliability, availability, or scale.
