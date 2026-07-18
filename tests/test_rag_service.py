import re
import sqlite3
from pathlib import Path

from aec_code_compliance_rag import QueryLogger, ServiceSettings, create_service_app
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1] / "projects" / "aec-code-compliance-rag"


def client_for(tmp_path: Path, *, api_key: str | None = "test-secret") -> TestClient:
    settings = ServiceSettings(
        project_root=PROJECT_ROOT,
        api_key=api_key,
        log_path=tmp_path / "query_log.sqlite",
    )
    return TestClient(create_service_app(settings))


def test_service_fails_closed_without_api_key(tmp_path: Path) -> None:
    client = client_for(tmp_path, api_key=None)

    assert client.get("/health/live").status_code == 200
    assert client.get("/health/ready").status_code == 503
    response = client.post("/query", json={"question": "What is an accessible route?"})

    assert response.status_code == 503
    assert response.json()["detail"] == "api_key_not_configured"


def test_service_rejects_missing_and_invalid_api_keys(tmp_path: Path) -> None:
    client = client_for(tmp_path)

    missing = client.get("/sources")
    invalid = client.get("/sources", headers={"X-API-Key": "wrong"})

    assert missing.status_code == 401
    assert invalid.status_code == 401
    assert missing.headers["www-authenticate"] == "ApiKey"


def test_authorized_query_is_traced_and_redacted_by_default(tmp_path: Path) -> None:
    client = client_for(tmp_path)
    headers = {"X-API-Key": "test-secret", "X-Request-ID": "test-query-001"}

    response = client.post(
        "/query",
        headers=headers,
        json={"question": "What clear width is required for an accessible route?"},
    )
    logs = client.get("/logs/recent", headers={"X-API-Key": "test-secret"})

    assert response.status_code == 200
    assert response.headers["x-request-id"] == "test-query-001"
    assert response.headers["cache-control"] == "no-store"
    assert response.json()["status"] == "answered"
    assert response.json()["sources"]
    assert response.json()["service"]["request_id"] == "test-query-001"
    assert logs.status_code == 200
    assert logs.json()[0]["question"] == "[redacted]"
    assert logs.json()[0]["request_id"] == "test-query-001"
    assert logs.json()[0]["status"] == "answered"


def test_service_validates_modes_filters_and_questions(tmp_path: Path) -> None:
    client = client_for(tmp_path)
    headers = {"X-API-Key": "test-secret"}

    invalid_mode = client.post(
        "/query",
        headers=headers,
        json={"question": "route", "retrieval_mode": "unknown"},
    )
    invalid_filter = client.post(
        "/query",
        headers=headers,
        json={"question": "route", "source_filters": {"secret_field": "x"}},
    )
    empty_question = client.post(
        "/query",
        headers=headers,
        json={"question": "   "},
    )

    assert invalid_mode.status_code == 422
    assert invalid_filter.status_code == 422
    assert empty_question.status_code == 422


def test_service_metrics_capture_routes_and_sanitize_request_ids(tmp_path: Path) -> None:
    client = client_for(tmp_path)
    response = client.get(
        "/sources",
        headers={"X-API-Key": "test-secret", "X-Request-ID": "invalid id with spaces"},
    )
    metrics = client.get("/metrics", headers={"X-API-Key": "test-secret"})

    assert response.status_code == 200
    assert re.fullmatch(r"req_[0-9a-f]{32}", response.headers["x-request-id"])
    assert metrics.status_code == 200
    assert metrics.json()["requests_total"] >= 1
    assert metrics.json()["requests_by_route"]["GET /sources"] == 1
    assert metrics.json()["responses_by_status"]["200"] >= 1


def test_service_metrics_bound_unmatched_route_cardinality(tmp_path: Path) -> None:
    client = client_for(tmp_path)

    assert client.get("/missing/one").status_code == 404
    assert client.get("/missing/two").status_code == 404
    metrics = client.get("/metrics", headers={"X-API-Key": "test-secret"})

    assert metrics.status_code == 200
    assert metrics.json()["requests_by_route"]["GET <unmatched>"] == 2
    assert "GET /missing/one" not in metrics.json()["requests_by_route"]


def test_public_corpus_readiness_fails_when_downloads_are_missing(tmp_path: Path) -> None:
    settings = ServiceSettings(
        project_root=tmp_path,
        api_key="test-secret",
        corpus="public",
        log_path=tmp_path / "query_log.sqlite",
    )
    client = TestClient(create_service_app(settings))

    response = client.get("/health/ready")

    assert response.status_code == 503
    assert response.json()["detail"] == "corpus_not_available"


def test_query_logger_migrates_legacy_schema(tmp_path: Path) -> None:
    path = tmp_path / "legacy.sqlite"
    with sqlite3.connect(path) as connection:
        connection.execute("""
            CREATE TABLE query_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                corpus TEXT NOT NULL,
                retrieval_mode TEXT NOT NULL,
                question TEXT NOT NULL,
                status TEXT NOT NULL,
                confidence TEXT NOT NULL,
                result_count INTEGER NOT NULL,
                latency_ms INTEGER NOT NULL,
                source_filters_json TEXT NOT NULL,
                response_json TEXT NOT NULL
            )
            """)

    logger = QueryLogger(path)
    logger.log_query(
        corpus="synthetic",
        retrieval_mode="hybrid",
        question="private project question",
        response={"status": "no_evidence", "confidence": "low", "retrieval": {}},
        latency_ms=3,
        request_id="migration-001",
    )

    record = logger.recent(limit=1)[0]
    assert record["request_id"] == "migration-001"
    assert record["operation"] == "query"
    assert record["error_type"] == ""
    assert record["question"] == "[redacted]"


def test_failed_query_is_recorded_without_payloads(tmp_path: Path) -> None:
    settings = ServiceSettings(
        project_root=tmp_path,
        api_key="test-secret",
        corpus="public",
        log_path=tmp_path / "query_log.sqlite",
    )
    client = TestClient(create_service_app(settings))
    headers = {"X-API-Key": "test-secret", "X-Request-ID": "failed-query-001"}

    response = client.post(
        "/query",
        headers=headers,
        json={"question": "Which document applies?"},
    )
    logs = client.get("/logs/recent", headers={"X-API-Key": "test-secret"})

    assert response.status_code == 503
    assert logs.status_code == 200
    assert logs.json()[0]["status"] == "error"
    assert logs.json()[0]["error_type"] == "RuntimeError"
    assert logs.json()[0]["request_id"] == "failed-query-001"
    assert logs.json()[0]["question"] == "[redacted]"


def test_query_logger_payload_storage_requires_explicit_opt_in(tmp_path: Path) -> None:
    logger = QueryLogger(tmp_path / "payloads.sqlite", store_payloads=True)
    logger.log_query(
        corpus="synthetic",
        retrieval_mode="hybrid",
        question="review this exact question",
        response={"status": "answered", "confidence": "medium", "retrieval": {}},
        latency_ms=4,
        request_id="payload-opt-in-001",
    )

    record = logger.recent(limit=1)[0]
    assert record["question"] == "review this exact question"
    assert record["response"]["status"] == "answered"
