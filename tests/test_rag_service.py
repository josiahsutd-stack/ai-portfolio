import re
import sqlite3
from pathlib import Path

import pytest
from aec_code_compliance_rag import (
    QueryLogger,
    ServiceSettings,
    ServiceTelemetryStore,
    create_service_app,
    evaluate_query_objectives,
)
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
    assert metrics.json()["durable"]["payloads_stored"] is False
    assert metrics.json()["durable"]["retained_request_count"] >= 1
    assert metrics.json()["query_objectives"]["status"] == "insufficient_data"


def test_service_metrics_bound_unmatched_route_cardinality(tmp_path: Path) -> None:
    client = client_for(tmp_path)

    assert client.get("/missing/one").status_code == 404
    assert client.get("/missing/two").status_code == 404
    metrics = client.get("/metrics", headers={"X-API-Key": "test-secret"})

    assert metrics.status_code == 200
    assert metrics.json()["requests_by_route"]["GET <unmatched>"] == 2
    assert metrics.json()["durable"]["requests_by_route"]["GET <unmatched>"] == 2
    assert "GET /missing/one" not in metrics.json()["requests_by_route"]
    assert "GET /missing/one" not in metrics.json()["durable"]["requests_by_route"]


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


def test_durable_telemetry_survives_app_reconstruction_without_payloads(
    tmp_path: Path,
) -> None:
    settings = ServiceSettings(
        project_root=PROJECT_ROOT,
        api_key="test-secret",
        log_path=tmp_path / "durable.sqlite",
        query_objective_min_requests=2,
    )
    headers = {"X-API-Key": "test-secret"}
    first_client = TestClient(create_service_app(settings))

    for request_id in ("durable-001", "durable-002"):
        response = first_client.post(
            "/query",
            headers={**headers, "X-Request-ID": request_id},
            json={"question": "What clear width is required?"},
        )
        assert response.status_code == 200
    first_metrics = first_client.get("/metrics", headers=headers).json()

    second_client = TestClient(create_service_app(settings))
    restarted_metrics = second_client.get("/metrics", headers=headers).json()

    assert first_metrics["query_objectives"]["status"] == "pass"
    assert restarted_metrics["requests_total"] == 0
    assert restarted_metrics["durable"]["retained_request_count"] >= 3
    assert restarted_metrics["query_objectives"]["observed_request_count"] == 2
    assert restarted_metrics["query_objectives"]["status"] == "pass"
    with sqlite3.connect(settings.resolved_log_path()) as connection:
        columns = {
            str(row[1])
            for row in connection.execute("PRAGMA table_info(service_request)").fetchall()
        }
    assert "question" not in columns
    assert "headers" not in columns
    assert "query_string" not in columns


def test_service_telemetry_retention_is_bounded(tmp_path: Path) -> None:
    store = ServiceTelemetryStore(tmp_path / "bounded.sqlite", retention=3)
    for index in range(5):
        store.record(
            instance_id="instance-001",
            request_id=f"request-{index}",
            method="GET",
            route="/health/live",
            status_code=200,
            latency_ms=float(index),
        )

    snapshot = store.snapshot(limit=10)

    assert snapshot["retention_limit"] == 3
    assert snapshot["retained_request_count"] == 3
    assert snapshot["window_request_count"] == 3
    assert snapshot["requests_by_route"] == {"GET /health/live": 3}


def test_query_objectives_distinguish_insufficient_pass_and_fail(tmp_path: Path) -> None:
    settings = ServiceSettings(
        project_root=PROJECT_ROOT,
        api_key="test-secret",
        log_path=tmp_path / "objectives.sqlite",
        query_objective_min_requests=3,
        query_p95_latency_budget_ms=100.0,
        query_server_error_rate_budget=0.01,
    )
    base_snapshot: dict[str, object] = {
        "window_request_count": 2,
        "p95_latency_ms": 12.0,
        "server_error_rate": 0.0,
    }

    insufficient = evaluate_query_objectives(base_snapshot, settings)
    passing = evaluate_query_objectives(
        {**base_snapshot, "window_request_count": 3},
        settings,
    )
    failing = evaluate_query_objectives(
        {
            **base_snapshot,
            "window_request_count": 3,
            "p95_latency_ms": 101.0,
            "server_error_rate": 0.02,
        },
        settings,
    )

    assert insufficient["status"] == "insufficient_data"
    assert passing["status"] == "pass"
    assert failing["status"] == "fail"
    assert failing["checks"] == {
        "minimum_request_count_met": True,
        "p95_latency_budget_met": False,
        "server_error_rate_budget_met": False,
    }


def test_telemetry_write_failure_does_not_take_down_service(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    app = create_service_app(
        ServiceSettings(
            project_root=PROJECT_ROOT,
            api_key="test-secret",
            log_path=tmp_path / "write-failure.sqlite",
        )
    )

    def fail_write(**_kwargs: object) -> None:
        raise sqlite3.OperationalError("synthetic write failure")

    monkeypatch.setattr(app.state.request_telemetry, "record", fail_write)
    client = TestClient(app)

    live = client.get("/health/live")
    metrics = client.get("/metrics", headers={"X-API-Key": "test-secret"})

    assert live.status_code == 200
    assert metrics.status_code == 200
    assert metrics.json()["telemetry_write_failures"] == 1


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("telemetry_retention", 0),
        ("telemetry_window", 0),
        ("query_objective_min_requests", 0),
        ("query_p95_latency_budget_ms", 0.0),
        ("query_server_error_rate_budget", 1.1),
    ],
)
def test_invalid_service_objective_settings_are_rejected(
    tmp_path: Path,
    field: str,
    value: int | float,
) -> None:
    kwargs: dict[str, object] = {
        "project_root": PROJECT_ROOT,
        "api_key": "test-secret",
        "log_path": tmp_path / "invalid.sqlite",
        field: value,
    }
    with pytest.raises(ValueError):
        ServiceSettings(**kwargs)
