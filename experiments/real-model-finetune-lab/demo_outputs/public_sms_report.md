# Public Dataset Training Report

Dataset: UCI SMS Spam Collection compact subset

## Split

- Train rows: 160
- Validation rows: 40
- Test rows: 40
- Labels: ham, spam

## Metrics

- Baseline test accuracy: 0.5
- Trained validation accuracy: 0.85
- Trained test accuracy: 0.95
- Baseline test macro-F1: 0.333
- Trained validation macro-F1: 0.848
- Trained test macro-F1: 0.95
- Learned coefficient shape: (1, 634)

## Confusion Matrix

Labels: ham, spam

```json
[[19, 1], [1, 19]]
```

The public-dataset path uses a deterministic, source-traceable UCI SMS Spam subset that remains small enough for offline CI.
