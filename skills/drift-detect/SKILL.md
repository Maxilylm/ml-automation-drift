---
name: drift-detect
description: "Detect data drift between reference and production datasets using PSI, CSI, KS test, and Jensen-Shannon divergence. Flags features with significant distributional shift."
aliases: [detect drift, data drift, psi check, distribution shift, feature drift]
extends: spark
user_invocable: true
---

# Drift Detect

Run statistical drift detection between a reference dataset (training distribution) and a production dataset (serving distribution). Computes PSI, KS test, and Jensen-Shannon divergence per feature, flags drifted features by severity, and recommends actions.

Use this whenever a model has been deployed and new data arrives, even if the user doesn't mention "drift" -- any question about production data quality, feature stability, or model input health is a drift-detect trigger.

## When to Use

- A model is in production and you need to verify that input features still match the training distribution.
- New batch data has arrived and you want to check for distributional shift before scoring.
- Model performance has degraded and you suspect upstream data changes rather than concept drift.
- You need a one-off drift snapshot (for continuous monitoring, see `/drift-monitor` instead).

## Workflow

1. **Env Check** -- Verify numpy/scipy are available; install if missing.
2. **Load & Validate** -- Read reference and production datasets, align schemas, report missing columns.
3. **PSI Computation** -- Compute Population Stability Index per feature using quantile-based binning.
4. **KS Test** -- Run two-sample Kolmogorov-Smirnov test with Benjamini-Hochberg correction.
5. **Jensen-Shannon Divergence** -- Compute symmetric JSD per feature, bounded [0, 1].
6. **Summary with Severity Ranking** -- Aggregate all metrics, assign severity scores, rank features, and emit actionable recommendations.

## Report Bus Integration

```python
from ml_utils import save_agent_report

save_agent_report("drift-monitor", {
    "stage": "drift-detect",
    "summary": { "total_features": 42, "drifted_features": 5, "overall_severity": "moderate" },
    "top_drifted": ["income", "age", "zip_code", "tenure", "balance"],
    "recommendations": ["Investigate top drifted features", "Consider retraining"]
})
```

## Full Specification

Usage: `/drift-detect <reference_data> <production_data> [--features <cols>] [--method psi,ks,js] [--threshold 0.25]`

See `commands/drift-detect.md` for the complete workflow.
