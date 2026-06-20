# Public Dataset Training Report

Dataset: UCI SMS Spam Collection compact subset

## Split

- Train rows: 160
- Validation rows: 40
- Test rows: 40
- Labels: ham, spam

## Metrics

- Baseline test accuracy: 0.5
- Trained validation accuracy: 0.825
- Trained test accuracy: 0.975
- Baseline test macro-F1: 0.333
- Trained validation macro-F1: 0.825
- Trained test macro-F1: 0.975
- Learned coefficient shape: (1, 691)

## Confusion Matrix

Labels: ham, spam

```json
[[19, 1], [0, 20]]
```

The public-dataset path uses a locally bundled UCI SMS Spam subset. It is a stronger signal than the tiny synthetic demo, while still staying small enough for offline CI.
