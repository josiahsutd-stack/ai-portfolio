# Final Evidence Audit

**Document status:** self-authored hiring-manager-style audit, dated 18 July 2026. It is not an independent endorsement, reference, or hiring decision.

## Fifteen-Minute Screen Answers

| Question | Evidence-based answer |
| --- | --- |
| Is the first screen compelling? | Yes for AEC, construction robotics, and computational-design roles: it opens with three differentiated projects and measured results. |
| Are the top three obvious? | Yes: AEC RAG, Construction Embodied Agent, and Constraint-Aware Massing Explorer. |
| Can something run quickly? | Yes: each selected project has one evaluator command, the cross-project contract runs with `python integrations/aec-design-to-cost/run_workflow.py`, and the full local verifier is `python scripts/verify.py`. |
| Is there proof beyond claims? | Yes: versioned JSON/CSV/Markdown/SVG outputs, public-source hashes, focused tests, baselines, failure analyses, and an executed source-linked cross-project trace. |
| Are limitations honest? | Yes: professional, production, data, simulation, model, and geometry boundaries are repeated at project and portfolio level. |
| Are synthetic and mock parts unmistakable? | Yes in data files, app captions, generated artifacts, READMEs, and the claims policy. |
| Are selected projects deeper than experiments? | Yes. Promotion requires tests, an evaluator, checked-in evidence, architecture documentation, and limitations. |
| Are tests and evals present? | Yes across all selected projects and the integration rejection paths; the full verifier also checks artifact idempotence, links, claims, formatting, and imports. |
| Are research references decorative? | No headline claim depends on an unimplemented paper or SOTA label. Local baselines and implemented algorithms carry the evidence. |
| Would the repository earn an interview? | Yes for junior/applied AEC AI, computational-design AI, or construction-robotics roles. It does not yet prove mid-level production ownership. |

## Brutally Honest Score

| Dimension | Score | Reason |
| --- | ---: | --- |
| Domain differentiation | 9.0/10 | Architecture, AEC documents, massing, QS, and construction robotics form a credible specialization. |
| Evidence and reproducibility | 8.7/10 | Strong local tests, evaluators, artifacts, baselines, claim checks, and a deterministic cross-project contract; several datasets remain small and authored. |
| Applied AI engineering | 8.2/10 | Good retrieval, workflow state, classical policy learning, geometry, evaluation, typed handoffs, and local interfaces. Limited neural-model depth. |
| Visual and reviewer clarity | 9.1/10 | Actual generated outputs and an executed workflow trace explain the systems; project hierarchy is explicit. |
| Production evidence | 4.5/10 | No users, cloud deployment, auth, observability at scale, service reliability, or customer data. |
| Professional AEC validation | 4.0/10 | No authority, architect, engineer, or QS validation on live project outputs. |

**Overall junior/applied interview readiness: 8.6/10.**

**Mid-level production AI readiness based on this repository alone: 5.5/10.**

## Highest-Value Next Evidence

1. One permissioned public or partner AEC dataset with expert labels and a held-out evaluation protocol.
2. One deployed selected project with authentication, monitoring, latency/error budgets, and usage evidence.
3. One robotics integration beyond structured grids, such as perception input, ROS 2 simulation, or a physics-based environment.
4. Professional review of a bounded massing, specification, or QS output with documented disagreement and corrections.
