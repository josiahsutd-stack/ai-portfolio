# Evaluation

This project does not compute real fine-tuned model metrics because no model weights are updated locally.

## What Exists

`build_evaluation_template()` creates an explicit evaluation plan with:

- held-out prompts
- expected behavior
- exact-label checks
- confusion matrix requirement
- manual review of uncertain cases
- overfitting and duplicate-check reminders

## What A Real Eval Would Need

- Baseline model output before adaptation.
- Fine-tuned model output after adaptation.
- Held-out prompts that were not used for training.
- Label accuracy, confusion matrix, and per-class failure review.
- Qualitative review of uncertain or ambiguous tickets.
- Safety review for overconfident wrong labels.

## Failure Cases To Add Next

- Ambiguous tickets with multiple possible categories.
- Out-of-domain requests.
- Empty or malformed user messages.
- Near-duplicate training examples to detect memorization.
- Class imbalance and rare-label cases.
