# ADR 0003: Mock Provider Boundaries

## Context

LLM and VLM calls should not require paid keys for tests.

## Decision

Keep deterministic mock providers and label their limitations prominently.

## Consequences

Workflows are testable, but mock outputs do not prove model intelligence.

## Alternatives Considered

Mandatory hosted providers were rejected because they would break local verification.

## Production Change

Production systems would need real provider integration, latency/cost tracking, evals, and fallback behavior.
