# /drift-report

Generate a comprehensive drift monitoring report with visualizations.

## Usage

```
/drift-report <reference_data> <production_data> [--format html|json|markdown] [--output reports/drift_report]
```

- `reference_data`: CSV/Parquet file with reference distribution
- `production_data`: CSV/Parquet file with production distribution
- `--format`: report format (default: html)
- `--output`: output path without extension (default: `reports/drift_report`)

## Workflow

### Stage 0: Environment Check

1. Check if `ml_utils.py` exists in `src/` -- if missing, copy from core plugin
2. Check if `drift_utils.py` exists in `src/` -- if missing, copy from this plugin's `templates/drift_utils.py`
3. Verify data files exist and are readable

### Stage 1: Compute All Drift Metrics

1. Load reference and production datasets
2. For every shared feature compute:
   - PSI (with per-bin breakdown)
   - KS test (D-statistic, p-value)
   - Jensen-Shannon divergence
   - Missing value rate change
   - Mean/median shift (numerical) or frequency change (categorical)
3. Store all metrics in structured dict

### Stage 2: Feature-Level Visualizations

1. Per-feature distribution overlays:
   - Reference histogram (blue) vs production histogram (red)
   - KDE overlay for smooth comparison
   - Annotated PSI score and drift status
2. Per-feature QQ plots (reference quantiles vs production quantiles)
3. Drift heatmap: features x metrics matrix with color-coded severity
4. Save all figures to `reports/drift_figures/`

### Stage 3: Summary Dashboard

1. Executive summary:
   - Total features analyzed
   - Features with significant drift (count, percentage)
   - Top 5 most drifted features
   - Overall drift severity (low/moderate/high/critical)
2. Drift timeline (if historical snapshots exist in `drift_snapshots/`)
3. Recommendations section:
   - Features requiring investigation
   - Suggested retraining triggers
   - Data quality issues detected

### Stage 4: Report Generation

1. If `--format html`: generate self-contained HTML with embedded charts
2. If `--format json`: structured JSON with all metrics and figure paths
3. If `--format markdown`: readable markdown with inline base64 images
4. Save to `--output` path with appropriate extension

### Stage 5: Report Bus

```python
from ml_utils import save_agent_report
save_agent_report("drift-monitor", {
    "status": "completed",
    "report_type": "drift_report",
    "format": report_format,
    "output_path": output_path,
    "features_analyzed": len(features),
    "drifted_features": len(drifted),
    "overall_severity": severity,
    "figures_generated": len(figures)
})
```

Print report path and summary statistics.
