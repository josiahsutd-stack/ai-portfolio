# Evaluation

## Scope

The evaluation measures deterministic state transitions over 5 repository-authored synthetic conversations. It does not evaluate a language model or compare against professional specification authors.

## Cases

| Case | Behavior under test |
| --- | --- |
| Clinic brief revision | Multi-requirement extraction, budget replacement, conflict resolution, approvals, and citations. |
| Warehouse role gates | Structural, performance, and budget approvals plus three unauthorized attempts. |
| Community-centre conflict | Unresolved facade alternatives, partial approvals, and open decisions. |
| Unsupported chatter | Questions and prompt-like text produce no requirement or clause. |
| Direct approval reference | Requirement-ID approval with one denied and one authorized action. |

## Metrics

- Requirement extraction precision, recall, and F1 over active key/value pairs.
- Open-conflict precision, recall, and F1 over requirement keys.
- Approval-state precision, recall, and F1 over approved keys.
- Specification-clause precision, recall, and F1 over keys represented in the draft.
- Requirement citation coverage.
- Denied-approval count accuracy.
- Draft-status accuracy, including a no-approved-evidence case.

## Checked-In Result

All listed metrics are `1.000` over `35` messages in `5` synthetic cases. The result is intentionally narrow: fixtures were written to exercise the implemented grammar and role matrix. It should be read as executable regression evidence, not generalization evidence.

## Artifacts

- [`demo_outputs/evaluation_summary.json`](demo_outputs/evaluation_summary.json): metrics and observed state per case.
- [`demo_outputs/evaluation_report.md`](demo_outputs/evaluation_report.md): compact score table and boundary.
- [`demo_outputs/failure_analysis.md`](demo_outputs/failure_analysis.md): fixture-level mismatches.
- [`demo_outputs/sample_audit_trace.json`](demo_outputs/sample_audit_trace.json): append-only event sequence for one case.
- [`demo_outputs/sample_specification.md`](demo_outputs/sample_specification.md): source-linked draft.
- [`demo_outputs/sample_trace.svg`](demo_outputs/sample_trace.svg): generated trace diagram.

## Missing Evaluation

- No expert-labeled real conversation set.
- No transcription errors, multilingual messages, long-context threads, or document attachments.
- No requirement ontology benchmark or inter-annotator agreement.
- No adversarial identity spoofing, database concurrency, or access-control penetration testing.
