---
name: data_parser
description: (Reference) Normalization contract for fitness file parsing.
---

NOTE: Parsing is done deterministically in code (`packages/fitness_agents/parsers.py`), not by
an LLM — file parsing must be exact. This file documents the normalization contract that the
parser fills and the agents consume.

Every supported file (`.fit`, `.tcx`, `.gpx`, `.csv`, `.json`) is normalized to a list of
`ActivityRecord` samples with these fields:

- `timestamp` — ISO datetime of the sample
- `latitude`, `longitude`, `altitude_m`
- `distance_m` — cumulative distance (or integrated from GPS)
- `heart_rate` (bpm), `cadence`, `power_w`, `speed_mps`
- `source_format`

`metrics.py` then reduces these to an `ActivitySummary` (distance, duration, pace, HR, power,
elevation gain) which is what the analyst, planner, and reviewer agents actually read.

To support a new format, add a parser function returning `list[ActivityRecord]` and register
its extension in `PARSERS`.
