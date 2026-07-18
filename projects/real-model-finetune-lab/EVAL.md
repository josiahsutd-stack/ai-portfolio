# Evaluation

This evaluation measures a small classical text classifier on fixed local splits. It is evidence that model parameters are fitted and evaluated reproducibly, not a benchmark or production-quality claim.

## Public SMS Protocol

- Dataset: compact balanced subset deterministically selected from a pinned UCI SMS Spam Collection archive.
- Split: fixed train, validation, and test labels stored in the TSV file.
- Baseline: most-frequent-class `DummyClassifier` fitted on the training split.
- Model: TF-IDF unigrams/bigrams plus logistic regression fitted on training rows only.
- Selection: the validation split is reported separately; the test split is used for the final checked-in result.
- Outputs: metrics, confusion matrix, report, and a locally generated ignored model binary.

## Current Measured Results

| Metric | Result |
| --- | --- |
| Train rows | `160` |
| Validation rows | `40` |
| Test rows | `40` |
| Baseline test accuracy | `0.500` |
| Validation accuracy | `0.850` |
| Test accuracy | `0.950` |
| Test macro-F1 | `0.950` |

Class-level errors are visible in [`demo_outputs/public_sms_confusion_matrix.json`](demo_outputs/public_sms_confusion_matrix.json). Exact values above are tied to [`demo_outputs/public_sms_metrics.json`](demo_outputs/public_sms_metrics.json) by the repository evidence checker.

## Leakage Controls

- Source archive hash, one-based source row, normalization, selection seed, and split assignment are recorded in `sample_data/uci_sms_subset_manifest.json`.
- Normalized duplicate messages are removed before deterministic SHA-256 ranking and split assignment.
- Split labels are explicit and mutually exclusive, with balanced labels inside each split.
- TF-IDF vocabulary and logistic-regression parameters are fitted on training rows only.
- Validation and test rows are transformed through the fitted pipeline without refitting.
- Tests assert the split sizes, learned coefficient shape, and improvement over the baseline.
- The generated artifact records the dataset name and all split counts.

## Interpretation Limits

- The 240-row subset is deliberately compact and balanced; it does not represent the full dataset distribution.
- The same fixed test set is used as a regression fixture, so repeated repository development can indirectly overfit to it.
- No hyperparameter search, probability calibration, robustness suite, latency benchmark, or external test corpus is included.
- Accuracy and macro-F1 on 40 test rows have high sampling uncertainty and should not be generalized to production messaging.
- This is classical supervised learning, not transformer or LoRA adaptation.

## Reproduce

```bash
python projects/real-model-finetune-lab/evaluate_model.py
python -m pytest tests/test_real_model_finetune_lab.py
```
