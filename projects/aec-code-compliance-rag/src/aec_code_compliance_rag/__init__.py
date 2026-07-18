from .assistant import RAGAssistant, build_assistant_from_paths
from .chunking import DocumentChunk, chunk_pdf_pages, chunk_text, load_document_chunks
from .evaluation import (
    RetrievalEvalCase,
    evaluate_retrieval,
    evaluate_retrieval_modes,
    load_eval_cases,
    validate_retrieval_eval_targets,
)
from .faithfulness import check_citation_faithfulness
from .observability import QueryLogger, ServiceTelemetryStore
from .pdf_ingestion import load_pdf_chunks
from .public_sources import download_public_sources, downloaded_public_paths
from .retrieval import (
    BM25Retriever,
    CrossEncoderRerankedRetriever,
    DenseLsaRetriever,
    HybridRetriever,
    SentenceTransformerRetriever,
    TfidfRetriever,
)
from .service import (
    QueryRequest,
    RetrieveRequest,
    ServiceMetrics,
    ServiceSettings,
    create_service_app,
    evaluate_query_objectives,
)
from .source_manifest import load_source_manifest
from .uncertainty import (
    bootstrap_mean_interval,
    build_retrieval_uncertainty,
    paired_bootstrap_mean_interval,
    wilson_score_interval,
)

__all__ = [
    "DocumentChunk",
    "RAGAssistant",
    "QueryLogger",
    "BM25Retriever",
    "DenseLsaRetriever",
    "HybridRetriever",
    "SentenceTransformerRetriever",
    "ServiceMetrics",
    "ServiceSettings",
    "ServiceTelemetryStore",
    "CrossEncoderRerankedRetriever",
    "RetrievalEvalCase",
    "TfidfRetriever",
    "QueryRequest",
    "RetrieveRequest",
    "build_assistant_from_paths",
    "check_citation_faithfulness",
    "create_service_app",
    "evaluate_query_objectives",
    "chunk_pdf_pages",
    "chunk_text",
    "evaluate_retrieval",
    "evaluate_retrieval_modes",
    "download_public_sources",
    "downloaded_public_paths",
    "load_document_chunks",
    "load_eval_cases",
    "validate_retrieval_eval_targets",
    "load_pdf_chunks",
    "load_source_manifest",
    "bootstrap_mean_interval",
    "build_retrieval_uncertainty",
    "paired_bootstrap_mean_interval",
    "wilson_score_interval",
]
