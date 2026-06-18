# Architecture Diagrams

## AEC Code Compliance RAG Assistant

```mermaid
flowchart LR
  A["Mock AEC documents"] --> B["Chunking pipeline"]
  B --> C["Local vector store"]
  Q["User question"] --> C
  C --> D["Retrieved chunks"]
  D --> E["LLM/mock answer generator"]
  E --> F["Answer with citations"]
```

## Construction Progress CV Tracker

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
  B --> D["Candidate skill matching"]
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

