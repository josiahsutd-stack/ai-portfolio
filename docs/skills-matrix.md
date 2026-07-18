# Skills Evidence Matrix

Evidence levels refer to code, tests, and generated artifacts in this repository. Future extensions are not counted as implementation.

| Skill | Strong evidence | Supporting evidence | Not demonstrated / boundary |
| --- | --- | --- | --- |
| Python engineering | AEC RAG, Construction Embodied Agent, Real Model Lab, Agent, MLOps | All experiment modules | No large multi-service production system. |
| RAG and retrieval evaluation | AEC RAG | Agentic Research Ops | Hosted embedding/reranking quality is not evaluated. |
| Citations and abstention | AEC RAG | Agentic Research Ops | Citation checks are deterministic, not full factual verification. |
| Embodied-agent simulation | Construction Embodied Agent | Robot Task Planner, Safety Monitor | Learned action classifier over structured state; no foundation VLA, perception stack, physics, ROS, or hardware. |
| Classical model training | Real Model Lab, MLOps | Energy ML, Recommender, Time-Series | No large-scale or transformer training. |
| Agent workflows | Agentic Research Ops | BIM Issue Agent | No live web research or autonomous production tools. |
| FastAPI and schemas | MLOps | Vision, Recommender, Time-Series, VLM | Local endpoints only. |
| Persistence and observability | Agent SQLite traces, MLOps prediction logs | AEC query logs | Local development storage, not production telemetry. |
| Testing and evaluation | Full pytest suite, AEC eval, embodied-policy eval, Real Model metrics | Project smoke tests | Local runs are the primary evidence. |
| MLOps concepts | MLOps Serving and Monitoring | Real Model Lab | No hosted registry, alerting, delayed-label loop, or retraining service. |
| VLM workflow design |  | Multimodal VLM Visual QA | Mock mode does not perform visual reasoning. |
| Computer vision |  | Classical threshold baseline and metadata workflow | No trained CNN, ViT, detector, or segmentation model. |
| LoRA / transformer fine-tuning |  | Dataset and configuration workflow only | No updated neural weights or real LoRA metrics. |
| Frontend engineering | Static HTML/CSS portfolio and Streamlit demos |  | No TypeScript/React application. |
| CI/CD | GitHub Actions workflow definition and local verifier |  | A workflow file is not proof of a successful hosted run. |
