# Portfolio Review Record

**Document status:** self-authored engineering audit, not an external recruiter endorsement.

| Round | Credibility issue | Repository change | Verifiable outcome |
| --- | --- | --- | --- |
| 1. Claim boundaries | Early project names and summaries implied deeper AI capability than the code supported. | Renamed weak systems, separated selected work from experiments, and added a claims policy plus automated phrase checks. | `scripts/check_claims.py` and `scripts/check_repo_health.py` run in full verification. |
| 2. AEC flagship depth | The original AEC RAG looked like a basic local demo. | Added metadata-rich chunking, four retrieval modes, citations, abstention, evaluation cases, failure analysis, architecture docs, and focused tests. | Synthetic 51-case regression plus public 24-case snapshot over 15 validated downloads. |
| 3. Public-source credibility | Public-document claims lacked fail-closed validation and reproducible identity. | Added source manifests, resolved URLs, PDF/content validation, SHA-256 fingerprints, and snapshot-scoped reporting. | Public `Hit@1 0.952`, `MRR 0.976`, paraphrase `MRR 0.917`, no-answer `1.000`. |
| 4. Embodied AI evidence | Language-to-action logic was initially too close to a scripted grid demo. | Added procedural splits, expert trajectories, fitted behavior cloning, raw and filtered closed-loop evaluation, interventions, and failures. | 24 unseen scenarios; filtered learned policy success `0.625`, unsafe-action rate `0.000`. |
| 5. AEC workflow depth | Massing, communication, and QS ideas existed only as portfolio concepts. | Built three bounded systems with typed contracts, focused tests, evaluators, architecture docs, limitations, and generated visuals. | Massing baseline gap, 35-message specification regression, and 21-line QS/tender fixture evaluation. |
| 6. Recruiter hierarchy | Generic text, research, and MLOps exercises diluted the AEC specialization. | Promoted evidence-backed AEC workflow projects and moved generic systems to experiments. Rewrote README, profile, site, role map, and review paths. | Exactly five selected projects and fourteen experiments enforced by repository health checks. |
| 7. Cross-project credibility | A workflow diagram implied continuity without demonstrating that the specification, massing, and QS schemas actually exchanged data. | Added a separate deterministic integration contract with approved-requirement gating, field-level sources, cross-project invariants, schematic geometry provenance, generated traces, and rejection tests. | One labeled synthetic fixture records 5 approved requirements, 16 sourced fields, 96 generated candidates, and 7 priced takeoff lines; tender analysis remains explicitly not run. |

The audit intentionally preserves limitations and negative evidence. Perfect fixture scores are labeled as deterministic regression results, not general model-quality claims.
