# Retrieval Evaluation Report

Singapore public-source evaluation for the AEC Code Compliance RAG Assistant.

## Reproducibility Evidence

- Corpus documents: 15
- Corpus SHA-256: `f0af72d9f642a1a1bf86cbd8d1d0268bf3a4a3fa4505546655d36f7cb36dceb1`
- Eval-set SHA-256: `a2a54737b71cff6a3cddf11faead236ca99a188f62d0b7712bee5950c12cec18`
- Eval set: `public_eval_cases.jsonl`
- Machine-dependent latency is measured at runtime and omitted from committed artifacts.

## Summary

- Cases: 24
- Answerable retrieval cases: 21
- No-evidence cases: 2
- Professional-review cases: 1
- Top-k: 4
- Recall@k: 1.0
- Precision@k: 0.917
- Hit rate: 1.0
- Mean reciprocal rank: 0.976
- Section hit rate: 1.0
- Citation coverage: 0.968
- Grounding check rate: 0.905
- Status accuracy: 1.0
- Citation check pass rate: 1.0
- Answer sentence support rate: 1.0
- Unsupported answer sentence rate: 0.0
- Hit@1: 0.952
- Hit@3: 1.0
- Candidate-authored exact evidence targets: 21
- Exact evidence target Hit@1: 0.81
- Exact evidence target Hit@3: 0.952
- Exact evidence target MRR: 0.881
- Page-labeled targets: 18
- Source-page target Hit@1: 0.778
- Source-page target Hit@3: 0.944
- Source-page target MRR: 0.861
- No-answer accuracy: 1.0
- Unsupported-scope accuracy: 1.0

## Results By Case Type

| Case type | Cases | Answerable | Document MRR | Exact-target n | Exact Hit@1 | Exact MRR | Status accuracy |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| public_source_direct | 15 | 15 | 1.0 | 15 | 0.867 | 0.9 | 1.0 |
| public_source_negative | 1 | 0 | None | 0 | None | None | 1.0 |
| public_source_no_evidence | 2 | 0 | None | 0 | None | None | 1.0 |
| public_source_paraphrase | 6 | 6 | 0.917 | 6 | 0.667 | 0.833 | 1.0 |

## Per-Question Results

| ID | Type | Question | Expected status | Actual status | Retrieved chunks | Document MRR | Exact-target MRR | Page-target MRR | Grounding/no-answer check | Missing terms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| sg-001 | public_source_direct | What does the BCA Code on Accessibility 2025 set out for accessible and inclusive buildings? | answered | answered | bca_code_on_accessibility_2025-code-on-accessibility-in-the-built-environment-2025-p9-000, bca_code_on_accessibility_2025-8-i-n-t-r-o-d-u-c-t-i-o-n-p8-000, bca_code_on_accessibility_2025-8-i-n-t-r-o-d-u-c-t-i-o-n-p8-001, bca_code_on_accessibility_2025-code-on-accessibility-in-the-built-environment-2025-p61-000 | 1.0 | 0.5 | 0.5 | True | None |
| sg-002 | public_source_direct | Who does BCA say should integrate accessibility and usability considerations from the onset of a building project? | answered | answered | bca_code_on_accessibility_2025-8-i-n-t-r-o-d-u-c-t-i-o-n-p8-001, bca_code_on_accessibility_2025-8-i-n-t-r-o-d-u-c-t-i-o-n-p8-000, bca_green_mark_2021_certification_standard_2nd_ed-page-12-of-33-p12-000, bca_green_mark_2021_certification_standard_2nd_ed-page-11-of-33-p11-002 | 1.0 | 1.0 | 1.0 | True | None |
| sg-003 | public_source_direct | What does the BCA Approved Document provide for prescribed objectives and performance requirements? | answered | answered | bca_approved_document_v7_07-building-and-construction-authority-page-1-of-65-p24-001, bca_approved_document_v7_07-building-and-construction-authority-page-1-of-65-p24-000, bca_approved_document_v7_07-building-and-construction-authority-page-1-of-65-p24-002, bca_approved_document_v7_07-building-and-construction-authority-page-52-of-62-p75-001 | 1.0 | 1.0 | 1.0 | True | None |
| sg-004 | public_source_direct | Which BCA document contains the Green Mark 2021 certification standard? | answered | answered | bca_green_mark_2021_certification_standard_2nd_ed-page-10-of-33-p10-003, bca_green_mark_2021_certification_standard_2nd_ed-page-10-of-33-p10-002, bca_green_mark_2021_certification_standard_2nd_ed-page-2-of-33-p2-000, bca_green_mark_2021_certification_standard_2nd_ed-certification-standard-p1-000 | 1.0 | 1.0 | 1.0 | True | None |
| sg-005 | public_source_direct | What is the SCDF Fire Code 2023 used for in Singapore building fire safety design? | answered | answered | scdf_fire_code_2023-code-of-practice-for-fire-p1-000, scdf_fire_code_2023-amendment-history-chapter-3-structural-fire-precautions-p109-005, scdf_fire_code_2023-amendment-history-chapter-1-general-p31-000, scdf_fire_code_2023-clause-11-3-assessment-and-validation-p253-004 | 1.0 | 0.0 | 0.0 | True | None |
| sg-006 | public_source_negative | Can this assistant certify a Singapore building plan for BCA approval? | needs_professional_review | needs_professional_review |  | 0.0 | None | None | True | None |
| sg-007 | public_source_direct | What does URA say the Gross Floor Area handbook advisory notes are not exhaustive about? | answered | answered | ura_gfa_handbook_advisory_notes-gross-floor-area-000, ura_gfa_handbook_advisory_notes-ura-gfa-handbook-advisory-notes-000, ura_gfa_handbook_advisory_notes-ura-gross-floor-area-handbook-advisory-notes-000, ura_gfa_handbook_advisory_notes-gross-floor-area-002 | 1.0 | 1.0 | None | True | None |
| sg-008 | public_source_direct | Which URA GFA glance source lists items excluded, partially excluded, included, and over Master Plan control? | answered | answered | ura_gfa_guidelines_at_a_glance-guidelines-at-a-glance-gross-floor-area-p1-000, ura_gfa_guidelines_at_a_glance-items-excluded-from-p2-000, ura_gfa_guidelines_at_a_glance-items-excluded-from-p3-000, ura_gfa_guidelines_at_a_glance-items-excluded-from-p2-001 | 1.0 | 1.0 | 1.0 | True | None |
| sg-009 | public_source_direct | What does NEA COPEH say residential buildings taller than four storeys need for refuse? | answered | answered | nea_code_of_practice_environmental_health_2025-code-of-practice-on-environmental-health-2025-edition-p7-002, nea_code_of_practice_environmental_health_2025-code-of-practice-on-environmental-health-2025-edition-p33-003, nea_code_of_practice_environmental_health_2025-code-of-practice-on-environmental-health-2025-edition-p11-004, nea_code_of_practice_environmental_health_2025-code-of-practice-on-environmental-health-2025-edition-p8-001 | 1.0 | 1.0 | 1.0 | True | None |
| sg-010 | public_source_direct | What does the LTA works on public streets code set out for permits and technical requirements? | answered | answered | lta_code_of_practice_works_on_public_streets_2025-code-of-practice-for-works-on-public-streets-12-p12-001, lta_code_of_practice_works_on_public_streets_2025-code-of-practice-for-works-on-public-streets-54-p54-000, lta_code_of_practice_works_on_public_streets_2025-code-of-practice-for-works-on-public-streets-7-p7-001, lta_code_of_practice_works_on_public_streets_2025-code-of-practice-for-works-on-public-streets-40-p40-000 | 1.0 | 1.0 | 1.0 | True | None |
| sg-011 | public_source_direct | What does the LTA railway protection code cover for development and building proposals? | answered | answered | lta_code_of_practice_railway_protection_2024-21-p-a-g-e-p22-000, lta_code_of_practice_railway_protection_2024-64-p-a-g-e-p65-000, lta_code_of_practice_railway_protection_2024-4-p-a-g-e-p5-000, lta_code_of_practice_railway_protection_2024-2024-edition-p1-000 | 1.0 | 1.0 | 1.0 | True | None |
| sg-012 | public_source_direct | Which PUB resource page lists the Code of Practice on Coastal Protection and says new requirements take effect in 2028? | answered | answered | pub_codes_of_practice_and_standard_drawings-codes-of-practice-and-standard-drawings-003, pub_codes_of_practice_and_standard_drawings-codes-of-practice-and-standard-drawings-001, pub_codes_of_practice_and_standard_drawings-codes-of-practice-and-standard-drawings-005, pub_codes_of_practice_and_standard_drawings-codes-of-practice-and-standard-drawings-002 | 1.0 | 1.0 | None | True | None |
| sg-013 | public_source_direct | What does PUB's Surface Water Drainage code specify for new developments? | answered | answered | pub_surface_water_drainage_cop_2025-1-p20-002, pub_surface_water_drainage_cop_2025-26-p45-000, pub_surface_water_drainage_cop_2025-code-of-practice-p1-000, pub_surface_water_drainage_cop_2025-ii-p2-000 | 1.0 | 1.0 | 1.0 | True | None |
| sg-014 | public_source_direct | Before design starts, what PUB sewerage information must be obtained for sewers and pumping mains? | answered | answered | pub_sewerage_sanitary_works_2025-1-p-a-g-e-p9-000, pub_sewerage_sanitary_works_2025-42-p-a-g-e-p50-000, pub_sewerage_sanitary_works_2025-42-p-a-g-e-p50-001, pub_sewerage_sanitary_works_2025-14-p-a-g-e-p22-002 | 1.0 | 1.0 | 1.0 | True | None |
| sg-015 | public_source_direct | What do NParks greenery provision and tree conservation guidelines describe for development projects in Singapore? | answered | answered | nparks_greenery_tree_conservation_2025-1-p9-000, nparks_greenery_tree_conservation_2025-80-p80-000, nparks_greenery_tree_conservation_2025-152-p152-000, nparks_greenery_tree_conservation_2025-iguidelines-on-greenery-provision-and-tree-conservation-for-developments-p4-000 | 1.0 | 1.0 | 1.0 | True | None |
| sg-016 | public_source_direct | Which project stages does the NParks Greenery and Development Planning Branch work with developers and QPs on? | answered | answered | nparks_development_plan_submission-development-plan-submission-000, nparks_greenery_tree_conservation_2025-1-p9-000, nparks_development_plan_submission-nparks-development-plan-submission-000, nparks_greenery_tree_conservation_2025-154-p154-000 | 1.0 | 1.0 | None | True | None |
| sg-017 | public_source_paraphrase | A proposal includes new and altered buildings. Which reference sets baseline access expectations for disabled users, older adults, and families with young children? | answered | answered | bca_code_on_accessibility_2025-8-i-n-t-r-o-d-u-c-t-i-o-n-p8-004, bca_code_on_accessibility_2025-code-on-accessibility-in-the-built-environment-2025-p18-000, bca_code_on_accessibility_2025-code-on-accessibility-in-the-built-environment-2025-p86-000, bca_code_on_accessibility_2025-8-i-n-t-r-o-d-u-c-t-i-o-n-p8-003 | 1.0 | 1.0 | 1.0 | False | baseline requirements |
| sg-018 | public_source_paraphrase | Where should a designer check whether balconies, covered walkways, service ducts, and similar spaces count toward development intensity? | answered | answered | scdf_fire_code_2023-clause-3-5-external-wall-p60-011, ura_gfa_guidelines_at_a_glance-guidelines-at-a-glance-gross-floor-area-p1-000, lta_code_of_practice_railway_protection_2024-59-p-a-g-e-p60-000, ura_gfa_handbook_advisory_notes-gross-floor-area-002 | 0.5 | 0.5 | 0.5 | True | None |
| sg-019 | public_source_paraphrase | Which local reference covers submissions when excavation or construction may affect a protected rail corridor? | answered | answered | lta_code_of_practice_railway_protection_2024-21-p-a-g-e-p22-000, lta_code_of_practice_railway_protection_2024-86-p-a-g-e-p87-000, lta_code_of_practice_railway_protection_2024-86-p-a-g-e-p87-001, lta_code_of_practice_railway_protection_2024-31-p-a-g-e-p32-000 | 1.0 | 1.0 | 1.0 | True | None |
| sg-020 | public_source_paraphrase | Which guide should a qualified person consult before designing platform levels and flood-protection measures for a new development? | answered | answered | pub_surface_water_drainage_cop_2025-7-p26-002, pub_surface_water_drainage_cop_2025-8-p27-001, pub_surface_water_drainage_cop_2025-8-p27-002, pub_surface_water_drainage_cop_2025-46-p65-000 | 1.0 | 1.0 | 1.0 | False | new developments |
| sg-021 | public_source_paraphrase | Which guidance combines green buffers, tree conservation, and development-plan clearance procedures? | answered | answered | nparks_greenery_tree_conservation_2025-59-p59-000, nparks_greenery_tree_conservation_2025-156-p156-000, nparks_greenery_tree_conservation_2025-49-p49-000, nparks_greenery_tree_conservation_2025-160guidelines-on-greenery-provision-and-tree-conservation-for-developments-p160-000 | 1.0 | 0.5 | 0.5 | True | None |
| sg-022 | public_source_paraphrase | A residential block is more than four storeys high. Which environmental-health source addresses its refuse-chute provision? | answered | answered | nea_code_of_practice_environmental_health_2025-code-of-practice-on-environmental-health-2025-edition-p7-002, nea_code_of_practice_environmental_health_2025-code-of-practice-on-environmental-health-2025-edition-p33-003, nea_code_of_practice_environmental_health_2025-code-of-practice-on-environmental-health-2025-edition-p8-002, nea_code_of_practice_environmental_health_2025-code-of-practice-on-environmental-health-2025-edition-p8-001 | 1.0 | 1.0 | 1.0 | True | None |
| sg-023 | public_source_no_evidence | What exact gross floor area was granted for parcel MK01-99999? | no_evidence | no_evidence | ura_gfa_handbook_advisory_notes-gross-floor-area-000, ura_gfa_handbook_advisory_notes-gross-floor-area-001, ura_gfa_handbook_advisory_notes-ura-gfa-handbook-advisory-notes-000, ura_gfa_handbook_advisory_notes-gross-floor-area-003 | 1.0 | None | None | True | None |
| sg-024 | public_source_no_evidence | What structural load capacity applies to an unnamed tower transfer slab? | no_evidence | no_evidence | nea_code_of_practice_environmental_health_2025-code-of-practice-on-environmental-health-2025-edition-p45-000, nea_code_of_practice_environmental_health_2025-contents-p3-001, nea_code_of_practice_environmental_health_2025-code-of-practice-on-environmental-health-2025-edition-p46-000, nea_code_of_practice_environmental_health_2025-contents-p3-000 | 1.0 | None | None | True | None |
