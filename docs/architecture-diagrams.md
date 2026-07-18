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

## Construction Progress CV Workflow Tracker

```mermaid
flowchart LR
  A["Synthetic site metadata"] --> B["Feature pipeline"]
  B --> C["Progress classifier"]
  C --> D["Stage prediction"]
  A --> E["Report generator"]
  D --> F["Dashboard/API"]
  E --> F
```

## BIM Issue Detection Agent

```mermaid
flowchart LR
  A["Mock BIM export"] --> B["Parser"]
  B --> C["Rule engine"]
  C --> D["Severity scoring"]
  D --> E["Explanation layer"]
  D --> F["Issue report"]
```

## AI + AEC Job Fit Analyzer

```mermaid
flowchart LR
  A["Job description"] --> B["Skill extraction"]
  B --> C["Role classification"]
  B --> D["Applicant profile skill matching"]
  C --> E["Fit score"]
  D --> E
  E --> F["Application strategy"]
```

## Building Energy ML Pipeline

```mermaid
flowchart LR
  A["Synthetic building data"] --> B["Feature preprocessing"]
  B --> C["Regression model"]
  C --> D["Metrics"]
  C --> E["Prediction API"]
  C --> F["Dashboard"]
```

## Spatial Design Recommender

```mermaid
flowchart LR
  A["Design constraints"] --> B["Scenario validation"]
  B --> C["Scoring function"]
  C --> D["Recommendation engine"]
  D --> E["Explainable actions"]
```

## Construction Robot Task Planner

```mermaid
flowchart LR
  A["Synthetic construction site map"] --> B["Robot task"]
  B --> C["A* route planner"]
  A --> C
  C --> D["Route steps"]
  D --> E["Payload and battery risk estimate"]
  E --> F["Dashboard/API"]
```

## Site Robot Safety Monitor

```mermaid
flowchart LR
  A["Synthetic robot telemetry"] --> B["Telemetry parser"]
  B --> C["Safety rules"]
  C --> D["Risk events"]
  D --> E["Recommended actions"]
  E --> F["Dashboard/API"]
```
