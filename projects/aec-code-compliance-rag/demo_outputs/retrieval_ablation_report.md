# Retrieval Mode Ablation

Synthetic demo comparison of local retrieval modes over the same AEC eval set.

Corpus SHA-256: `23648efd4c6080f9e4549757917d5223e28901f4a87eb490994690952a6a3636`
Eval-set SHA-256: `259f983f9822172808c113ddf9efacedf2c78f2773811ed37576d9a1fadd203f`

| Mode | Recall@k | MRR | Hit@3 | Citation coverage | Status accuracy |
| --- | --- | --- | --- | --- | --- |
| dense_lsa | 1.0 | 0.927 | 1.0 | 1.0 | 1.0 |
| tfidf | 1.0 | 0.915 | 1.0 | 1.0 | 1.0 |
| bm25 | 1.0 | 0.906 | 1.0 | 1.0 | 1.0 |
| hybrid | 1.0 | 0.906 | 1.0 | 1.0 | 1.0 |

## Interpretation

- `tfidf` and `bm25` are transparent lexical baselines.
- `dense_lsa` is a local dense baseline using TF-IDF projected into latent semantic analysis space.
- `hybrid` is the default app mode because it combines lexical evidence and a lightweight rerank boost.
- These numbers are local regression checks, not production compliance accuracy.
