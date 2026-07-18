from __future__ import annotations

from dataclasses import replace

import pytest

from scripts.check_visual_contract import collect_issues
from scripts.generate_system_maps import build_specs
from shared.portfolio_visuals import render_system_map


def test_selected_project_visual_contract_is_current() -> None:
    assert collect_issues() == []


def test_system_maps_embed_accessible_structure_and_provenance() -> None:
    for spec in build_specs().values():
        rendered = render_system_map(spec)

        assert 'role="img"' in rendered
        assert 'aria-labelledby="map-title map-desc"' in rendered
        assert "<metadata>" in rendered
        assert "EXECUTED SYSTEM JOURNEY" in rendered
        assert "PROOF, CONTROLS, AND FAILURE BOUNDARIES" in rendered
        assert "HUMAN REVIEW BOUNDARY:" in rendered


def test_system_map_renderer_rejects_incomplete_journeys() -> None:
    spec = next(iter(build_specs().values()))

    with pytest.raises(ValueError, match="exactly five journey stages"):
        render_system_map(replace(spec, stages=spec.stages[:-1]))

    with pytest.raises(ValueError, match="exactly four connector labels"):
        render_system_map(replace(spec, connectors=spec.connectors[:-1]))

    with pytest.raises(ValueError, match="exactly three evidence panels"):
        render_system_map(replace(spec, evidence=spec.evidence[:-1]))
