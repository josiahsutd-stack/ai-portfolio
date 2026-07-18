# Case Study: Deterministic Research Workflow

## Problem

Tool-workflow demos can hide selection rules and failure paths. This implementation keeps both deterministic and inspectable.

## Local System

The default planner classifies tasks, selects allowed tools, searches local documents, creates a cited report, records approval requirements, and persists the trace to SQLite.

## Retry And Tool Handling

Tool calls record attempts, latency, errors, denied-tool status, and approval requirements. Transient failures can succeed on retry; exhausted failures remain visible in the trace.

## Evaluation

`python experiments/deterministic-research-workflow/scripts/evaluate_workflow.py` writes an eval summary, report, and sample trace.

## Boundaries

The project is not autonomous web research and is not a replacement for a research analyst. Its evidence is limited to the bundled local workflow and trace checks.
