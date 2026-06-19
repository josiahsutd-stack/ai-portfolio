# Retrieval Mode Ablation

Singapore public-source comparison of local retrieval modes over the same AEC eval set.

| Mode | Recall@k | MRR | Hit@3 | Citation coverage | Status accuracy |
| --- | --- | --- | --- | --- | --- |
| tfidf | 1.0 | 0.967 | 1.0 | 1.0 | 1.0 |
| bm25 | 1.0 | 0.922 | 1.0 | 1.0 | 1.0 |
| hybrid | 1.0 | 0.922 | 1.0 | 1.0 | 1.0 |
| dense_lsa | 0.933 | 0.839 | 0.867 | 0.611 | 1.0 |

## Interpretation

- `tfidf` and `bm25` are transparent lexical baselines.
- `dense_lsa` is a local dense baseline using TF-IDF projected into latent semantic analysis space.
- `hybrid` is the default app mode because it combines lexical evidence and a lightweight rerank boost.
- These numbers are local regression checks, not production compliance accuracy.
