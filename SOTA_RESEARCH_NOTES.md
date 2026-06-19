# Research Notes, Not SOTA Claims

These notes summarize research and industry practices that are relevant to the repository. They are used to guide lightweight, local, testable improvements rather than to claim frontier performance. Items marked `Future only` or `Docs only` are not implemented evidence and should not be presented as incorporated capability.

## RAG

| Source | Insight | Incorporate? | Repo impact |
| --- | --- | --- | --- |
| [Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401) | RAG combines parametric generation with retrieved external knowledge and helps with provenance/updating knowledge. | Yes, locally. | AEC RAG should emphasize retrieved evidence, citations, and provenance over answer fluency. |
| [RAGAS paper](https://arxiv.org/abs/2309.15217) and [Ragas metrics docs](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/) | RAG quality should be evaluated component-wise: retrieval context, faithfulness, answer relevance, context precision/recall. | Yes, simplified. | AEC eval adds recall@k, precision@k, hit rate, MRR, citation coverage, no-answer accuracy, and simple grounding checks. |
| [HyDE](https://arxiv.org/abs/2212.10496) | Query rewriting through hypothetical documents can improve zero-shot dense retrieval but may introduce false details before grounding. | Future only. | Add as AEC productionization idea, not current implementation. |
| [GraphRAG](https://arxiv.org/abs/2404.16130) and [Microsoft GraphRAG docs](https://microsoft.github.io/graphrag/) | Graph indexes help corpus-level/global questions, but require graph extraction, community summaries, and evaluation. | Future only. | Do not brand this repo as GraphRAG until graph construction/eval exists. |

## Agents

| Source | Insight | Incorporate? | Repo impact |
| --- | --- | --- | --- |
| [ReAct](https://arxiv.org/abs/2210.03629) | Interleaving reasoning and actions improves interpretability and tool-grounded behavior. | Yes, in spirit. | Agent docs should show planner -> tools -> evidence -> report -> approval trace. |
| [Toolformer](https://arxiv.org/abs/2302.04761) | Tool use needs explicit decisions about when to call tools and how results affect outputs. | Yes, simplified. | Agent should expose tool registry, inputs, outputs, retries, and failures. |
| [Ragas agentic metrics docs](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/) | Agent workflows can be evaluated, not just manually inspected. | Yes, local. | Keep trace eval and add demo trace output. |

## MLOps

| Source | Insight | Incorporate? | Repo impact |
| --- | --- | --- | --- |
| [MLflow Model Registry](https://mlflow.org/docs/latest/ml/model-registry/) | Models need versions, metadata, aliases/tags, and lifecycle tracking. | Yes, local skeleton. | Save version, metrics, feature schema, dataset info, and git commit in metadata. |
| [Evidently drift docs](https://docs.evidentlyai.com/metrics/explainer_drift) | Drift detection compares feature distributions and should be configurable by column type and threshold. | Yes, simplified. | Add PSI-style drift alongside mean shift and document limits. |
| [Evidently custom drift docs](https://docs.evidentlyai.com/metrics/customize_data_drift) | Drift methods and thresholds should be adjustable. | Yes. | Keep drift threshold parameter and expose monitoring report warnings. |

## Fine-Tuning / LoRA

| Source | Insight | Incorporate? | Repo impact |
| --- | --- | --- | --- |
| [LoRA](https://arxiv.org/abs/2106.09685) | Low-rank adapters reduce trainable parameters and memory compared with full fine-tuning. | Docs only. | Fine-tuning lab explains LoRA config but does not claim real adaptation. |
| [QLoRA](https://arxiv.org/abs/2305.14314) | Quantized fine-tuning reduces memory needs but still requires real training/evaluation. | Docs only. | Add hardware assumptions and overfitting risks. |
| [Hugging Face PEFT LoRA docs](https://huggingface.co/docs/peft/package_reference/lora) | PEFT methods are practical but require model/task-specific configuration. | Future only. | Add template config rather than importing PEFT without use. |

## Multimodal / VLM

| Source | Insight | Incorporate? | Repo impact |
| --- | --- | --- | --- |
| [LLaVA Visual Instruction Tuning](https://arxiv.org/abs/2304.08485) | Real VLM systems need instruction data, model training/integration, and evaluation benchmarks. | Docs only. | VLM project must not imply real visual reasoning in mock mode. |
| [Improved Baselines with Visual Instruction Tuning](https://arxiv.org/abs/2310.03744) | VLM capability varies by architecture/data/eval task; benchmark context matters. | Docs only. | Add limitations and failure demo for mock VLM. |

## AEC / Built Environment

| Source | Insight | Incorporate? | Repo impact |
| --- | --- | --- | --- |
| [Automated code compliance checking with BIM and knowledge graphs](https://www.nature.com/articles/s41598-023-34342-1) | Code checking benefits from structured building data and explicit rule/knowledge representations. | Future. | AEC RAG roadmap should include BIM/jurisdiction metadata and structured rule checks. |
| [BIM, NLP, and AI for automated compliance checking](https://par.nsf.gov/biblio/10347911-chapter-building-information-modeling-natural-language-processing-artificial-intelligence-automated-compliance-checking) | Building-code compliance involves regulatory text analytics and BIM information analytics. | Yes, as framing. | Keep compliance claims cautious and traceable. |
| [Building-code RAG framework](https://www.iaarc.org/publications/csce_crc_2025/an_llm_based_framework_with_retrieval_augmented_generation_for_building_code_interpretation.html) | RAG can reduce hallucination risk for building-code interpretation but still needs careful retrieval and validation. | Yes, local. | AEC RAG focuses on retrieval eval, citations, and no-answer behavior. |

## Research Ideas Explicitly Not Added

- No GraphRAG implementation.
- No hosted embedding/reranking dependency.
- No autonomous agent claim.
- No real LoRA/QLoRA training.
- No real VLM benchmark or visual grounding claim.
- No real building-code/legal compliance claim.
