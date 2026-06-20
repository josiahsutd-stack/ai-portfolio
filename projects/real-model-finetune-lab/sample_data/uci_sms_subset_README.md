# UCI SMS Spam Subset

`uci_sms_subset.tsv` is a compact, balanced subset of the UCI SMS Spam Collection for offline CI-friendly text-classification evaluation.

Source: [UCI Machine Learning Repository - SMS Spam Collection](https://archive.ics.uci.edu/dataset/228/sms%2Bspam%2Bcollection)

Citation from the dataset page:

Tiago A. Almeida, Jose Maria Gomez Hidalgo, and Akebo Yamakami. Contributions to the study of SMS spam filtering: new collection and results. ACM Symposium on Document Engineering, 2011.

Subset construction:

- 240 total rows.
- 120 `ham`, 120 `spam`.
- Fixed split: 160 train, 40 validation, 40 test.
- Text is normalized to single-line ASCII for repository portability.

This subset is included only for a small public-dataset training path. It is not intended as a benchmark replacement for the full corpus.
