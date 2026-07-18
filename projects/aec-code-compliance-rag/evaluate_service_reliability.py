from __future__ import annotations

import asyncio
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any

import httpx

PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT))

from aec_code_compliance_rag import ServiceSettings, create_service_app  # noqa: E402

WORKLOAD_REQUESTS = 48
MAX_CONCURRENCY = 8
P95_LATENCY_BUDGET_MS = 500.0
SERVER_ERROR_RATE_BUDGET = 0.01
QUESTIONS = (
    "What clear width is required for an accessible route?",
    "What does the sample guidance say about exit access travel distance?",
    "Which source discusses sanitary discharge requirements?",
    "What is the approved beam size for Project Atlas?",
)


async def _run_workload(
    app: Any,
    *,
    request_count: int,
    concurrency: int,
) -> tuple[httpx.Response, list[httpx.Response], httpx.Response]:
    transport = httpx.ASGITransport(app=app)
    auth = {"X-API-Key": "reliability-evaluation-key"}
    semaphore = asyncio.Semaphore(concurrency)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://local-evaluation",
        timeout=30.0,
    ) as client:
        ready = await client.get("/health/ready")

        async def query(index: int) -> httpx.Response:
            async with semaphore:
                return await client.post(
                    "/query",
                    headers={
                        **auth,
                        "X-Request-ID": f"reliability-{index:03d}",
                    },
                    json={"question": QUESTIONS[index % len(QUESTIONS)]},
                )

        responses = await asyncio.gather(*(query(index) for index in range(request_count)))
        metrics = await client.get("/metrics", headers=auth)
    return ready, responses, metrics


async def _read_restarted_metrics(app: Any) -> httpx.Response:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://local-evaluation",
        timeout=30.0,
    ) as client:
        return await client.get(
            "/metrics",
            headers={"X-API-Key": "reliability-evaluation-key"},
        )


def _remove_sqlite_files(path: Path) -> None:
    for candidate in (path, Path(f"{path}-wal"), Path(f"{path}-shm")):
        candidate.unlink(missing_ok=True)


def run_service_reliability_evaluation(
    output_dir: str | Path,
    *,
    request_count: int = WORKLOAD_REQUESTS,
    concurrency: int = MAX_CONCURRENCY,
    p95_latency_budget_ms: float = P95_LATENCY_BUDGET_MS,
    server_error_rate_budget: float = SERVER_ERROR_RATE_BUDGET,
) -> tuple[dict[str, object], dict[str, float]]:
    if request_count < 1:
        raise ValueError("request_count must be at least 1")
    if not 1 <= concurrency <= request_count:
        raise ValueError("concurrency must be between 1 and request_count")
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    database_path = REPO_ROOT / ".artifacts" / "aec-rag-reliability-eval.sqlite"
    database_path.parent.mkdir(parents=True, exist_ok=True)
    _remove_sqlite_files(database_path)
    telemetry_window = max(100, request_count)
    settings = ServiceSettings(
        project_root=PROJECT_ROOT,
        api_key="reliability-evaluation-key",
        corpus="synthetic",
        log_path=database_path,
        store_log_payloads=False,
        telemetry_retention=5000,
        telemetry_window=telemetry_window,
        query_objective_min_requests=request_count,
        query_p95_latency_budget_ms=p95_latency_budget_ms,
        query_server_error_rate_budget=server_error_rate_budget,
    )
    app = create_service_app(settings)
    ready, responses, metrics_response = asyncio.run(
        _run_workload(
            app,
            request_count=request_count,
            concurrency=concurrency,
        )
    )
    metrics = metrics_response.json()
    query_objectives = metrics["query_objectives"]

    restarted_app = create_service_app(settings)
    restarted_metrics_response = asyncio.run(_read_restarted_metrics(restarted_app))
    restarted_metrics = restarted_metrics_response.json()
    restarted_objectives = restarted_metrics["query_objectives"]

    status_codes = [response.status_code for response in responses]
    response_request_ids = [response.headers.get("x-request-id") for response in responses]
    successful_responses = sum(status == 200 for status in status_codes)
    server_error_count = sum(status >= 500 for status in status_codes)
    with sqlite3.connect(database_path) as connection:
        query_log_count = int(connection.execute("SELECT COUNT(*) FROM query_log").fetchone()[0])
        redacted_query_count = int(
            connection.execute(
                "SELECT COUNT(*) FROM query_log WHERE question = '[redacted]'"
            ).fetchone()[0]
        )
        telemetry_columns = {
            str(row[1])
            for row in connection.execute("PRAGMA table_info(service_request)").fetchall()
        }

    checks = {
        "readiness_warms_index": ready.status_code == 200 and ready.json().get("status") == "ready",
        "all_workload_requests_return_200": successful_responses == request_count,
        "request_ids_remain_unique_and_propagated": len(set(response_request_ids)) == request_count
        and None not in response_request_ids,
        "query_logs_are_complete_and_redacted": query_log_count == request_count
        and redacted_query_count == request_count,
        "no_server_errors_in_workload": server_error_count == 0,
        "p95_latency_budget_is_met": query_objectives["checks"]["p95_latency_budget_met"],
        "server_error_rate_budget_is_met": query_objectives["checks"][
            "server_error_rate_budget_met"
        ],
        "query_objective_has_sufficient_data": query_objectives["checks"][
            "minimum_request_count_met"
        ],
        "durable_query_count_matches_workload": query_objectives["observed_request_count"]
        == request_count,
        "durable_telemetry_survives_app_reconstruction": restarted_objectives[
            "observed_request_count"
        ]
        == request_count,
        "process_metrics_reset_on_app_reconstruction": restarted_metrics["requests_total"] == 0,
        "objective_status_survives_app_reconstruction": restarted_objectives["status"] == "pass",
        "telemetry_schema_excludes_request_payloads": not {
            "question",
            "headers",
            "query_string",
            "body",
        }
        & telemetry_columns,
        "telemetry_writes_succeed": metrics["telemetry_write_failures"] == 0
        and restarted_metrics["telemetry_write_failures"] == 0,
    }
    payload: dict[str, object] = {
        "artifact_schema_version": 1,
        "data_status": "synthetic",
        "evaluation_scope": (
            "fixed concurrent in-process ASGI workload after local index warm-up; "
            "no network, external deployment, sustained load, or user traffic"
        ),
        "workload": {
            "request_count": request_count,
            "max_concurrency": concurrency,
            "question_count": len(QUESTIONS),
            "corpus": "bundled synthetic",
        },
        "objectives": {
            "minimum_query_requests": request_count,
            "p95_latency_budget_ms": p95_latency_budget_ms,
            "server_error_rate_budget": server_error_rate_budget,
            "status": query_objectives["status"],
            "p95_latency_budget_passed": query_objectives["checks"]["p95_latency_budget_met"],
            "server_error_rate_budget_passed": query_objectives["checks"][
                "server_error_rate_budget_met"
            ],
        },
        "observed": {
            "check_count": len(checks),
            "passed_check_count": sum(checks.values()),
            "successful_response_count": successful_responses,
            "server_error_count": server_error_count,
            "server_error_rate": query_objectives["observed_server_error_rate"],
            "unique_response_request_id_count": len(set(response_request_ids)),
            "redacted_query_log_count": redacted_query_count,
            "durable_query_count_before_app_reconstruction": query_objectives[
                "observed_request_count"
            ],
            "durable_query_count_after_app_reconstruction": restarted_objectives[
                "observed_request_count"
            ],
            "durable_request_rows_after_app_reconstruction": restarted_metrics["durable"][
                "retained_request_count"
            ],
            "process_request_count_after_app_reconstruction": restarted_metrics["requests_total"],
            "telemetry_retention_limit": restarted_metrics["durable"]["retention_limit"],
            "versioned_latency_result": (
                f"p95_at_or_below_{p95_latency_budget_ms:g}_ms"
                if query_objectives["checks"]["p95_latency_budget_met"]
                else f"p95_above_{p95_latency_budget_ms:g}_ms"
            ),
        },
        "checks": checks,
        "passed": all(checks.values()),
    }
    runtime_measurements = {
        "observed_query_p95_latency_ms": float(query_objectives["observed_p95_latency_ms"]),
        "observed_query_server_error_rate": float(query_objectives["observed_server_error_rate"]),
    }
    (target / "service_reliability_summary.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (target / "service_reliability_report.md").write_text(
        _service_reliability_report(payload),
        encoding="utf-8",
    )
    if not payload["passed"]:
        failed = [name for name, passed in checks.items() if not passed]
        raise RuntimeError(f"service reliability checks failed: {', '.join(failed)}")
    return payload, runtime_measurements


def _service_reliability_report(payload: dict[str, object]) -> str:
    workload = payload["workload"]
    objectives = payload["objectives"]
    observed = payload["observed"]
    checks = payload["checks"]
    assert isinstance(workload, dict)
    assert isinstance(objectives, dict)
    assert isinstance(observed, dict)
    assert isinstance(checks, dict)
    lines = [
        "# Local Service Reliability Evaluation",
        "",
        "Fixed concurrent in-process ASGI evaluation over the bundled synthetic corpus. It exercises local persistence and objective logic; it is not external load testing, availability evidence, or a production SLO.",
        "",
        "## Workload",
        "",
        f"- Requests: {workload['request_count']}",
        f"- Maximum concurrency: {workload['max_concurrency']}",
        f"- Distinct questions: {workload['question_count']}",
        "- The hybrid index is warmed through readiness before timing the query workload.",
        "",
        "## Objective Result",
        "",
        f"- Status: `{objectives['status']}`",
        f"- P95 latency budget: at or below `{objectives['p95_latency_budget_ms']}` ms - {'pass' if objectives['p95_latency_budget_passed'] else 'fail'}",
        f"- Server-error-rate budget: at or below `{objectives['server_error_rate_budget']}` - {'pass' if objectives['server_error_rate_budget_passed'] else 'fail'}",
        f"- Successful responses: `{observed['successful_response_count']}/{workload['request_count']}`",
        f"- Server errors: `{observed['server_error_count']}`",
        f"- Durable query rows after app reconstruction: `{observed['durable_query_count_after_app_reconstruction']}`",
        f"- Process request count after app reconstruction: `{observed['process_request_count_after_app_reconstruction']}`",
        "",
        "Exact wall-clock latency is printed at runtime but is not committed because it is machine-dependent. The versioned artifact records only whether the fixed local budget was met.",
        "",
        "## Contract Checks",
        "",
        "| Check | Result |",
        "| --- | --- |",
    ]
    lines.extend(
        f"| {name.replace('_', ' ')} | {'pass' if passed else 'fail'} |"
        for name, passed in checks.items()
    )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "Telemetry stores timestamp, service-instance id, bounded request id, method, route template, status, and latency. It does not store arbitrary headers, query strings, questions, or response bodies. The SQLite file is a local durability mechanism, not a distributed metrics backend. This evaluation does not demonstrate TLS, identity-aware authorization, multi-process aggregation, autoscaling, sustained capacity, incident response, or external availability.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    payload, runtime_measurements = run_service_reliability_evaluation(
        PROJECT_ROOT / "demo_outputs"
    )
    print(
        json.dumps(
            {
                "versioned_summary": payload,
                "runtime_only_measurements": runtime_measurements,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
