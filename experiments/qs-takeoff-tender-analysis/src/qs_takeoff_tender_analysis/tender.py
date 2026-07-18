from __future__ import annotations

from .models import CostEstimate, TenderAnalysis, TenderFlag, TenderSubmission


def analyze_tender(
    tender: TenderSubmission,
    benchmark: CostEstimate,
    low_ratio: float = 0.75,
    high_ratio: float = 1.25,
) -> TenderAnalysis:
    if tender.currency != benchmark.currency:
        raise ValueError("Tender and benchmark currencies must match before comparison.")
    if not 0 < low_ratio < 1 < high_ratio:
        raise ValueError("Tender review bands must straddle 1.0.")

    benchmark_amounts = {line.item_code: line.amount for line in benchmark.priced_lines}
    flags: list[TenderFlag] = []
    supplied_benchmark_items = 0
    for item_code, amount in benchmark_amounts.items():
        submitted = tender.line_items.get(item_code)
        if submitted is None:
            flags.append(TenderFlag(item_code, "missing", amount, None, None))
            continue
        supplied_benchmark_items += 1
        ratio = submitted / amount if amount else 1.0
        flag = "within_demo_band"
        if ratio < low_ratio:
            flag = "low_quote"
        elif ratio > high_ratio:
            flag = "high_quote"
        flags.append(
            TenderFlag(
                item_code,
                flag,
                amount,
                round(submitted, 2),
                round(ratio, 4),
            )
        )

    for item_code, submitted in sorted(tender.line_items.items()):
        if item_code not in benchmark_amounts:
            flags.append(TenderFlag(item_code, "extra_item", None, round(submitted, 2), None))

    submitted_total = sum(tender.line_items.values())
    benchmark_total = benchmark.base_total
    review_flags = [flag for flag in flags if flag.flag != "within_demo_band"]
    return TenderAnalysis(
        tender_id=tender.tender_id,
        bidder_alias=tender.bidder_alias,
        status="needs_review" if review_flags else "within_demo_band",
        currency=tender.currency,
        submitted_total=round(submitted_total, 2),
        benchmark_total=benchmark_total,
        deviation_fraction=round(
            (submitted_total - benchmark_total) / benchmark_total if benchmark_total else 0.0,
            4,
        ),
        completeness_fraction=round(
            supplied_benchmark_items / len(benchmark_amounts) if benchmark_amounts else 0.0,
            4,
        ),
        flags=tuple(flags),
    )


def review_flags(analysis: TenderAnalysis) -> tuple[TenderFlag, ...]:
    return tuple(flag for flag in analysis.flags if flag.flag != "within_demo_band")
