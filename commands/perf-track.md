# /perf-track

Track model performance metrics over time. Detect degradation, concept drift, and retraining triggers.

## Usage

```
/perf-track <metrics_log> [--metrics accuracy,auc,f1] [--window 7d] [--baseline <path>]
```

- `metrics_log`: CSV/JSON file with timestamped performance metrics (columns: timestamp, metric_name, value)
- `--metrics`: metrics to track (default: all found in log)
- `--window`: rolling window size for trend analysis (default: 7d)
- `--baseline`: reference performance file for comparison

## Workflow

### Stage 0: Environment Check

1. Check if `ml_utils.py` exists in `src/` -- if missing, copy from core plugin
2. Check if `drift_utils.py` exists in `src/` -- if missing, copy from this plugin's `templates/drift_utils.py`
3. Verify metrics log file exists and parse format

### Stage 1: Load and Parse Metrics

1. Load metrics log (CSV with timestamp + metric columns, or JSON array)
2. Parse timestamps and sort chronologically
3. Identify available metrics and time range
4. Report: metric names, time range, observation count, data frequency

### Stage 2: Trend Analysis

1. For each metric:
   - Compute rolling mean and std over `--window`
   - Fit linear trend (slope indicates direction of change)
   - Compute EWMA (exponential weighted moving average) for smoothing
   - Identify monotonic decline stretches
2. If `--baseline` provided: compute relative change from baseline
3. Report: per-metric trend direction, magnitude, current vs baseline

### Stage 3: Change Point Detection

1. For each metric:
   - Run CUSUM control chart analysis
   - Run Page-Hinkley test for abrupt changes
   - Identify statistically significant change points with timestamps
   - Classify: gradual decay vs sudden drop vs oscillation
2. Report: detected change points with dates and confidence

### Stage 4: Retraining Trigger Evaluation

1. Apply trigger rules:
   - Absolute threshold: metric below minimum acceptable value
   - Relative decay: metric dropped > X% from baseline
   - Consecutive decline: metric declining for N consecutive windows
   - Statistical trigger: change point detected with high confidence
2. Compute trigger score (0-100) based on combined signals
3. Recommendation: retrain (score > 70), investigate (30-70), stable (< 30)

### Stage 5: Report

```python
from ml_utils import save_agent_report
save_agent_report("performance-tracker", {
    "status": "completed",
    "time_range": {"start": start_ts, "end": end_ts},
    "metrics_tracked": metrics_list,
    "trends": per_metric_trends,
    "change_points": detected_change_points,
    "trigger_score": trigger_score,
    "recommendation": recommendation,
    "current_performance": current_metrics
})
```

Write performance report to `reports/performance_tracking_report.json`.

Print metric trend summary table.
Print retraining recommendation with supporting evidence.
