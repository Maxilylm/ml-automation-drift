---
name: drift-monitor
description: "Set up continuous drift monitoring pipeline with scheduled checks, reference snapshots, and automated drift detection scripts."
aliases: [monitor drift, continuous monitoring, drift pipeline, production monitoring]
extends: ml-automation
user_invocable: true
---

# Drift Monitor

Set up a continuous drift monitoring pipeline that takes a reference snapshot, generates scheduled drift detection scripts, configures thresholds, and validates the pipeline with an initial self-check run.

Use this whenever a model needs ongoing production surveillance, even if the user doesn't mention "monitoring" -- any request for scheduled checks, recurring drift reports, or automated data quality gates is a drift-monitor trigger.

## When to Use

- You need continuous, scheduled drift detection rather than a one-off check.
- A model is moving to production and requires a monitoring harness as part of the deployment checklist.
- The team wants automated daily/weekly drift snapshots written to a reports directory.
- You are setting up a CI/CD gate that blocks deployment when drift exceeds thresholds.

## Workflow

1. **Env Check** -- Verify runtime dependencies (numpy, scipy, pandas) are available.
2. **Reference Snapshot** -- Load the reference dataset (typically training data), compute and persist baseline statistics and bin edges.
3. **Schedule Setup** -- Generate a monitoring script with the chosen cadence (daily, weekly, or hourly) and output directory configuration.
4. **Monitoring Pipeline** -- Wire drift-detect logic into the scheduled script, configure thresholds, run an initial self-check to validate end-to-end, and report results.

## Report Bus Integration

```python
from ml_utils import save_agent_report

save_agent_report("drift-monitor", {
    "stage": "drift-monitor-setup",
    "schedule": "daily",
    "reference_snapshot": "data/reference/snapshot_20260402.parquet",
    "output_dir": "reports/drift/",
    "self_check": "passed"
})
```

## Full Specification

Usage: `/drift-monitor <reference_data> [--schedule daily|weekly|hourly] [--features <cols>] [--output-dir reports/drift/]`

See `commands/drift-monitor.md` for the complete workflow.
