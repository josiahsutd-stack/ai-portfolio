# Case Study: Local Model Serving And Monitoring Scaffold

## Problem

ML portfolio projects often stop at a notebook. This project shows the local shape of training, schema validation, artifact metadata, prediction logging, and drift simulation.

## Local System

The project generates synthetic churn data, trains a scikit-learn model, computes metrics, saves model metadata, validates prediction payloads, logs predictions, and writes drift reports.

## Evaluation

`python experiments/mlops-model-serving-monitoring/scripts/evaluate_model.py` writes model metrics, sample prediction logs, and a drift report to `demo_outputs/`.

## Boundaries

This is a local MLOps skeleton. It is not production monitoring and not a real customer-retention decision system.

## Production Extension

A production version would need a real registry, feature store or batch pipeline, delayed labels, alerting, access controls, rollback, model governance, and monitoring ownership.
