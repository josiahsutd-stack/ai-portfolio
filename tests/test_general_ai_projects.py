import json
from pathlib import Path

import pytest
from agentic_research_ops_assistant import ResearchAgent, evaluate_trace
from mlops_model_serving_monitoring import (
    ChurnPredictionInput,
    detect_drift,
    generate_churn_data,
    generate_monitoring_report,
    list_drift_reports,
    list_prediction_logs,
    log_prediction,
    population_stability_index,
    predict_churn,
    record_drift_report,
    save_model_artifact,
    train_churn_model,
)
from streamlit.testing.v1 import AppTest
from visual_provider_contract import (
    MockVLMProvider,
    OpenAICompatibleVLMProvider,
    build_vlm_prompt,
    validate_image_bytes,
)
from vla_embodied_agent_simulator import GridWorldEnv, plan_from_instruction


def test_vlm_structured_output_schema_and_validation() -> None:
    image_bytes = b"\x89PNG\r\n\x1a\nsynthetic"
    response = MockVLMProvider().answer(image_bytes, "Extract defects as JSON")

    assert validate_image_bytes(image_bytes) == "png"
    assert response.structured_json.key_values["mode"] == "mock_no_visual_inference"
    assert response.confidence == 0.0
    assert response.model_dump()["structured_json"]["defects"] == []
    assert response.structured_json.detected_objects == []
    assert "did not inspect or infer" in response.answer


def test_agent_planning_tool_execution_and_citations(tmp_path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "deployment.md").write_text(
        "# Deployment\nOnline model deployment needs monitoring and rollback.", encoding="utf-8"
    )
    trace_db = tmp_path / "traces.sqlite"
    agent = ResearchAgent(docs, trace_db_path=trace_db)

    trace = agent.run("Compare AI model deployment strategies")

    assert "search_local_docs" in trace.plan
    assert trace.tool_calls
    assert trace.citations == ["deployment.md"]
    assert "Research Brief" in trace.final_report
    assert trace.evaluation["passed"]
    assert agent.recent_traces(limit=1)[0]["trace_id"] == trace.trace_id
    assert trace_db.exists()


def test_agent_tool_permissions_and_trace_eval(tmp_path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "ops.md").write_text("# Ops\nMonitoring requires logs and alerts.", encoding="utf-8")
    agent = ResearchAgent(
        docs,
        trace_db_path=tmp_path / "limited.sqlite",
        allowed_tools={"search_local_docs", "create_report", "ask_human_approval", "save_memory"},
    )

    trace = agent.run("Summarize monitoring requirements")
    evaluation = evaluate_trace(trace.model_dump())

    assert "summarize_document" not in trace.plan
    assert trace.citations == ["ops.md"]
    assert evaluation["passed"]
    assert trace.planner_reason.startswith("Default deterministic local planner")


def test_agent_retry_succeeds_after_transient_failure(tmp_path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    agent = ResearchAgent(docs, trace_db_path=tmp_path / "retry.sqlite", max_retries=2)
    calls = {"count": 0}

    def flaky_tool() -> str:
        calls["count"] += 1
        if calls["count"] == 1:
            raise RuntimeError("temporary failure")
        return "ok"

    result, call = agent._run_tool("search_local_docs", flaky_tool)  # noqa: SLF001

    assert result == "ok"
    assert call.status == "ok"
    assert call.attempts == 2
    assert call.errors == ["temporary failure"]


def test_agent_retry_exhausts_and_records_error(tmp_path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    agent = ResearchAgent(docs, trace_db_path=tmp_path / "retry.sqlite", max_retries=1)

    def failing_tool() -> str:
        raise RuntimeError("still broken")

    result, call = agent._run_tool("search_local_docs", failing_tool)  # noqa: SLF001

    assert result is None
    assert call.status == "error"
    assert call.attempts == 2
    assert call.error == "still broken"
    assert call.errors == ["still broken", "still broken"]


def test_agent_denied_tool_records_trace_without_execution(tmp_path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    agent = ResearchAgent(
        docs,
        trace_db_path=tmp_path / "denied.sqlite",
        allowed_tools={"search_local_docs"},
    )

    result, call = agent._run_tool("create_report", lambda: "should not run")  # noqa: SLF001

    assert result is None
    assert call.status == "denied"
    assert call.attempts == 0
    assert call.error == "permission_denied"


def test_vla_environment_transitions_and_safety() -> None:
    env = GridWorldEnv()
    state, reward, done, info = env.step("move_right")
    assert state["agent"] == (1, 0)
    assert reward < 0
    assert not done
    _state, blocked_reward, _done, blocked_info = env.step("move_down")
    assert blocked_reward == -1.0
    assert blocked_info["error"] == "unsafe_or_blocked_move"


def test_vla_task_completion_plan() -> None:
    env = GridWorldEnv()
    done = False
    for action in plan_from_instruction(
        "Pick up the red object and move it to the blue zone.", env
    ):
        _state, _reward, done, _info = env.step(action)
        if done:
            break
    assert done


def test_mlops_prediction_schema_and_drift_detection() -> None:
    data = generate_churn_data()
    model, _metrics = train_churn_model(data)
    prediction = predict_churn(
        model,
        {
            "tenure_months": 12,
            "monthly_spend": 80,
            "support_tickets": 3,
            "usage_score": 0.6,
        },
    )
    current = data.copy()
    current["usage_score"] = current["usage_score"] * 0.2
    drift = detect_drift(data, current, threshold=0.1)

    assert 0 <= prediction["churn_probability"] <= 1
    assert prediction["predicted_label"] in {0, 1}
    assert prediction["schema_version"]
    assert drift["drift_detected"]
    assert drift["top_drifted_features"]
    assert drift["scores"]["usage_score"]["psi"] > 0
    assert population_stability_index(data["usage_score"], current["usage_score"]) > 0


def test_mlops_artifact_logging_and_drift_history(tmp_path) -> None:
    data = generate_churn_data(80)
    model, metrics = train_churn_model(data)
    artifacts = save_model_artifact(model, metrics, registry_dir=tmp_path / "registry")
    db_path = tmp_path / "observability.sqlite"
    payload = {
        "tenure_months": 12,
        "monthly_spend": 80,
        "support_tickets": 3,
        "usage_score": 0.6,
    }
    prediction = predict_churn(model, payload)
    log_id = log_prediction(
        payload,
        prediction,
        model_version=str(metrics["version"]),
        db_path=db_path,
        request_id="req-1",
        latency_ms=9,
    )
    drift = detect_drift(data, data.assign(usage_score=data["usage_score"] * 0.1))
    report_id = record_drift_report(
        drift,
        reference_window="reference",
        current_window="current",
        db_path=db_path,
    )

    assert artifacts["model_path"].endswith(".joblib")
    assert "metadata_path" in artifacts
    metadata = json.loads(Path(artifacts["metadata_path"]).read_text(encoding="utf-8"))
    assert metadata["feature_schema"] == metrics["feature_schema"]
    assert metadata["dataset_info"]["source"] == "synthetic generated churn data"
    assert "git_commit" in metadata
    assert log_id == 1
    assert report_id == 1
    logs = list_prediction_logs(db_path=db_path)
    assert logs[0]["prediction"] == prediction
    assert logs[0]["request_id"] == "req-1"
    report = generate_monitoring_report(
        data, data.assign(usage_score=data["usage_score"] * 0.1), prediction_logs=logs
    )
    assert report["prediction_volume"] == 1
    assert report["latency_ms"]["avg"] == 9
    assert list_drift_reports(db_path=db_path)[0]["drift_detected"]


def test_vlm_rejects_unsupported_image_type() -> None:
    with pytest.raises(ValueError):
        validate_image_bytes(b"not-an-image")


def test_vlm_prompt_contract_includes_uncertainty_and_metadata() -> None:
    prompt = build_vlm_prompt("Find defects", image_metadata={"source": "synthetic.png"})

    assert "Return JSON" in prompt
    assert "uncertain" in prompt.lower()
    assert "source: synthetic.png" in prompt


def test_vlm_rejects_deceptive_local_provider_alias(monkeypatch) -> None:
    monkeypatch.setenv("VLM_PROVIDER", "local")

    from visual_provider_contract import get_vlm_provider

    with pytest.raises(ValueError, match="Unsupported VLM_PROVIDER"):
        get_vlm_provider()


def test_hosted_vlm_without_key_falls_back_to_zero_confidence_mock(monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    response = OpenAICompatibleVLMProvider(api_key=None).answer(
        b"\x89PNG\r\n\x1a\nsynthetic",
        "Find defects",
    )

    assert response.provider == "openai-compatible-vlm-mock-fallback"
    assert response.confidence == 0.0
    assert response.structured_json.defects == []
    assert response.structured_json.key_values["mode"] == "mock_no_visual_inference"


def test_visual_provider_app_exposes_mock_boundary_without_errors() -> None:
    app = AppTest.from_file("experiments/visual-provider-contract/app.py").run(timeout=15)

    assert not app.exception
    assert app.title[0].value == "Visual Provider Contract"
    assert "performs no visual inference" in app.caption[0].value
    assert app.button[0].label == "Run provider"


def test_openai_compatible_vlm_provider_parses_schema(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self) -> bytes:
            return json.dumps(
                {
                    "choices": [
                        {
                            "message": {
                                "content": json.dumps(
                                    {
                                        "answer": "Visible defect noted.",
                                        "detected_objects": ["panel"],
                                        "visible_text": [],
                                        "defects": ["scratch"],
                                        "key_values": {"severity": "low"},
                                        "confidence": 0.71,
                                        "uncertainty": "Single image only.",
                                        "observations": ["Provider parsed image."],
                                    }
                                )
                            }
                        }
                    ]
                }
            ).encode("utf-8")

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["timeout"] = timeout
        captured["body"] = json.loads(request.data.decode("utf-8"))
        return FakeResponse()

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    provider = OpenAICompatibleVLMProvider(
        api_key="test-key",
        base_url="https://example.test/v1",
        model="vision-test",
    )
    response = provider.answer(b"\x89PNG\r\n\x1a\nsynthetic", "Find defects")

    assert captured["url"] == "https://example.test/v1/chat/completions"
    assert captured["body"]["model"] == "vision-test"
    assert response.provider == "openai-compatible-vlm"
    assert response.structured_json.defects == ["scratch"]
    assert response.confidence == 0.71


def test_mlops_rejects_missing_prediction_fields() -> None:
    model, _metrics = train_churn_model(generate_churn_data())
    with pytest.raises(ValueError):
        predict_churn(model, {"tenure_months": 1})


def test_mlops_rejects_impossible_prediction_values() -> None:
    model, _metrics = train_churn_model(generate_churn_data())
    with pytest.raises(ValueError):
        predict_churn(
            model,
            {
                "tenure_months": -1,
                "monthly_spend": 80,
                "support_tickets": 3,
                "usage_score": 0.6,
            },
        )


def test_mlops_schema_rejects_extra_fields() -> None:
    with pytest.raises(ValueError):
        ChurnPredictionInput.model_validate(
            {
                "tenure_months": 12,
                "monthly_spend": 80,
                "support_tickets": 3,
                "usage_score": 0.6,
                "unused": 1,
            }
        )
