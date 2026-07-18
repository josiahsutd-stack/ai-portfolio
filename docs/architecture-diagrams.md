# Architecture Diagrams

## AEC Code Compliance RAG Assistant

```mermaid
flowchart LR
  A["Synthetic guidance or local public documents"] --> B["Page and section-aware chunking"]
  M["Source manifest and authority metadata"] --> B
  B --> C["TF-IDF, BM25, dense LSA, or hybrid retrieval"]
  Q["Question and optional source filters"] --> C
  C --> D["Ranked evidence chunks"]
  D --> E["Grounded response or abstention"]
  E --> F["Citations, status, and eval artifacts"]
```

## Construction Progress Metadata Classifier

```mermaid
flowchart LR
  A["Synthetic site metadata"] --> B["Feature pipeline"]
  B --> C["Progress classifier"]
  C --> D["Stage prediction"]
  A --> E["Report generator"]
  D --> F["Dashboard/API"]
  E --> F
```

## BIM Schedule Rule Checker

```mermaid
flowchart LR
  A["Mock BIM export"] --> B["Parser"]
  B --> C["Rule engine"]
  C --> D["Severity scoring"]
  D --> E["Explanation layer"]
  D --> F["Issue report"]
```

## AI/AEC Job Description Match Baseline

```mermaid
flowchart LR
  A["Job description"] --> B["Skill extraction"]
  B --> C["Role classification"]
  B --> D["Applicant profile skill matching"]
  C --> E["Fit score"]
  D --> E
  E --> F["Application strategy"]
```

## Building Energy Regression Pipeline

```mermaid
flowchart LR
  A["Synthetic building data"] --> B["Feature preprocessing"]
  B --> C["Regression model"]
  C --> D["Metrics"]
  C --> E["Prediction API"]
  C --> F["Dashboard"]
```

## Constraint-Aware Massing Explorer

```mermaid
flowchart LR
  A["Synthetic or user-supplied numeric constraints"] --> B["Scenario validation"]
  B --> C["Seeded massing typologies"]
  C --> D["Hard-constraint checks"]
  D --> E["Environmental and access proxies"]
  E --> F["Pareto front and weighted ranking"]
  F --> G["Evaluated geometry and SVG comparison"]
```

## Construction Grid Route Planner

```mermaid
flowchart LR
  A["Synthetic construction site map"] --> B["Robot task"]
  B --> C["A* route planner"]
  A --> C
  C --> D["Route steps"]
  D --> E["Payload and battery risk estimate"]
  E --> F["Dashboard/API"]
```

## Robot Telemetry Safety Rule Monitor

```mermaid
flowchart LR
  A["Synthetic robot telemetry"] --> B["Telemetry parser"]
  B --> C["Safety rules"]
  C --> D["Risk events"]
  D --> E["Recommended actions"]
  E --> F["Dashboard/API"]
```
