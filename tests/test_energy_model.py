import pandas as pd
from building_energy_ml_pipeline.model import (
    evaluate_energy_model,
    predict_energy_use,
    train_energy_model,
)


def _energy_frame() -> pd.DataFrame:
    rows = []
    for idx in range(36):
        glazing = 0.2 + (idx % 6) * 0.08
        floor_area = 1000 + idx * 300
        occupancy = 40 + idx * 12
        insulation = 0.35 + (idx % 5) * 0.1
        target = 105 + glazing * 80 + occupancy * 0.04 + floor_area * 0.002 - insulation * 35
        rows.append(
            {
                "building_type": ["office", "school", "retail"][idx % 3],
                "floor_area_m2": floor_area,
                "glazing_ratio": glazing,
                "orientation": ["N", "S", "E", "W"][idx % 4],
                "climate_zone": ["tropical", "temperate", "cold"][idx % 3],
                "occupancy": occupancy,
                "insulation_score": insulation,
                "hvac_type": ["split", "vav", "heat-pump"][idx % 3],
                "operating_hours_per_week": 45 + idx % 20,
                "energy_use_kwh_m2_year": target,
            }
        )
    return pd.DataFrame(rows)


def test_energy_model_trains_and_predicts() -> None:
    data = _energy_frame()
    model = train_energy_model(data)

    prediction = predict_energy_use(model, data.iloc[0].drop("energy_use_kwh_m2_year").to_dict())
    metrics = evaluate_energy_model(data)

    assert prediction > 0
    assert metrics["mae"] >= 0
    assert -1 <= metrics["r2"] <= 1


def test_energy_prediction_rejects_missing_fields() -> None:
    model = train_energy_model(_energy_frame())

    try:
        predict_energy_use(model, {"building_type": "office"})
    except ValueError as exc:
        assert "Missing prediction fields" in str(exc)
    else:
        raise AssertionError("Expected missing fields to raise ValueError")
