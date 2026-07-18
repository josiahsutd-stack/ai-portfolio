# Language Coverage Stress Audit

**Data status:** synthetic

**Label source:** manually labeled, not blinded or independently validated

The fixed set contains 33 single-message cases: 25 positive requirement forms and 8 negative controls.

| Group | Cases | Precision | Recall | F1 | Exact-case accuracy |
| --- | ---: | ---: | ---: | ---: | ---: |
| Direct Form | 8 | 1.000 | 1.000 | 1.000 | 1.000 |
| Paraphrase | 17 | 1.000 | 0.882 | 0.938 | 0.882 |
| Negative Control | 8 | 1.000 | 1.000 | 1.000 | 1.000 |

Overall requirement extraction F1 is `0.958`; exact-case accuracy is `0.939`; negative-control accuracy is `1.000`.

This is a repository-authored coverage audit over documented forms. It is not evidence of open-domain conversation understanding, expert agreement, or professional specification quality.
