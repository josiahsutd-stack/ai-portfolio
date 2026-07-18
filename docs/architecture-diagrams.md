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

## QS Takeoff and Tender Analysis Workbench

```mermaid
flowchart LR
  A["Synthetic vector floor plan"] --> B["Scale and geometry validation"]
  B --> C["Shared-wall quantity takeoff"]
  D["Versioned synthetic rates"] --> E["Cost build-up and uncertainty"]
  C --> E
  F["Synthetic normalized tenders"] --> G["Completeness and ratio-band checks"]
  E --> G
  G --> H["Human review queue; no award recommendation"]
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

## Project Brief and Specification Copilot

```mermaid
flowchart LR
  A["Role-tagged project messages"] --> B["Requirement extraction"]
  B --> C["Versioned requirement ledger"]
  C --> D["Conflict register"]
  C --> E["Role authorization gate"]
  E --> F["Source-linked draft clauses"]
  A --> G["Append-only audit events"]
  B --> G
  D --> G
  E --> G
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
