# Monitoring

This project includes local monitoring primitives for a synthetic churn model. The goal is to show operational thinking, not deployed monitoring.

## What Is Logged

Prediction logs include:

- timestamp
- request ID
- model version
- input payload
- prediction
- latency in milliseconds when supplied
- error text when supplied

## Drift Metrics

The project uses two lightweight numeric checks:

- Mean shift: relative change in feature mean.
- PSI-style distribution shift: compares binned reference and current feature distributions.

These are useful demo signals but not a substitute for full monitoring. PSI is sensitive to binning, sample size, and feature distribution.

## Monitoring Report

`generate_monitoring_report()` returns:

- prediction volume
- latency count/average/max
- error count
- drift scores
- warning messages for drifted features

Sample report:

- [demo_outputs/sample_monitoring_report.json](demo_outputs/sample_monitoring_report.json)

## Production Gaps

- No live endpoint metrics.
- No delayed labels.
- No feature store.
- No alert routing.
- No model rollback automation.
- No auth, privacy, or multi-tenant logging controls.
