---
name: drift-report
description: "Generate comprehensive drift monitoring reports with distribution overlays, drift heatmaps, and executive summaries in HTML, JSON, or Markdown format."
aliases: [drift report, drift dashboard, drift visualization, monitoring report]
extends: ml-automation
user_invocable: true
---

# Drift Report

Generate a full drift monitoring report with per-feature distribution visualizations, drift heatmaps, executive summary, and actionable recommendations. Supports HTML, JSON, and Markdown output formats.

Use this whenever stakeholders need a shareable drift summary, even if the user doesn't mention "report" -- any request for drift visualization, distribution overlays, heatmaps, or executive-friendly output is a drift-report trigger.

## When to Use

- You have already run drift detection and need a presentable summary for stakeholders or an audit trail.
- The team wants distribution overlay plots comparing reference vs. production for each feature.
- You need a drift heatmap across features and time windows for a monitoring dashboard.
- A compliance or model risk review requires documented evidence of data stability.

## Workflow

1. **Env Check** -- Verify runtime dependencies (numpy, scipy, matplotlib/plotly for HTML) are available.
2. **Compute All Drift Metrics** -- Run PSI, KS test, and Jensen-Shannon divergence across all features between the reference and production datasets.
3. **Generate Report** -- Build the report in the requested format (HTML with interactive distribution overlays, JSON for programmatic consumption, or Markdown for documentation), including severity rankings, feature-level drill-downs, and recommendations.

## Report Bus Integration

```python
from ml_utils import save_agent_report

save_agent_report("drift-monitor", {
    "stage": "drift-report",
    "format": "html",
    "output_path": "reports/drift/drift_report_20260402.html",
    "summary": { "total_features": 42, "drifted_features": 5, "overall_severity": "moderate" }
})
```

## Full Specification

Usage: `/drift-report <reference_data> <production_data> [--format html|json|markdown]`

See `commands/drift-report.md` for the complete workflow.
