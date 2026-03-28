# /drift-detect

Detect data drift between reference and production datasets using PSI, CSI, KS test, and Jensen-Shannon divergence.

## Usage

```
/drift-detect <reference_data> <production_data> [--features <cols>] [--method psi,ks,js] [--threshold 0.25]
```

- `reference_data`: CSV/Parquet file with reference (training) distribution
- `production_data`: CSV/Parquet file with production (serving) distribution
- `--features`: comma-separated column names (default: all shared columns)
- `--method`: drift detection methods (default: psi,ks,js)
- `--threshold`: PSI threshold for flagging drift (default: 0.25)

## Workflow

### Stage 0: Environment Check

1. Check if `ml_utils.py` exists in `src/` -- if missing, copy from core plugin (`~/.claude/plugins/*/templates/ml_utils.py`)
2. Check if `drift_utils.py` exists in `src/` -- if missing, copy from this plugin's `templates/drift_utils.py`
3. Verify both data files exist and are readable (CSV or Parquet)

### Stage 1: Load and Validate Data

1. Load reference and production datasets
2. Identify shared columns between both datasets
3. Classify columns as numerical or categorical
4. If `--features` provided, validate all specified columns exist in both datasets
5. Report: row counts, column counts, shared columns, type classification

### Stage 2: Population Stability Index (PSI)

1. For each numerical feature:
   - Create quantile bins from reference distribution (10 bins default)
   - Bin production data using the same breakpoints
   - Compute PSI: sum((prod% - ref%) * ln(prod% / ref%))
   - Flag: < 0.1 stable, 0.1-0.25 moderate, > 0.25 significant
2. For each categorical feature:
   - Compute category frequencies in reference and production
   - Handle new categories in production (add to "other" bin)
   - Compute PSI across category bins
3. Report: per-feature PSI, drift status, top drifted features

### Stage 3: Kolmogorov-Smirnov Test

1. For each numerical feature:
   - Run two-sample KS test (reference vs production)
   - Record D-statistic and p-value
   - Apply Benjamini-Hochberg correction for multiple comparisons
   - Flag features with corrected p-value < 0.05
2. Report: per-feature KS results, significant features

### Stage 4: Jensen-Shannon Divergence

1. For each feature:
   - Compute histogram-based probability distributions (reference and production)
   - Compute JSD = 0.5 * KL(P||M) + 0.5 * KL(Q||M), where M = 0.5*(P+Q)
   - Range: 0 (identical) to 1 (maximally different)
2. Report: per-feature JSD scores

### Stage 5: Drift Summary Report

```python
from ml_utils import save_agent_report
save_agent_report("drift-monitor", {
    "status": "completed",
    "reference_rows": ref_rows,
    "production_rows": prod_rows,
    "features_analyzed": len(features),
    "drift_results": {
        "psi": per_feature_psi,
        "ks_test": per_feature_ks,
        "jensen_shannon": per_feature_jsd
    },
    "drifted_features": drifted_features,
    "drift_severity": overall_severity,
    "recommendations": recommendations
})
```

Write drift report to `reports/drift_detection_report.json`.

Print summary table with per-feature drift scores across all methods.
Print ranked list of drifted features with recommended actions.
