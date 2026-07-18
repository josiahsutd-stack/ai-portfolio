# Case Study: Deterministic Research Workflow Assistant

## Problem

Research-agent demos often hide tool choices and failure paths. This project keeps the workflow deterministic and traceable.

## Local System

The default planner classifies tasks, selects allowed tools, searches local documents, creates a cited report, records approval requirements, and persists the trace to SQLite.

## Retry And Tool Handling

Tool calls record attempts, latency, errors, denied-tool status, and approval requirements. Transient failures can succeed on retry; exhausted failures remain visible in the trace.

## Evaluation

`python experiments/agentic-research-ops-assistant/scripts/evaluate_agent.py` writes an eval summary, report, and sample trace.

## Boundaries

The project is not autonomous web research and is not a replacement for a research analyst. It demonstrates traceable tool orchestration and approval checkpoints.
