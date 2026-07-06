"""AKI recognition — deterministic, no model.

Grounded in spec/guidelines/aki_thresholds.md and spec/aki_spec.md (KDIGO / Think Kidneys).
Community setting: creatinine/eGFR criteria only (urine-output criteria are hospital-only).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta

ABS_RISE_UMOL = 26.0
ABS_RISE_WINDOW = timedelta(hours=48)
RATIO_THRESHOLD = 1.5
RATIO_WINDOW = timedelta(days=7)


@dataclass
class CreatinineReading:
    value_umol_l: float
    timestamp: datetime


@dataclass
class AkiResult:
    suspected_aki: bool = False
    criterion: str | None = None  # "abs_rise_48h" | "ratio_1_5x_7d"
    detail: str = ""
    flagged_reading_ts: datetime | None = None
    baseline_used: float | None = None


def _select_baseline(readings: list[CreatinineReading], explicit: float | None) -> float | None:
    """Baseline = explicit value if given, else the person's lowest prior stable value.

    Using the minimum of prior readings as the stable reference is the simplest correct rule for
    the community slice; a richer baseline model (e.g. median of readings 7-365 days prior, the
    Think Kidneys algorithm) is documented as a limitation in spec/aki_spec.md.
    """
    if explicit is not None:
        return explicit
    if len(readings) < 2:
        return None
    # baseline candidates = all but the latest reading
    prior = sorted(readings, key=lambda r: r.timestamp)[:-1]
    return min(r.value_umol_l for r in prior) if prior else None


def check_aki(
    readings: list[CreatinineReading], baseline: float | None = None
) -> AkiResult:
    """Return a suspected-AKI flag from timestamped creatinine readings.

    Fires if EITHER a rise >= 26 umol/L within 48h OR a rise to >= 1.5x baseline within 7d.
    On a hit, the flagged reading should be held out of the CKD trend and KFRE by callers.
    """
    if len(readings) < 2:
        return AkiResult(
            suspected_aki=False,
            detail="Insufficient data: need at least two timestamped creatinine readings.",
        )

    ordered = sorted(readings, key=lambda r: r.timestamp)
    base = _select_baseline(ordered, baseline)
    if base is None:
        return AkiResult(suspected_aki=False, detail="Insufficient data: no baseline available.")

    base_ts = ordered[0].timestamp
    latest = ordered[-1]

    # Criterion 1: absolute rise >= 26 umol/L within 48h of baseline timestamp.
    for r in ordered[1:]:
        if (r.timestamp - base_ts) <= ABS_RISE_WINDOW and (r.value_umol_l - base) >= ABS_RISE_UMOL:
            return AkiResult(
                suspected_aki=True,
                criterion="abs_rise_48h",
                detail=(
                    f"Creatinine rose by {r.value_umol_l - base:.0f} umol/L "
                    f"(from {base:.0f} to {r.value_umol_l:.0f}) within 48 hours — at or above the "
                    f"26 umol/L threshold. This reading has been separated from your long-term "
                    f"kidney trend and left out of any risk estimate."
                ),
                flagged_reading_ts=r.timestamp,
                baseline_used=base,
            )

    # Criterion 2: rise to >= 1.5x baseline within 7 days.
    for r in ordered[1:]:
        if (r.timestamp - base_ts) <= RATIO_WINDOW and base > 0 and (r.value_umol_l / base) >= RATIO_THRESHOLD:
            return AkiResult(
                suspected_aki=True,
                criterion="ratio_1_5x_7d",
                detail=(
                    f"Creatinine rose to {r.value_umol_l / base:.2f}x your baseline "
                    f"(from {base:.0f} to {r.value_umol_l:.0f}) within 7 days — at or above 1.5x. "
                    f"This reading has been separated from your long-term kidney trend and left out "
                    f"of any risk estimate."
                ),
                flagged_reading_ts=r.timestamp,
                baseline_used=base,
            )

    return AkiResult(
        suspected_aki=False,
        detail="No acute rise meeting AKI thresholds detected.",
        baseline_used=base,
        flagged_reading_ts=None,
    )
