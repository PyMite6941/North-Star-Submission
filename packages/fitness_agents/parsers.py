"""Parse fitness files into a common :class:`ActivityRecord` schema.

Supported: .fit, .tcx, .gpx, .csv, .json. Each parser returns a list of records
(one row per sample / trackpoint / entry). Register new formats in ``PARSERS``.
"""

from __future__ import annotations

import csv
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

from polaris_core.logging import get_logger
from pydantic import BaseModel

logger = get_logger(__name__)


class ActivityRecord(BaseModel):
    """A single normalized sample from any fitness file."""

    timestamp: datetime | None = None
    latitude: float | None = None
    longitude: float | None = None
    altitude_m: float | None = None
    distance_m: float | None = None
    heart_rate: float | None = None
    cadence: float | None = None
    power_w: float | None = None
    speed_mps: float | None = None
    source_format: str = ""


# ---------------------------------------------------------------------------
# Individual format parsers
# ---------------------------------------------------------------------------
def _parse_fit(path: Path) -> list[ActivityRecord]:
    from fitparse import FitFile  # local import: optional heavy dep

    records: list[ActivityRecord] = []
    fit = FitFile(str(path))
    for msg in fit.get_messages("record"):
        d = {x.name: x.value for x in msg}
        records.append(
            ActivityRecord(
                timestamp=d.get("timestamp"),
                latitude=_semicircles(d.get("position_lat")),
                longitude=_semicircles(d.get("position_long")),
                altitude_m=d.get("altitude") or d.get("enhanced_altitude"),
                distance_m=d.get("distance"),
                heart_rate=d.get("heart_rate"),
                cadence=d.get("cadence"),
                power_w=d.get("power"),
                speed_mps=d.get("speed") or d.get("enhanced_speed"),
                source_format="fit",
            )
        )
    return records


def _semicircles(value) -> float | None:
    """Convert Garmin semicircle coordinates to degrees."""
    if value is None:
        return None
    return value * (180.0 / 2**31)


_NS_TCX = {"t": "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"}


def _parse_tcx(path: Path) -> list[ActivityRecord]:
    tree = ET.parse(path)
    records: list[ActivityRecord] = []
    def _f(trackpoint, tag: str, ns=_NS_TCX) -> float | None:
        el = trackpoint.find(tag, ns)
        return float(el.text) if el is not None and el.text else None

    for tp in tree.iterfind(".//t:Trackpoint", _NS_TCX):
        time_el = tp.find("t:Time", _NS_TCX)
        hr_el = tp.find("t:HeartRateBpm/t:Value", _NS_TCX)
        records.append(
            ActivityRecord(
                timestamp=_iso(time_el.text) if time_el is not None else None,
                latitude=_f(tp, "t:Position/t:LatitudeDegrees"),
                longitude=_f(tp, "t:Position/t:LongitudeDegrees"),
                altitude_m=_f(tp, "t:AltitudeMeters"),
                distance_m=_f(tp, "t:DistanceMeters"),
                heart_rate=float(hr_el.text) if hr_el is not None and hr_el.text else None,
                source_format="tcx",
            )
        )
    return records


def _parse_gpx(path: Path) -> list[ActivityRecord]:
    import gpxpy  # local import

    with open(path, encoding="utf-8") as fh:
        gpx = gpxpy.parse(fh)
    records: list[ActivityRecord] = []
    for track in gpx.tracks:
        for segment in track.segments:
            for pt in segment.points:
                hr = None
                # Heart rate lives in trackpoint extensions if present.
                for ext in pt.extensions or []:
                    for child in ext.iter():
                        if child.tag.endswith("hr") and child.text:
                            hr = float(child.text)
                records.append(
                    ActivityRecord(
                        timestamp=pt.time,
                        latitude=pt.latitude,
                        longitude=pt.longitude,
                        altitude_m=pt.elevation,
                        heart_rate=hr,
                        source_format="gpx",
                    )
                )
    return records


def _parse_csv(path: Path) -> list[ActivityRecord]:
    """Generic CSV: maps common column names (case-insensitive) to the schema."""
    records: list[ActivityRecord] = []
    with open(path, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            low = {k.lower().strip(): v for k, v in row.items()}
            records.append(
                ActivityRecord(
                    timestamp=_iso(low.get("timestamp") or low.get("time")),
                    latitude=_num(low.get("latitude") or low.get("lat")),
                    longitude=_num(low.get("longitude") or low.get("lon") or low.get("lng")),
                    altitude_m=_num(low.get("altitude") or low.get("elevation")),
                    distance_m=_num(low.get("distance")),
                    heart_rate=_num(low.get("heart_rate") or low.get("hr")),
                    cadence=_num(low.get("cadence")),
                    power_w=_num(low.get("power")),
                    speed_mps=_num(low.get("speed")),
                    source_format="csv",
                )
            )
    return records


def _parse_json(path: Path) -> list[ActivityRecord]:
    """JSON array of objects, or {"records": [...]}, using the same field names."""
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("records", data) if isinstance(data, dict) else data
    records: list[ActivityRecord] = []
    for row in rows:
        low = {str(k).lower(): v for k, v in row.items()}
        records.append(
            ActivityRecord(
                timestamp=_iso(low.get("timestamp") or low.get("time")),
                latitude=_num(low.get("latitude") or low.get("lat")),
                longitude=_num(low.get("longitude") or low.get("lon")),
                altitude_m=_num(low.get("altitude") or low.get("elevation")),
                distance_m=_num(low.get("distance")),
                heart_rate=_num(low.get("heart_rate") or low.get("hr")),
                cadence=_num(low.get("cadence")),
                power_w=_num(low.get("power")),
                speed_mps=_num(low.get("speed")),
                source_format="json",
            )
        )
    return records


# ---------------------------------------------------------------------------
# Helpers + dispatch
# ---------------------------------------------------------------------------
def _num(value) -> float | None:
    try:
        return float(value) if value not in (None, "") else None
    except (TypeError, ValueError):
        return None


def _iso(value) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


PARSERS = {
    ".fit": _parse_fit,
    ".tcx": _parse_tcx,
    ".gpx": _parse_gpx,
    ".csv": _parse_csv,
    ".json": _parse_json,
}


def parse_file(path: str | Path) -> list[ActivityRecord]:
    """Parse a single fitness file into normalized records."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    parser = PARSERS.get(path.suffix.lower())
    if not parser:
        raise ValueError(
            f"Unsupported format {path.suffix!r}. Supported: {', '.join(sorted(PARSERS))}"
        )
    records = parser(path)
    logger.info("Parsed %d records from %s (%s)", len(records), path.name, path.suffix)
    return records
