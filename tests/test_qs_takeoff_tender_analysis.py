from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest
from fastapi import HTTPException
from qs_takeoff_tender_analysis import (
    FloorPlan,
    RateLibrary,
    TenderSubmission,
    analyze_tender,
    build_cost_estimate,
    calculate_takeoff,
    evaluate_qs_workflow,
    load_floor_plans,
    load_json,
    load_rate_library,
    load_tenders,
    naive_room_perimeter_length_m,
    render_floor_plan_svg,
    review_flags,
)
from qs_takeoff_tender_analysis.api import takeoff as api_takeoff

PROJECT_ROOT = Path("projects/qs-takeoff-tender-analysis")
DATA_DIR = PROJECT_ROOT / "sample_data"


@pytest.fixture
def plans():
    return load_floor_plans(DATA_DIR / "synthetic_floor_plans.json")


@pytest.fixture
def rates():
    return load_rate_library(DATA_DIR / "synthetic_rate_library.json")


def test_takeoff_matches_hand_calculated_shared_wall_case(plans) -> None:
    plan = next(item for item in plans if item.plan_id == "office-02")
    result = calculate_takeoff(plan)

    assert result.external_wall_length_m == 36.0
    assert result.partition_length_m == 8.0
    assert result.quantity_map() == {
        "QTO-FLR": 80.0,
        "QTO-CEI": 80.0,
        "QTO-SLB": 12.0,
        "QTO-EXT": 99.48,
        "QTO-INT": 21.9,
        "QTO-DOR": 2.0,
        "QTO-WIN": 6.0,
    }
    assert naive_room_perimeter_length_m(plan) == 52.0


def test_opening_deductions_are_classified_by_host_wall(plans) -> None:
    plan = next(item for item in plans if item.plan_id == "clinic-03")
    result = calculate_takeoff(plan)

    assert result.opening_deductions_m2 == {"external": 7.7, "partition": 4.2}
    assert result.quantity_map()["QTO-EXT"] == 111.1
    assert result.quantity_map()["QTO-INT"] == 32.1


def test_missing_scale_fails_closed() -> None:
    payload = load_json(DATA_DIR / "synthetic_floor_plans.json")["plans"][0]
    payload = deepcopy(payload)
    payload.pop("scale_m_per_unit")

    with pytest.raises(ValueError, match="scale_m_per_unit"):
        FloorPlan.from_dict(payload)


def test_overlapping_rooms_are_rejected() -> None:
    payload = deepcopy(load_json(DATA_DIR / "synthetic_floor_plans.json")["plans"][0])
    payload["rooms"].append(
        {"room_id": "R-X", "name": "Overlap", "x": 2.0, "y": 2.0, "width": 2.0, "depth": 2.0}
    )

    with pytest.raises(ValueError, match="overlap"):
        FloorPlan.from_dict(payload)


def test_opening_off_wall_is_rejected(plans) -> None:
    payload = plans[0].to_dict()
    payload["openings"][0].update({"x1": 2.0, "y1": 2.0, "x2": 3.0, "y2": 2.0})

    with pytest.raises(ValueError, match="entirely on one classified wall"):
        calculate_takeoff(FloorPlan.from_dict(payload))


def test_overlapping_openings_are_rejected(plans) -> None:
    payload = plans[0].to_dict()
    payload["openings"] = list(payload["openings"])
    payload["openings"].append(
        {
            "opening_id": "D-X",
            "kind": "door",
            "x1": 1.5,
            "y1": 0.0,
            "x2": 2.5,
            "y2": 0.0,
            "height_m": 2.1,
        }
    )

    with pytest.raises(ValueError, match="overlap"):
        calculate_takeoff(FloorPlan.from_dict(payload))


def test_cost_estimate_carries_rate_and_geometry_provenance(plans, rates) -> None:
    estimate = build_cost_estimate(calculate_takeoff(plans[0]), rates)

    assert estimate.status == "priced"
    assert estimate.base_total == 33579.5
    assert estimate.low_total < estimate.base_total < estimate.high_total
    assert all(line.rate_provenance for line in estimate.priced_lines)
    assert all(line.quantity_source_refs for line in estimate.priced_lines)


def test_missing_rate_is_reported_without_zero_price(plans, rates) -> None:
    payload = {
        "version": rates.version,
        "currency": rates.currency,
        "data_status": rates.data_status,
        "source_note": rates.source_note,
        "items": [item.__dict__ for item in rates.items if item.item_code != "QTO-WIN"],
    }
    estimate = build_cost_estimate(
        calculate_takeoff(plans[0]),
        RateLibrary.from_dict(payload),
    )

    assert estimate.status == "needs_rate_review"
    assert estimate.unpriced_item_codes == ("QTO-WIN",)
    assert all(line.item_code != "QTO-WIN" for line in estimate.priced_lines)


def test_cost_estimate_rejects_rate_unit_mismatch(plans, rates) -> None:
    items = [item.__dict__.copy() for item in rates.items]
    items[0]["unit"] = "ea"
    mismatched_rates = RateLibrary.from_dict(
        {
            "version": rates.version,
            "currency": rates.currency,
            "data_status": rates.data_status,
            "source_note": rates.source_note,
            "items": items,
        }
    )

    with pytest.raises(ValueError, match="Unit mismatch"):
        build_cost_estimate(calculate_takeoff(plans[0]), mismatched_rates)


def test_tender_review_finds_missing_low_high_and_extra_items(plans, rates) -> None:
    benchmark_plan_id, tenders = load_tenders(DATA_DIR / "synthetic_tenders.json")
    plan = next(item for item in plans if item.plan_id == benchmark_plan_id)
    benchmark = build_cost_estimate(calculate_takeoff(plan), rates)
    analyses = {tender.tender_id: analyze_tender(tender, benchmark) for tender in tenders}

    assert review_flags(analyses["TENDER-A"]) == ()
    assert {(flag.item_code, flag.flag) for flag in review_flags(analyses["TENDER-B"])} == {
        ("QTO-EXT", "low_quote"),
        ("QTO-WIN", "missing"),
    }
    assert ("PRELIM", "extra_item") in {
        (flag.item_code, flag.flag) for flag in review_flags(analyses["TENDER-C"])
    }


def test_tender_review_rejects_currency_mismatch(plans, rates) -> None:
    benchmark = build_cost_estimate(calculate_takeoff(plans[0]), rates)
    tender = TenderSubmission(
        tender_id="T-X",
        bidder_alias="Anonymous Bidder X",
        data_status="synthetic",
        currency="USD",
        line_items={line.item_code: line.amount for line in benchmark.priced_lines},
    )

    with pytest.raises(ValueError, match="currencies must match"):
        analyze_tender(tender, benchmark)


def test_evaluation_has_zero_fixture_error_and_explicit_baseline_gap(plans, rates) -> None:
    benchmark_plan_id, tenders = load_tenders(DATA_DIR / "synthetic_tenders.json")
    result = evaluate_qs_workflow(
        plans,
        rates,
        load_json(DATA_DIR / "evaluation_cases.json"),
        benchmark_plan_id,
        tenders,
    )

    assert result["metrics"]["quantity_line_exact_match_rate"] == 1.0
    assert result["metrics"]["wall_length_mean_absolute_error_m"] == 0.0
    assert result["metrics"]["naive_perimeter_wall_mean_absolute_error_m"] == pytest.approx(
        6.333333
    )
    assert result["metrics"]["cost_total_mean_absolute_error"] == 0.0
    assert result["metrics"]["tender_flag_f1"] == 1.0
    assert not any(result["fixture_mismatches"].values())


def test_api_rejects_unscaled_plan_and_returns_takeoff(plans) -> None:
    valid = api_takeoff(plans[0].to_dict())
    invalid_payload = json.loads(json.dumps(plans[0].to_dict()))
    invalid_payload.pop("scale_m_per_unit")

    assert valid["quantities"][0]["item_code"] == "QTO-FLR"
    with pytest.raises(HTTPException) as error:
        api_takeoff(invalid_payload)
    assert error.value.status_code == 422


def test_generated_svg_is_accessible_and_contains_boundary(plans) -> None:
    svg = render_floor_plan_svg(plans[1], calculate_takeoff(plans[1]))

    assert 'role="img"' in svg
    assert "Synthetic vector takeoff" in svg
    assert "No PDF/CAD/BIM parsing" in svg
