from __future__ import annotations

import json
import sys
from pathlib import Path

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT))

from aec_code_compliance_rag import ServiceSettings, create_service_app  # noqa: E402


def run_service_evaluation(output_dir: str | Path) -> dict[str, object]:
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    database_path = REPO_ROOT / ".artifacts" / "aec-rag-service-eval.sqlite"
    database_path.parent.mkdir(parents=True, exist_ok=True)
    database_path.unlink(missing_ok=True)
    settings = ServiceSettings(
        project_root=PROJECT_ROOT,
        api_key="evaluation-key",
        corpus="synthetic",
        log_path=database_path,
        store_log_payloads=False,
    )
    client = TestClient(create_service_app(settings))
    auth = {"X-API-Key": "evaluation-key"}

    live = client.get("/health/live")
    ready = client.get("/health/ready")
    missing_key = client.post("/query", json={"question": "accessible route"})
    wrong_key = client.post(
        "/query",
        headers={"X-API-Key": "wrong"},
        json={"question": "accessible route"},
    )
    answered = client.post(
        "/query",
        headers={**auth, "X-Request-ID": "service-eval-answer"},
        json={"question": "What clear width is required for an accessible route?"},
    )
    no_evidence = client.post(
        "/query",
        headers={**auth, "X-Request-ID": "service-eval-no-evidence"},
        json={"question": "What is the approved beam size for Project Atlas?"},
    )
    invalid_mode = client.post(
        "/query",
        headers=auth,
        json={"question": "accessible route", "retrieval_mode": "unknown"},
    )
    retrieved = client.post(
        "/retrieve",
        headers=auth,
        json={"question": "accessible route clear width", "k": 3},
    )
    logs = client.get("/logs/recent", headers=auth)
    metrics = client.get("/metrics", headers=auth)

    answered_body = answered.json()
    no_evidence_body = no_evidence.json()
    log_rows = logs.json()
    metrics_body = metrics.json()
    checks = {
        "liveness_is_public": live.status_code == 200 and live.json()["status"] == "alive",
        "readiness_checks_configuration_and_index": ready.status_code == 200
        and ready.json()["status"] == "ready"
        and ready.json()["document_count"] > 0,
        "missing_key_is_rejected": missing_key.status_code == 401,
        "wrong_key_is_rejected": wrong_key.status_code == 401,
        "grounded_query_is_answered": answered.status_code == 200
        and answered_body.get("status") == "answered"
        and bool(answered_body.get("sources")),
        "request_id_is_propagated": answered.headers.get("x-request-id") == "service-eval-answer"
        and answered_body.get("service", {}).get("request_id") == "service-eval-answer",
        "no_evidence_status_is_preserved": no_evidence.status_code == 200
        and no_evidence_body.get("status") == "no_evidence"
        and not no_evidence_body.get("sources"),
        "invalid_retrieval_mode_is_rejected": invalid_mode.status_code == 422,
        "retrieval_endpoint_returns_ranked_results": retrieved.status_code == 200
        and retrieved.json()["count"] == 3,
        "query_payloads_are_redacted_by_default": len(log_rows) == 2
        and all(row["question"] == "[redacted]" for row in log_rows),
        "query_logs_preserve_request_ids": {row["request_id"] for row in log_rows}
        == {"service-eval-answer", "service-eval-no-evidence"},
        "service_metrics_record_routes_and_errors": metrics.status_code == 200
        and metrics_body["requests_total"] >= 9
        and metrics_body["client_errors_total"] >= 3
        and metrics_body["requests_by_route"].get("POST /query", 0) >= 5,
    }
    payload: dict[str, object] = {
        "artifact_schema_version": 1,
        "data_status": "synthetic",
        "evaluation_scope": "in-process ASGI contract; no external deployment or user traffic",
        "checks": checks,
        "observed": {
            "check_count": len(checks),
            "passed_check_count": sum(checks.values()),
            "document_count": ready.json().get("document_count"),
            "answered_status": answered_body.get("status"),
            "answered_source_count": len(answered_body.get("sources", [])),
            "no_evidence_status": no_evidence_body.get("status"),
            "retrieved_result_count": retrieved.json().get("count"),
            "redacted_log_count": len(log_rows),
            "requests_observed_before_metrics_response": metrics_body.get("requests_total"),
            "client_errors_observed_before_metrics_response": metrics_body.get(
                "client_errors_total"
            ),
        },
        "passed": all(checks.values()),
    }
    (target / "service_contract_summary.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (target / "service_contract_report.md").write_text(
        _service_report(payload),
        encoding="utf-8",
    )
    if not payload["passed"]:
        failed = [name for name, passed in checks.items() if not passed]
        raise RuntimeError(f"service contract checks failed: {', '.join(failed)}")
    return payload


def _service_report(payload: dict[str, object]) -> str:
    checks = payload["checks"]
    observed = payload["observed"]
    assert isinstance(checks, dict)
    assert isinstance(observed, dict)
    lines = [
        "# Local Service Contract Evaluation",
        "",
        "In-process ASGI evaluation over the bundled synthetic corpus. This proves local interface behavior, not cloud deployment, operational reliability, or user adoption.",
        "",
        "| Contract check | Result |",
        "| --- | --- |",
    ]
    lines.extend(
        f"| {name.replace('_', ' ')} | {'pass' if passed else 'fail'} |"
        for name, passed in checks.items()
    )
    lines.extend(
        [
            "",
            "## Observed Evidence",
            "",
            f"- Contract checks passed: {observed['passed_check_count']}/{observed['check_count']}",
            f"- Indexed documents at readiness: {observed['document_count']}",
            f"- Grounded answer citations: {observed['answered_source_count']}",
            f"- Raw retrieval results: {observed['retrieved_result_count']}",
            f"- Redacted query-log rows: {observed['redacted_log_count']}",
            f"- Requests observed before metrics response: {observed['requests_observed_before_metrics_response']}",
            f"- Client errors observed before metrics response: {observed['client_errors_observed_before_metrics_response']}",
            "",
            "## Boundary",
            "",
            "The API key, request tracing, readiness, metrics, and local SQLite audit log are implementation evidence only. They do not establish internet exposure, secret management, distributed tracing, load capacity, availability, incident response, privacy compliance, or production security.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    payload = run_service_evaluation(PROJECT_ROOT / "demo_outputs")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
