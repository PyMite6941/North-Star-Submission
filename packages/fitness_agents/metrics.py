"""Compute summary metrics from parsed activity records.

These ground the LLM agents in real numbers instead of guesses.
"""

from __future__ import annotations

from pydantic import BaseModel

from fitness_agents.parsers import ActivityRecord


class ActivitySummary(BaseModel):
    """Aggregate metrics for one activity / file."""

    n_samples: int = 0
    duration_s: float | None = None
    distance_km: float | None = None
    avg_speed_kmh: float | None = None
    avg_pace_min_per_km: float | None = None
    elevation_gain_m: float | None = None
    avg_heart_rate: float | None = None
    max_heart_rate: float | None = None
    avg_power_w: float | None = None
    avg_cadence: float | None = None
    training_load: float | None = None
    hr_zones: dict[str, float] | None = None  # zone -> fraction of time

    def to_prompt(self) -> str:
        """Compact, LLM-friendly rendering of the metrics."""
        lines = [f"- samples: {self.n_samples}"]
        if self.duration_s:
            lines.append(f"- duration: {self.duration_s / 60:.1f} min")
        if self.distance_km:
            lines.append(f"- distance: {self.distance_km:.2f} km")
        if self.avg_speed_kmh:
            lines.append(f"- avg speed: {self.avg_speed_kmh:.2f} km/h")
        if self.avg_pace_min_per_km:
            lines.append(f"- avg pace: {self.avg_pace_min_per_km:.2f} min/km")
        if self.elevation_gain_m is not None:
            lines.append(f"- elevation gain: {self.elevation_gain_m:.0f} m")
        if self.avg_heart_rate:
            lines.append(f"- avg HR: {self.avg_heart_rate:.0f} bpm (max {self.max_heart_rate:.0f})")
        if self.training_load is not None:
            lines.append(f"- training load: {self.training_load:.0f}")
        if self.hr_zones:
            zones = ", ".join(f"{z} {frac * 100:.0f}%" for z, frac in self.hr_zones.items())
            lines.append(f"- HR zones (% of time): {zones}")
        if self.avg_power_w:
            lines.append(f"- avg power: {self.avg_power_w:.0f} W")
        if self.avg_cadence:
            lines.append(f"- avg cadence: {self.avg_cadence:.0f}")
        return "\n".join(lines)


def _avg(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


# 5-zone model as fractions of the reference (peak) heart rate.
_HR_ZONE_BANDS = [
    ("Z1", 0.00, 0.60),
    ("Z2", 0.60, 0.70),
    ("Z3", 0.70, 0.80),
    ("Z4", 0.80, 0.90),
    ("Z5", 0.90, 1.01),
]


def _hr_zones(hrs: list[float], max_hr: float | None) -> dict[str, float] | None:
    """Fraction of HR samples falling in each of the 5 zones (relative to peak HR)."""
    if not hrs or not max_hr:
        return None
    counts = {band[0]: 0 for band in _HR_ZONE_BANDS}
    for hr in hrs:
        frac = hr / max_hr
        for name, lo, hi in _HR_ZONE_BANDS:
            if lo <= frac < hi:
                counts[name] += 1
                break
    total = len(hrs)
    return {z: counts[z] / total for z in counts}


def _training_load(
    duration_s: float | None,
    avg_hr: float | None,
    max_hr: float | None,
    resting_hr: float | None = None,
) -> float | None:
    """Session load ≈ minutes × HR intensity.

    With a resting HR, uses heart-rate reserve (Banister-style TRIMP); otherwise a
    simple avg/max fraction.
    """
    if not (duration_s and avg_hr and max_hr):
        return None
    minutes = duration_s / 60
    if resting_hr and max_hr > resting_hr:
        hrr = max(0.0, min(1.0, (avg_hr - resting_hr) / (max_hr - resting_hr)))
        return minutes * hrr
    return minutes * (avg_hr / max_hr)


def summarize(
    records: list[ActivityRecord],
    *,
    max_hr: float | None = None,
    resting_hr: float | None = None,
) -> ActivitySummary:
    """Reduce raw records to an :class:`ActivitySummary`.

    HR zones and training load use ``max_hr``/``resting_hr`` when given (or from the
    athlete profile in settings); otherwise they fall back to the observed peak HR.
    """
    if not records:
        return ActivitySummary()

    # Pull athlete profile defaults from settings when not explicitly provided.
    if max_hr is None or resting_hr is None:
        from polaris_core.config import get_settings

        settings = get_settings()
        max_hr = max_hr if max_hr is not None else settings.max_hr_estimate()
        resting_hr = resting_hr if resting_hr is not None else settings.athlete_resting_hr

    hrs = [r.heart_rate for r in records if r.heart_rate]
    powers = [r.power_w for r in records if r.power_w]
    cadences = [r.cadence for r in records if r.cadence]

    # Duration from timestamp span.
    times = sorted(r.timestamp for r in records if r.timestamp)
    duration_s = (times[-1] - times[0]).total_seconds() if len(times) >= 2 else None

    # Distance: prefer cumulative field, else integrate GPS haversine.
    distances = [r.distance_m for r in records if r.distance_m is not None]
    distance_m = max(distances) if distances else _gps_distance_m(records)
    distance_km = distance_m / 1000 if distance_m else None

    avg_speed_kmh = None
    avg_pace = None
    if distance_km and duration_s:
        avg_speed_kmh = distance_km / (duration_s / 3600)
        avg_pace = (duration_s / 60) / distance_km if distance_km else None

    avg_hr = _avg(hrs)
    observed_peak = max(hrs) if hrs else None
    # Zones/load use the profile max HR when available, else the observed peak.
    ref_max_hr = max_hr or observed_peak

    return ActivitySummary(
        n_samples=len(records),
        duration_s=duration_s,
        distance_km=distance_km,
        avg_speed_kmh=avg_speed_kmh,
        avg_pace_min_per_km=avg_pace,
        elevation_gain_m=_elevation_gain(records),
        avg_heart_rate=avg_hr,
        max_heart_rate=observed_peak,
        avg_power_w=_avg(powers),
        avg_cadence=_avg(cadences),
        training_load=_training_load(duration_s, avg_hr, ref_max_hr, resting_hr),
        hr_zones=_hr_zones(hrs, ref_max_hr),
    )


def _elevation_gain(records: list[ActivityRecord]) -> float | None:
    alts = [r.altitude_m for r in records if r.altitude_m is not None]
    if len(alts) < 2:
        return None
    return sum(max(0.0, b - a) for a, b in zip(alts, alts[1:], strict=False))


def _gps_distance_m(records: list[ActivityRecord]) -> float | None:
    """Haversine sum over GPS points when no cumulative distance is present."""
    from math import asin, cos, radians, sin, sqrt

    pts = [(r.latitude, r.longitude) for r in records if r.latitude and r.longitude]
    if len(pts) < 2:
        return None
    total = 0.0
    for (lat1, lon1), (lat2, lon2) in zip(pts, pts[1:], strict=False):
        dlat, dlon = radians(lat2 - lat1), radians(lon2 - lon1)
        a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
        total += 2 * 6_371_000 * asin(sqrt(a))
    return total
