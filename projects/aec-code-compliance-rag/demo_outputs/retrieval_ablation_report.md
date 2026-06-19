# Retrieval Mode Ablation

Synthetic comparison of local retrieval modes over the same AEC eval set.

| Mode | Recall@k | MRR | Hit@3 | Citation coverage | Status accuracy |
| --- | --- | --- | --- | --- | --- |
| dense_lsa | 0.922 | 0.863 | 1.0 | 0.922 | 1.0 |
| tfidf | 0.922 | 0.853 | 1.0 | 0.922 | 1.0 |
| bm25 | 0.922 | 0.846 | 1.0 | 0.922 | 1.0 |
| hybrid | 0.922 | 0.846 | 1.0 | 0.922 | 1.0 |

## Interpretation

- `tfidf` and `bm25` are transparent lexical baselines.
- `dense_lsa` is a local dense baseline using TF-IDF projected into latent semantic analysis space.
- `hybrid` is the default app mode because it combines lexical evidence and a lightweight rerank boost.
- These numbers are synthetic regression checks, not production compliance accuracy.
