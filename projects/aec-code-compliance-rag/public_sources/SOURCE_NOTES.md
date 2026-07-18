# Singapore Public Source Notes

This folder defines an optional real-source corpus for the AEC RAG project.

The repository does not commit downloaded BCA, URA, NEA, SCDF, LTA, PUB, or NParks PDFs/HTML snapshots. The downloader retrieves official public documents into `public_sources/downloaded/`, which is ignored by Git. This keeps the project useful for real-document testing while avoiding redistribution of government PDFs or modified copies.

## Source Set

| Source | Publisher | Role in the corpus |
| --- | --- | --- |
| BCA Code on Accessibility in the Built Environment 2025 | Building and Construction Authority | Accessibility, universal design, accessible routes, sanitary provisions, residential accessibility, signage, controls. |
| BCA Approved Document Version 7.07 | Building and Construction Authority | Acceptable solutions linked to Singapore Building Control performance requirements. |
| BCA Green Mark 2021 Certification Standard, 2nd Edition | Building and Construction Authority | Sustainability certification framework for Singapore buildings. |
| BCA Green Mark 2021 Energy Efficiency Technical Guide | Building and Construction Authority | Energy-efficiency evidence for Green Mark evaluation. |
| SCDF Code of Practice for Fire Precautions in Buildings 2023 | Singapore Civil Defence Force | Fire precautions, means of escape, fire safety design references. |
| URA Gross Floor Area Handbook | Urban Redevelopment Authority | GFA advisory notes and guidelines-at-a-glance for development control questions. |
| NEA Code of Practice on Environmental Health 2025 | National Environment Agency | Environmental health requirements for refuse, sanitation, ventilation, and building-plan review. |
| LTA Code of Practice for Works on Public Streets 2025 | Land Transport Authority | Street-work submission and technical requirements for development works affecting public streets. |
| LTA Code of Practice for Railway Protection 2024 | Land Transport Authority | Development and building works near railway protection zones. |
| PUB Codes of Practice and Standard Drawings | PUB, Singapore's National Water Agency | Index for drainage, coastal protection, sewerage/sanitary, and water-services codes and standard drawings. |
| PUB Code of Practice on Surface Water Drainage | PUB, Singapore's National Water Agency | Drainage requirements for new developments, platform/crest levels, drainage reserves, flood protection, and construction drainage controls. |
| PUB Code of Practice on Sewerage and Sanitary Works | PUB, Singapore's National Water Agency | Public sewer connections, sewer protection, setbacks, sanitary drainage, and pumped sewage systems. |
| NParks Guidelines on Greenery Provision and Tree Conservation for Developments | National Parks Board | Greenery provision, tree planting, tree conservation, green buffers, and development-plan clearance. |
| NParks Development Plan Submission | National Parks Board | Development-plan submission workflow for greenery and development planning at DC, BP, and CSC stages. |

## Boundary

- These files are for local retrieval and evaluation experiments only.
- The assistant is not a compliance authority and must not certify design compliance.
- Any use beyond this retrieval experiment requires verification against current BCA, URA, NEA, SCDF, LTA, PUB, NParks, CORENET, and Singapore Statutes Online sources.
- The downloader records source URLs, publisher, document version, and download timestamp in `public_sources/downloaded/source_manifest.json`.

## Usage

```bash
python projects/aec-code-compliance-rag/scripts/download_public_sources.py
python projects/aec-code-compliance-rag/scripts/evaluate_retrieval.py --corpus public
streamlit run projects/aec-code-compliance-rag/app.py
```
