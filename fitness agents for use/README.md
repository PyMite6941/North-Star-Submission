# Component 3 — Fitness MD Agents

Looks at **uploaded fitness files** and data types, analyzes the user's progress, and creates
a **growth plan** to help them improve physically.

Library: `packages/fitness_agents`. Pipeline (LangGraph):

```
parse_files → compute_metrics → analyze → plan → review
```

The three reasoning steps are **markdown-defined agents** in [`agent mds/`](agent%20mds) —
edit a file to change an agent's behaviour, no code change needed. Parsing is deterministic
code (file formats must be exact).

## Supported file formats

`.fit` · `.tcx` · `.gpx` · `.csv` · `.json` — all normalized to a common `ActivityRecord`
schema, then summarized (distance, duration, pace, HR, power, elevation gain).

## Agents (`agent mds/`)

| File | Role |
|------|------|
| `fitness_analyst.md` | Assess current fitness, strengths, weaknesses. |
| `growth_planner.md` | Build a concrete, progressive plan from the analysis. |
| `plan_reviewer.md` | Review the plan for safety/realism, output the final version. |
| `data_parser.md` | Reference: the normalization contract (parsing is in code). |

## Run

```bash
polaris-fitness agents                                   # list agents
polaris-fitness parse "fitness agents for use/sample_data/run.csv"
polaris-fitness analyze "fitness agents for use/sample_data/run.csv" --goal "run a sub-25 5K"

# without entry points:
python "fitness agents for use/core programs/analyze.py" "fitness agents for use/sample_data/run.csv"
```

`core programs/` holds the runnable entry scripts; `sample_data/` holds an example file you can
analyze immediately.
