---
name: perf-track
description: "Track model performance metrics over time. Detect degradation trends, change points, concept drift, and evaluate retraining triggers."
aliases: [track performance, model monitoring, metric decay, performance degradation, retraining trigger]
extends: ml-automation
user_invocable: true
---

# Performance Track

Track model performance metrics over time windows, detect degradation trends using CUSUM and Page-Hinkley tests, identify change points, and evaluate whether retraining is warranted based on combined drift and performance signals.

Use this whenever a model's predictive quality needs to be assessed over time, even if the user doesn't mention "performance tracking" -- any question about accuracy decay, metric trends, retraining timing, or concept drift is a perf-track trigger.

## When to Use

- Model accuracy, AUC, or F1 has been logged over time and you need trend analysis.
- You suspect concept drift (labels have shifted) rather than just data drift.
- The team needs an automated retraining trigger based on performance degradation thresholds.
- You want to identify exact change points where model quality dropped.

## Workflow

1. **Env Check** -- Verify runtime dependencies (numpy, scipy) are available.
2. **Load Metrics** -- Read the metrics log (CSV/JSON with timestamps and metric values), validate schema, align to the requested time window.
3. **Trend Analysis** -- Compute rolling statistics, linear trend slope, EWMA smoothing, CUSUM control chart, and Page-Hinkley change point detection.
4. **Retraining Triggers** -- Score degradation severity (0-100), emit a recommendation (stable / investigate / retrain) with supporting evidence and change-point timestamps.

## Report Bus Integration

```python
from ml_utils import save_agent_report

save_agent_report("performance-tracker", {
    "stage": "perf-track",
    "trend": "declining",
    "trigger_score": 72,
    "recommendation": "retrain",
    "change_points": [{"timestamp": "2026-03-28", "direction": "decrease", "magnitude": -0.04}],
    "current_accuracy": 0.81,
    "baseline_accuracy": 0.87
})
```

## Full Specification

Usage: `/perf-track <metrics_log> [--metrics accuracy,auc,f1] [--window 7d] [--baseline <path>]`

See `commands/perf-track.md` for the complete workflow.
