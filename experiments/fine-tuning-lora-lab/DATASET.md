# Dataset

This lab uses a synthetic instruction dataset for support-ticket classification. It is designed to demonstrate dataset hygiene before fine-tuning, not to train a useful model.

## Schema

Each row must contain:

- `instruction`
- `input`
- `output`

## Validation Checks

`validate_dataset()` checks:

- required fields exist
- fields are not empty
- output labels exist
- duplicate instruction/input/output triples are rejected
- row count is non-zero

## Split Checks

`split_dataset()` verifies:

- `train_ratio` is between 0 and 1
- train and validation sets are both non-empty when rows exist

## Known Dataset Limitations

- Synthetic messages are templated and small.
- There is no real user/customer data.
- There is no privacy review because no private data is included.
- The dataset is not large or varied enough to prove real fine-tuning value.
