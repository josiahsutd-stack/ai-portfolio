from __future__ import annotations

from .models import CostEstimate, CostLine, RateLibrary, TakeoffResult

DEFAULT_EXCLUSIONS = (
    "Preliminaries, contractor overhead, profit, taxes, escalation, and location factors",
    "Structural reinforcement, foundations, MEP systems, specialist works, and temporary works",
    "Drawing interpretation beyond the bundled rectangular vector schema",
)


def build_cost_estimate(
    takeoff: TakeoffResult,
    rate_library: RateLibrary,
    exclusions: tuple[str, ...] = DEFAULT_EXCLUSIONS,
) -> CostEstimate:
    rates = {item.item_code: item for item in rate_library.items}
    priced_lines: list[CostLine] = []
    unpriced: list[str] = []
    for quantity in takeoff.quantities:
        rate = rates.get(quantity.item_code)
        if rate is None:
            unpriced.append(quantity.item_code)
            continue
        if rate.unit != quantity.unit:
            raise ValueError(
                f"Unit mismatch for {quantity.item_code}: quantity is {quantity.unit}, rate is {rate.unit}."
            )
        amount = quantity.quantity * rate.unit_rate
        priced_lines.append(
            CostLine(
                item_code=quantity.item_code,
                description=quantity.description,
                unit=quantity.unit,
                quantity=quantity.quantity,
                unit_rate=rate.unit_rate,
                amount=round(amount, 2),
                low_amount=round(amount * (1 - rate.uncertainty_fraction), 2),
                high_amount=round(amount * (1 + rate.uncertainty_fraction), 2),
                rate_provenance=rate.provenance,
                quantity_source_refs=quantity.source_refs,
            )
        )
    return CostEstimate(
        plan_id=takeoff.plan_id,
        status="priced" if not unpriced else "needs_rate_review",
        currency=rate_library.currency,
        rate_library_version=rate_library.version,
        base_total=round(sum(line.amount for line in priced_lines), 2),
        low_total=round(sum(line.low_amount for line in priced_lines), 2),
        high_total=round(sum(line.high_amount for line in priced_lines), 2),
        priced_lines=tuple(priced_lines),
        unpriced_item_codes=tuple(unpriced),
        exclusions=exclusions,
    )
