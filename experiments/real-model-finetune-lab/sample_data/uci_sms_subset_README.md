# UCI SMS Spam Subset

`uci_sms_subset.tsv` is a compact, balanced subset of the UCI SMS Spam Collection for offline CI-friendly text-classification evaluation.

Source: [UCI Machine Learning Repository - SMS Spam Collection](https://archive.ics.uci.edu/dataset/228/sms%2Bspam%2Bcollection)

- DOI: [`10.24432/C5CC84`](https://doi.org/10.24432/C5CC84)
- License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- Pinned archive SHA-256: `1587ea43e58e82b14ff1f5425c88e17f8496bfcdb67a583dbff9eefaf9963ce3`

Citation from the dataset page:

Tiago A. Almeida, Jose Maria Gomez Hidalgo, and Akebo Yamakami. Contributions to the study of SMS spam filtering: new collection and results. ACM Symposium on Document Engineering, 2011.

Deterministic subset construction:

- Normalize source text with NFKD-to-ASCII conversion and collapsed whitespace.
- De-duplicate normalized messages, retaining the first one-based source row.
- Rank each label with SHA-256 using the fixed seed `ai-portfolio-public-sms-v1`.
- Select 120 `ham` and 120 `spam` messages.
- Assign 80 messages per label to train, 20 to validation, and 20 to test using a separate SHA-256 rank.
- Record each source row and the exact output hash in [`uci_sms_subset_manifest.json`](uci_sms_subset_manifest.json).

Rebuild from the pinned official archive or run the offline provenance check:

```bash
python experiments/real-model-finetune-lab/scripts/build_uci_sms_subset.py
python experiments/real-model-finetune-lab/scripts/build_uci_sms_subset.py --check
```

The builder downloads the official archive only when the ignored local copy is absent. Normal evaluation and CI use the checked-in subset without network access. The balanced subset is included only for a small training path and is not a replacement for full-corpus or naturally imbalanced evaluation.
