from __future__ import annotations

import json
import random
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
random.seed(42)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def generate_aec_docs() -> None:
    text = """
    # Synthetic AEC Code and Design Guidance

    This mock document is synthetic demo data. It is not a legal code, planning
    rule, accessibility standard, or professional design instruction.

    ## Accessible Routes

    Primary public routes should provide a clear width of at least 1200 mm in
    high traffic zones. Doorways serving accessible rooms should provide a clear
    opening of at least 850 mm. Threshold changes greater than 12 mm should be
    ramped or otherwise resolved in the design.

    ## Fire Compartment Notes

    Residential corridors longer than 30 m should include documented
    compartmentation intent, smoke control assumptions, and fire-rated door
    schedules. Any door on a fire-rated line should include a rating note in the
    drawing or room schedule.

    ## Daylight and Glazing Guidance

    Frequently occupied rooms should receive useful daylight where feasible.
    South and west glazing should be reviewed for solar gain, glare, and
    cooling impact. Deep floor plates should include a daylight mitigation
    strategy such as atria, light wells, borrowed light, or program zoning.

    ## Planning Review Checklist

    Planning packages should explain setbacks, massing intent, public realm
    interfaces, servicing strategy, accessible parking, and waste collection.
    Missing assumptions should be logged before submission.

    ## Internal QA Standard

    Every issued room schedule should include a unique room ID, room name,
    modeled area, scheduled area, finish material, door clearance, accessibility
    note where relevant, and unresolved coordination comments.
    """
    write_text(ROOT / "projects/aec-code-compliance-rag/sample_data/mock_aec_guidance.md", text)
    write_json(
        ROOT / "projects/aec-code-compliance-rag/sample_data/evaluation_questions.json",
        [
            {
                "question": "What clear width should be checked for high traffic accessible routes?",
                "expected_source": "mock_aec_guidance.md",
                "expected_terms": ["1200 mm", "clear width", "accessible routes"],
            },
            {
                "question": "What should be included for long residential corridors?",
                "expected_source": "mock_aec_guidance.md",
                "expected_terms": ["compartmentation", "smoke control", "fire-rated door"],
            },
            {
                "question": "What daylight risks should west glazing trigger?",
                "expected_source": "mock_aec_guidance.md",
                "expected_terms": ["solar gain", "glare", "cooling impact"],
            },
        ],
    )


def generate_construction_progress() -> None:
    stages = ["foundation", "structure", "envelope", "mep", "interior", "handover"]
    rows = []
    for week in range(1, 31):
        progress = min(100, week * 3.7 + random.uniform(-5, 5))
        foundation = min(100, progress * 1.7)
        structure = max(0, min(100, (progress - 18) * 1.55))
        envelope = max(0, min(100, (progress - 38) * 1.65))
        mep = max(0, min(100, (progress - 45) * 1.45))
        interior = max(0, min(100, (progress - 62) * 1.75))
        handover = max(0, min(100, (progress - 82) * 2.2))
        label = stages[min(len(stages) - 1, int(progress // 18))]
        rows.append(
            {
                "image_id": f"site_week_{week:02d}.jpg",
                "week": week,
                "zone": random.choice(["north wing", "south wing", "core", "podium"]),
                "foundation_pct": round(foundation, 1),
                "structure_pct": round(structure, 1),
                "envelope_pct": round(envelope, 1),
                "mep_pct": round(mep, 1),
                "interior_pct": round(interior, 1),
                "handover_pct": round(handover, 1),
                "safety_observations": random.randint(0, 4),
                "weather_delay_days": random.choice([0, 0, 1, 2]),
                "stage_label": label,
            }
        )
    pd.DataFrame(rows).to_csv(
        ROOT / "projects/construction-progress-cv/sample_data/synthetic_progress_metadata.csv",
        index=False,
    )


def generate_bim_exports() -> None:
    rooms = [
        {
            "room_id": "A-101",
            "room_name": "Lobby",
            "level": "01",
            "area_scheduled": 84.0,
            "area_model": 83.1,
            "door_clearance_mm": 920,
            "material_spec": "porcelain tile",
            "fire_rating_note": "not required",
            "accessibility_note": "accessible route",
            "coordination_comment": "",
        },
        {
            "room_id": "A-102",
            "room_name": "",
            "level": "01",
            "area_scheduled": 20.0,
            "area_model": 28.8,
            "door_clearance_mm": 760,
            "material_spec": "vinyl floor",
            "fire_rating_note": "",
            "accessibility_note": "",
            "coordination_comment": "MEP riser conflict unresolved",
        },
        {
            "room_id": "A-102",
            "room_name": "Storage",
            "level": "01",
            "area_scheduled": 12.0,
            "area_model": 11.8,
            "door_clearance_mm": 810,
            "material_spec": "",
            "fire_rating_note": "",
            "accessibility_note": "not public",
            "coordination_comment": "",
        },
        {
            "room_id": "B-210",
            "room_name": "Accessible WC",
            "level": "02",
            "area_scheduled": 9.2,
            "area_model": 8.4,
            "door_clearance_mm": 780,
            "material_spec": "anti-slip tile",
            "fire_rating_note": "60 min wall",
            "accessibility_note": "",
            "coordination_comment": "Door swing clashes with basin clearance",
        },
        {
            "room_id": "C-305",
            "room_name": "Plant Room",
            "level": "03",
            "area_scheduled": 55.0,
            "area_model": 54.6,
            "door_clearance_mm": 900,
            "material_spec": "sealed concrete",
            "fire_rating_note": "",
            "accessibility_note": "maintenance access",
            "coordination_comment": "Fire wall shown without door rating tag",
        },
    ]
    pd.DataFrame(rooms).to_csv(
        ROOT / "projects/bim-issue-detection-agent/sample_data/mock_bim_room_schedule.csv",
        index=False,
    )
    write_json(
        ROOT / "projects/bim-issue-detection-agent/sample_data/mock_drawing_notes.json",
        [
            {"sheet": "A-101", "note": "Verify lobby threshold transition before issue."},
            {"sheet": "A-210", "note": "Accessible WC layout pending final consultant overlay."},
            {"sheet": "A-305", "note": "Plant room fire strategy to be coordinated."},
        ],
    )


def generate_job_descriptions() -> None:
    jobs = [
        {
            "title": "Applied AI Engineer - Construction Analytics",
            "description": "Build LLM workflows, computer vision pipelines, and data products for construction progress, BIM QA, and site reporting. Python, FastAPI, ML evaluation, and architecture domain knowledge preferred.",
        },
        {
            "title": "Machine Learning Engineer",
            "description": "Own training pipelines, model evaluation, feature stores, and deployment for tabular and document intelligence workloads. Strong Python, sklearn, PyTorch, and API skills required.",
        },
        {
            "title": "Architectural Designer",
            "description": "Support concept design, drafting, presentation boards, planning submissions, and consultant coordination. Rhino, Revit, and construction documentation experience required.",
        },
        {
            "title": "LLM Product Engineer - PropTech",
            "description": "Prototype and ship LLM assistants for real estate workflows, retrieval augmented generation, structured outputs, and customer-facing AI features. Experience with AEC or property data is a plus.",
        },
    ]
    write_json(ROOT / "projects/ai-aec-job-fit-analyzer/sample_data/sample_jobs.json", jobs)


def generate_energy_data() -> None:
    building_types = ["office", "residential", "school", "retail", "healthcare"]
    climates = ["tropical", "temperate", "cold", "hot-dry"]
    hvac = ["split", "vav", "chilled-water", "heat-pump"]
    rows = []
    for _idx in range(180):
        building_type = random.choice(building_types)
        floor_area = random.randint(800, 45000)
        glazing_ratio = round(random.uniform(0.18, 0.72), 2)
        occupancy = random.randint(30, 2400)
        insulation = round(random.uniform(0.25, 0.95), 2)
        operating_hours = random.randint(40, 120)
        climate = random.choice(climates)
        hvac_type = random.choice(hvac)
        base = 80 + 0.002 * floor_area + 0.035 * occupancy + 72 * glazing_ratio
        climate_adjustment = {"tropical": 42, "temperate": 10, "cold": 34, "hot-dry": 45}[climate]
        hvac_adjustment = {"split": 28, "vav": 18, "chilled-water": 12, "heat-pump": 8}[hvac_type]
        energy = (
            base + climate_adjustment + hvac_adjustment + operating_hours * 1.2 - insulation * 55
        )
        energy += random.gauss(0, 18)
        rows.append(
            {
                "building_type": building_type,
                "floor_area_m2": floor_area,
                "glazing_ratio": glazing_ratio,
                "orientation": random.choice(["N", "S", "E", "W"]),
                "climate_zone": climate,
                "occupancy": occupancy,
                "insulation_score": insulation,
                "hvac_type": hvac_type,
                "operating_hours_per_week": operating_hours,
                "energy_use_kwh_m2_year": round(max(55, energy), 2),
            }
        )
    pd.DataFrame(rows).to_csv(
        ROOT / "projects/building-energy-ml-pipeline/sample_data/synthetic_building_energy.csv",
        index=False,
    )


def generate_spatial_scenarios() -> None:
    scenarios = [
        {
            "name": "Compact clinic suite",
            "floor_area_m2": 420,
            "room_count": 18,
            "avg_daylight_score": 0.42,
            "circulation_ratio": 0.34,
            "adjacency_priority": "exam rooms near reception",
            "public_private_separation": 0.55,
        },
        {
            "name": "Studio office floor",
            "floor_area_m2": 980,
            "room_count": 12,
            "avg_daylight_score": 0.71,
            "circulation_ratio": 0.22,
            "adjacency_priority": "collaboration near workstations",
            "public_private_separation": 0.78,
        },
        {
            "name": "Deep residential podium",
            "floor_area_m2": 1350,
            "room_count": 34,
            "avg_daylight_score": 0.31,
            "circulation_ratio": 0.41,
            "adjacency_priority": "amenity spaces near lift core",
            "public_private_separation": 0.47,
        },
    ]
    write_json(
        ROOT / "projects/spatial-design-recommender/sample_data/example_scenarios.json", scenarios
    )


def main() -> None:
    generate_aec_docs()
    generate_construction_progress()
    generate_bim_exports()
    generate_job_descriptions()
    generate_energy_data()
    generate_spatial_scenarios()
    print("Synthetic sample data generated for all portfolio projects.")


if __name__ == "__main__":
    main()
