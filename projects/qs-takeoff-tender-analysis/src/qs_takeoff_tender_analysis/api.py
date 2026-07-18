from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException

from .costing import build_cost_estimate
from .models import FloorPlan, RateLibrary, TenderSubmission
from .takeoff import calculate_takeoff
from .tender import analyze_tender

app = FastAPI(title="QS Takeoff and Tender Analysis Workbench")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "data_boundary": "vector geometry and explicit rates only"}


@app.post("/takeoff")
def takeoff(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        return calculate_takeoff(FloorPlan.from_dict(payload)).to_dict()
    except (KeyError, TypeError, ValueError) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@app.post("/estimate")
def estimate(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        plan = FloorPlan.from_dict(dict(payload["plan"]))
        rates = RateLibrary.from_dict(dict(payload["rate_library"]))
        return build_cost_estimate(calculate_takeoff(plan), rates).to_dict()
    except (KeyError, TypeError, ValueError) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@app.post("/tender-review")
def tender_review(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        plan = FloorPlan.from_dict(dict(payload["plan"]))
        rates = RateLibrary.from_dict(dict(payload["rate_library"]))
        tender = TenderSubmission.from_dict(dict(payload["tender"]))
        benchmark = build_cost_estimate(calculate_takeoff(plan), rates)
        return analyze_tender(tender, benchmark).to_dict()
    except (KeyError, TypeError, ValueError) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
