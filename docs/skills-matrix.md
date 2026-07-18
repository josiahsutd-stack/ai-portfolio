# Skills Evidence Matrix

Evidence levels refer to code, tests, and generated artifacts in this repository. Future extensions are not counted as implementation.

| Skill | Strong evidence | Supporting evidence | Not demonstrated / boundary |
| --- | --- | --- | --- |
| Python engineering | AEC RAG, Construction Embodied Agent, Local Text Classification, Research Workflow, Local Model Monitoring | All experiment modules | No large multi-service production system. |
| RAG and retrieval evaluation | AEC RAG | Deterministic Research Workflow | Hosted embedding/reranking quality is not evaluated. |
| Citations and abstention | AEC RAG | Deterministic Research Workflow | Citation checks are deterministic, not full factual verification. |
| Embodied-agent simulation | Construction Embodied Agent | Grid Route Planner, Telemetry Safety Rule Monitor | Learned action classifier over structured state; no foundation VLA, perception stack, physics, ROS, or hardware. |
| Classical model training | Local Text Classification, Local Model Monitoring | Energy Regression, Content Ranking, Time-Series Baselines | No large-scale or transformer training. |
| Tool workflows | Deterministic Research Workflow | BIM Schedule Rule Checker | Default planning is rule-based; no live web research or autonomous production tools. |
| FastAPI and schemas | Local Model Monitoring | Vision, Ranking, Time-Series, Visual Provider Contract | Local endpoints only. |
| Persistence and observability | Research Workflow SQLite traces, Local Model prediction logs | AEC query logs | Local development storage, not production telemetry. |
| Testing and evaluation | Full pytest suite, AEC eval, embodied-policy eval, Real Model metrics | Project smoke tests | Local runs are the primary evidence. |
| MLOps concepts | Local Model Serving and Monitoring | Local Text Classification Lab | No hosted registry, alerting, delayed-label loop, or retraining service. |
| Multimodal provider contracts |  | Visual QA Provider Contract | Default mock returns zero confidence and no semantic detections; no local vision model. |
| Computer vision |  | Classical threshold baseline and metadata workflow | No trained CNN, ViT, detector, or segmentation model. |
| LoRA / transformer fine-tuning |  | Dataset and configuration workflow only | No updated neural weights or real LoRA metrics. |
| Frontend engineering | Static HTML/CSS portfolio and Streamlit demos |  | No TypeScript/React application. |
| CI/CD | GitHub Actions workflow definition and local verifier |  | A workflow file is not proof of a successful hosted run. |
