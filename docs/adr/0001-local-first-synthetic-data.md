# ADR 0001: Local-First Synthetic Data

## Context

The portfolio must be reviewable without private datasets, paid APIs, or cloud services.

## Decision

Use synthetic data and deterministic local paths by default.

## Consequences

The repo is easy to run and safe to inspect, but it does not prove real-world deployment performance.

## Alternatives Considered

Hosted APIs and private datasets were rejected for default tests because they would make review fragile.

## Production Change

A production version would need permissioned data, security review, monitoring, and domain validation.
