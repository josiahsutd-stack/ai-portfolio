# Retrieval Evaluation Report

Synthetic demo evaluation for the AEC Code Compliance RAG Assistant.

## Summary

- Cases: 6
- Top-k: 4
- Recall@k: 1.0
- Precision@k: 1.0
- Hit rate: 1.0
- Mean reciprocal rank: 1.0
- Section hit rate: 1.0
- Citation coverage: 1.0
- Grounding check rate: 1.0
- No-answer accuracy: 1.0

## Per-Question Results

| Question | Expected section | Retrieved chunks | Recall@k | MRR | Grounding/no-answer check | Missing terms |
| --- | --- | --- | --- | --- | --- | --- |
| What clear width should be checked for high traffic accessible routes? | Accessible Routes | mock_aec_guidance-accessible-routes-000, mock_aec_guidance-planning-review-checklist-000 | 1.0 | 1.0 | True | None |
| What doorway and threshold checks apply to accessible rooms? | Accessible Routes | mock_aec_guidance-accessible-routes-000, mock_aec_guidance-planning-review-checklist-000, mock_aec_guidance-daylight-and-glazing-guidance-000 | 1.0 | 1.0 | True | None |
| What should be included for long residential corridors? | Fire Compartment Notes | mock_aec_guidance-fire-compartment-notes-000 | 1.0 | 1.0 | True | None |
| What daylight risks should west glazing trigger? | Daylight and Glazing Guidance | mock_aec_guidance-daylight-and-glazing-guidance-000 | 1.0 | 1.0 | True | None |
| Which assumptions should be logged before a planning submission? | Planning Review Checklist | mock_aec_guidance-planning-review-checklist-000, mock_aec_guidance-synthetic-aec-code-and-design-guidance-000, mock_aec_guidance-fire-compartment-notes-000 | 1.0 | 1.0 | True | None |
| What drone landing pad radius applies to rooftop aircraft operations? | None |  | 1.0 | 1.0 | True | None |
