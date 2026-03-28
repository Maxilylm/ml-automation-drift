# /drift-monitor

Set up a continuous drift monitoring pipeline for production models.

## Usage

```
/drift-monitor <reference_data> [--schedule daily|weekly|hourly] [--features <cols>] [--output-dir reports/drift/]
```

- `reference_data`: CSV/Parquet file with reference distribution (typically training data)
- `--schedule`: monitoring frequency (default: daily)
- `--features`: comma-separated columns to monitor (default: all)
- `--output-dir`: directory for monitoring reports (default: `reports/drift/`)

## Workflow

### Stage 0: Environment Check

1. Check if `ml_utils.py` exists in `src/` -- if missing, copy from core plugin
2. Check if `drift_utils.py` exists in `src/` -- if missing, copy from this plugin's `templates/drift_utils.py`
3. Verify reference data exists and create output directory

### Stage 1: Reference Snapshot

1. Load reference data and compute baseline statistics:
   - Per-feature mean, std, quantiles (numerical)
   - Per-feature category frequencies (categorical)
   - Per-feature missing value rates
2. Save reference snapshot to `drift_snapshots/reference_snapshot.json`
3. Report: feature count, row count, snapshot path

### Stage 2: Monitoring Configuration

1. Generate monitoring config file (`monitoring_config.yaml`):
   - Features to monitor with types
   - PSI thresholds per feature (default: 0.25 critical, 0.1 warning)
   - KS test significance level (default: 0.05)
   - Schedule (cron expression from `--schedule`)
   - Output directory path
2. Configure alert thresholds (defaults, user can customize later)
3. Report: config file path, monitoring schedule

### Stage 3: Pipeline Script Generation

1. Generate `scripts/run_drift_check.py`:
   - Load reference snapshot
   - Load latest production data (from configurable source)
   - Run PSI, KS test, JSD on all monitored features
   - Generate timestamped report
   - Trigger alerts if thresholds exceeded
2. Generate `scripts/drift_cron.sh` (wrapper for cron scheduling)
3. Report: generated script paths, cron command

### Stage 4: Initial Validation Run

1. Run the generated pipeline against reference data (self-check):
   - All PSI scores should be ~0 (same distribution)
   - All KS p-values should be > 0.05
2. Verify pipeline produces valid report JSON
3. Report: validation status, sample report path

### Stage 5: Report

```python
from ml_utils import save_agent_report
save_agent_report("drift-monitor", {
    "status": "completed",
    "pipeline_type": "continuous_monitoring",
    "reference_snapshot": snapshot_path,
    "config_path": config_path,
    "pipeline_script": script_path,
    "schedule": schedule,
    "features_monitored": len(features),
    "validation": validation_result
})
```

Print setup summary with instructions for activating the cron schedule.
