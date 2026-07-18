import os
import re
import secrets
from collections import Counter, deque
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from threading import Lock
from time import perf_counter, time
from typing import Annotated, Any, Literal
from uuid import uuid4

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request
from pydantic import BaseModel, Field, field_validator

from .assistant import RAGAssistant, build_assistant_from_paths
from .observability import QueryLogger
from .public_sources import downloaded_public_paths

RetrievalMode = Literal[
    "tfidf",
    "bm25",
    "dense_lsa",
    "hybrid",
    "semantic",
    "hybrid_cross_encoder",
]
SourceFilterValue = str | bool | list[str]
ALLOWED_SOURCE_FILTERS = {
    "document_id",
    "jurisdiction",
    "publisher",
    "source",
    "source_type",
    "superseded",
}
REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
SERVICE_ERRORS = (ImportError, RuntimeError, ValueError)


def default_log_path(project_root: Path) -> Path:
    return project_root.parents[1] / ".artifacts" / "aec-rag" / "query_log.sqlite"


class QueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    k: int = Field(default=4, ge=1, le=10)
    retrieval_mode: RetrievalMode = "hybrid"
    source_filters: dict[str, SourceFilterValue] | None = None

    @field_validator("question")
    @classmethod
    def strip_question(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("question must contain non-whitespace characters")
        return value

    @field_validator("source_filters")
    @classmethod
    def validate_source_filters(
        cls, value: dict[str, SourceFilterValue] | None
    ) -> dict[str, SourceFilterValue] | None:
        if value is None:
            return None
        unsupported = sorted(set(value) - ALLOWED_SOURCE_FILTERS)
        if unsupported:
            raise ValueError(f"unsupported source filters: {', '.join(unsupported)}")
        return value


class RetrieveRequest(QueryRequest):
    k: int = Field(default=4, ge=1, le=20)


@dataclass(frozen=True)
class ServiceSettings:
    project_root: Path
    api_key: str | None
    corpus: str = "synthetic"
    log_path: Path | None = None
    store_log_payloads: bool = False

    def __post_init__(self) -> None:
        if self.corpus not in {"synthetic", "public"}:
            raise ValueError("corpus must be `synthetic` or `public`")

    @classmethod
    def from_environment(cls, project_root: str | Path) -> "ServiceSettings":
        root = Path(project_root)
        log_path_value = os.getenv("AEC_RAG_LOG_PATH")
        return cls(
            project_root=root,
            api_key=os.getenv("AEC_RAG_API_KEY") or None,
            corpus=os.getenv("AEC_RAG_CORPUS", "synthetic"),
            log_path=(Path(log_path_value) if log_path_value else default_log_path(root)),
            store_log_payloads=os.getenv("AEC_RAG_LOG_PAYLOADS", "false").lower()
            in {"1", "true", "yes"},
        )

    def corpus_paths(self) -> tuple[list[Path], Path | None]:
        if self.corpus == "public":
            downloaded = self.project_root / "public_sources" / "downloaded"
            return (
                downloaded_public_paths(downloaded),
                downloaded / "source_manifest.json",
            )
        sample_data = self.project_root / "sample_data"
        docs = sorted([*sample_data.glob("*.md"), *sample_data.glob("*.pdf")])
        return docs, sample_data / "source_manifest.json"

    def resolved_log_path(self) -> Path:
        return self.log_path or default_log_path(self.project_root)


class ServiceMetrics:
    def __init__(self, *, sample_limit: int = 500) -> None:
        self.started_at = time()
        self._lock = Lock()
        self._requests: Counter[str] = Counter()
        self._statuses: Counter[str] = Counter()
        self._latencies_ms: deque[float] = deque(maxlen=sample_limit)

    def record(self, *, method: str, path: str, status_code: int, latency_ms: float) -> None:
        with self._lock:
            self._requests[f"{method.upper()} {path}"] += 1
            self._statuses[str(status_code)] += 1
            self._latencies_ms.append(latency_ms)

    def snapshot(self) -> dict[str, object]:
        with self._lock:
            latencies = sorted(self._latencies_ms)
            request_counts = dict(sorted(self._requests.items()))
            status_counts = dict(sorted(self._statuses.items()))
        total = sum(request_counts.values())
        average = sum(latencies) / len(latencies) if latencies else 0.0
        p95_index = max(0, int(len(latencies) * 0.95) - 1)
        p95 = latencies[p95_index] if latencies else 0.0
        return {
            "uptime_seconds": round(max(0.0, time() - self.started_at), 3),
            "requests_total": total,
            "client_errors_total": sum(
                count for status, count in status_counts.items() if 400 <= int(status) < 500
            ),
            "server_errors_total": sum(
                count for status, count in status_counts.items() if int(status) >= 500
            ),
            "average_latency_ms": round(average, 3),
            "p95_latency_ms": round(p95, 3),
            "requests_by_route": request_counts,
            "responses_by_status": status_counts,
            "latency_sample_count": len(latencies),
        }


def create_service_app(settings: ServiceSettings) -> FastAPI:
    app = FastAPI(
        title="AEC Code Compliance RAG API",
        version="0.2.0",
        description=(
            "Local source-grounded AEC document-assistance service. "
            "Not compliance certification or professional advice."
        ),
    )
    metrics = ServiceMetrics()
    query_logger = QueryLogger(
        settings.resolved_log_path(),
        store_payloads=settings.store_log_payloads,
    )
    app.state.settings = settings
    app.state.metrics = metrics
    app.state.query_logger = query_logger

    @lru_cache(maxsize=8)
    def assistant(retrieval_mode: str) -> RAGAssistant:
        docs, manifest_path = settings.corpus_paths()
        if not docs:
            raise RuntimeError(
                "Public corpus missing. Run scripts/download_public_sources.py first."
            )
        return build_assistant_from_paths(
            docs,
            manifest_path=manifest_path,
            retrieval_mode=retrieval_mode,
        )

    def require_api_key(
        x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
    ) -> None:
        if settings.api_key is None:
            raise HTTPException(status_code=503, detail="api_key_not_configured")
        if x_api_key is None or not secrets.compare_digest(x_api_key, settings.api_key):
            raise HTTPException(
                status_code=401,
                detail="invalid_api_key",
                headers={"WWW-Authenticate": "ApiKey"},
            )

    Authenticated = Annotated[None, Depends(require_api_key)]

    @app.middleware("http")
    async def observe_request(request: Request, call_next):
        supplied_request_id = request.headers.get("X-Request-ID", "")
        request_id = (
            supplied_request_id
            if REQUEST_ID_PATTERN.fullmatch(supplied_request_id)
            else f"req_{uuid4().hex}"
        )
        request.state.request_id = request_id
        started = perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            route = request.scope.get("route")
            metrics.record(
                method=request.method,
                path=getattr(route, "path", "<unmatched>"),
                status_code=500,
                latency_ms=(perf_counter() - started) * 1000,
            )
            raise
        route = request.scope.get("route")
        metrics.record(
            method=request.method,
            path=getattr(route, "path", "<unmatched>"),
            status_code=response.status_code,
            latency_ms=(perf_counter() - started) * 1000,
        )
        response.headers["X-Request-ID"] = request_id
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.get("/health/live")
    def live() -> dict[str, str]:
        return {"status": "alive", "service": "aec-rag"}

    @app.get("/health/ready")
    def ready() -> dict[str, object]:
        if settings.api_key is None:
            raise HTTPException(status_code=503, detail="api_key_not_configured")
        docs, _manifest_path = settings.corpus_paths()
        if not docs:
            raise HTTPException(status_code=503, detail="corpus_not_available")
        try:
            assistant("hybrid")
        except SERVICE_ERRORS as exc:
            raise HTTPException(status_code=503, detail="retriever_not_ready") from exc
        return {
            "status": "ready",
            "corpus": settings.corpus,
            "document_count": len(docs),
        }

    @app.get("/sources")
    def sources(_auth: Authenticated, retrieval_mode: RetrievalMode = "hybrid"):
        try:
            return assistant(retrieval_mode).source_catalog()
        except SERVICE_ERRORS as exc:
            raise HTTPException(status_code=503, detail="retrieval_mode_unavailable") from exc

    @app.post("/query")
    def query(request: Request, payload: QueryRequest, _auth: Authenticated) -> dict[str, object]:
        started = perf_counter()
        try:
            response = assistant(payload.retrieval_mode).answer(
                payload.question,
                k=payload.k,
                source_filters=payload.source_filters,
            )
        except SERVICE_ERRORS as exc:
            latency_ms = int((perf_counter() - started) * 1000)
            query_logger.log_query(
                corpus=settings.corpus,
                retrieval_mode=payload.retrieval_mode,
                question=payload.question,
                response={"status": "error", "confidence": "low", "retrieval": {}},
                latency_ms=latency_ms,
                source_filters=payload.source_filters,
                request_id=request.state.request_id,
                error_type=type(exc).__name__,
            )
            raise HTTPException(status_code=503, detail="retrieval_mode_unavailable") from exc
        latency_ms = int((perf_counter() - started) * 1000)
        log_id = query_logger.log_query(
            corpus=settings.corpus,
            retrieval_mode=payload.retrieval_mode,
            question=payload.question,
            response=response,
            latency_ms=latency_ms,
            source_filters=payload.source_filters,
            request_id=request.state.request_id,
        )
        response["service"] = {
            "latency_ms": latency_ms,
            "query_log_id": log_id,
            "request_id": request.state.request_id,
        }
        return response

    @app.post("/retrieve")
    def retrieve(payload: RetrieveRequest, _auth: Authenticated) -> dict[str, object]:
        try:
            results = assistant(payload.retrieval_mode).retrieve(
                payload.question,
                k=payload.k,
                source_filters=payload.source_filters,
            )
        except SERVICE_ERRORS as exc:
            raise HTTPException(status_code=503, detail="retrieval_mode_unavailable") from exc
        return {
            "count": len(results),
            "results": [
                {
                    "source": result.source,
                    "score": result.score,
                    "metadata": result.metadata,
                    "excerpt": result.text[:600],
                }
                for result in results
            ],
        }

    @app.get("/logs/recent")
    def recent_logs(
        _auth: Authenticated,
        limit: Annotated[int, Query(ge=1, le=100)] = 20,
    ) -> list[dict[str, Any]]:
        return query_logger.recent(limit=limit)

    @app.get("/metrics")
    def service_metrics(_auth: Authenticated) -> dict[str, object]:
        return metrics.snapshot()

    return app
