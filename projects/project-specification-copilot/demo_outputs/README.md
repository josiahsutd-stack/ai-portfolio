# Demo Outputs

These files are deterministically generated from the bundled **synthetic** conversation fixtures:

```bash
python projects/project-specification-copilot/evaluate_specification.py
```

The Markdown specification is a human-review draft. The trace SVG is generated from the same message, requirement, and clause records; neither file is a real project artifact.

The language-stress files are generated from a separate manually labeled synthetic set:

- `language_stress_summary.json`: case-level results and explicit evidence boundaries.
- `language_stress_report.md`: group metrics for direct forms, paraphrases, and negative controls.
- `language_stress_failures.md`: retained number-word misses.
- `language_stress_comparison.svg`: generated exact-case comparison.

The stress labels are not blinded, independently validated, or representative of real project correspondence.
