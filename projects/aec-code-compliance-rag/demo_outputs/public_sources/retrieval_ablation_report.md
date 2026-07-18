# Retrieval Mode Ablation

Singapore public-source comparison of local retrieval modes over the same AEC eval set.

Corpus SHA-256: `f0af72d9f642a1a1bf86cbd8d1d0268bf3a4a3fa4505546655d36f7cb36dceb1`
Eval-set SHA-256: `a2a54737b71cff6a3cddf11faead236ca99a188f62d0b7712bee5950c12cec18`

| Mode | Document Hit@1 | Document MRR | Exact Hit@1 | Exact MRR | Page Hit@1 | Page MRR | Status accuracy |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| hybrid | 0.952 | 0.976 | 0.81 | 0.881 | 0.778 | 0.861 | 1.0 |
| bm25 | 0.952 | 0.964 | 0.714 | 0.813 | 0.667 | 0.782 | 1.0 |
| tfidf | 0.81 | 0.873 | 0.476 | 0.619 | 0.5 | 0.611 | 1.0 |
| dense_lsa | 0.857 | 0.857 | 0.429 | 0.544 | 0.444 | 0.551 | 1.0 |

## Interpretation

- `tfidf` and `bm25` are transparent lexical baselines.
- `dense_lsa` is a local dense baseline using TF-IDF projected into latent semantic analysis space.
- `hybrid` is the default app mode because it combines lexical evidence and a lightweight rerank boost.
- These numbers are local regression checks, not production compliance accuracy.
