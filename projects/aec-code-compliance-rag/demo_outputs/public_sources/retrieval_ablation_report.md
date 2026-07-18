# Retrieval Mode Ablation

Singapore public-source comparison of local retrieval modes over the same AEC eval set.

Corpus SHA-256: `f0af72d9f642a1a1bf86cbd8d1d0268bf3a4a3fa4505546655d36f7cb36dceb1`
Eval-set SHA-256: `aa2cc41f311071d6f9ccad09c154b34a3d872db470d023cfa874c71f68ea6498`

| Mode | Recall@k | MRR | Hit@3 | Citation coverage | Status accuracy |
| --- | --- | --- | --- | --- | --- |
| hybrid | 1.0 | 0.976 | 1.0 | 0.968 | 1.0 |
| bm25 | 1.0 | 0.964 | 0.952 | 0.968 | 1.0 |
| tfidf | 0.952 | 0.873 | 0.952 | 0.873 | 1.0 |
| dense_lsa | 0.857 | 0.857 | 0.857 | 0.778 | 1.0 |

## Interpretation

- `tfidf` and `bm25` are transparent lexical baselines.
- `dense_lsa` is a local dense baseline using TF-IDF projected into latent semantic analysis space.
- `hybrid` is the default app mode because it combines lexical evidence and a lightweight rerank boost.
- These numbers are local regression checks, not production compliance accuracy.
