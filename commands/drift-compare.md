# /drift-compare

Compare two dataset versions feature-by-feature. Useful for comparing training batches, A/B test populations, or temporal slices.

## Usage

```
/drift-compare <dataset_a> <dataset_b> [--features <cols>] [--labels "baseline,current"] [--output reports/drift_comparison]
```

- `dataset_a`: first dataset (CSV/Parquet)
- `dataset_b`: second dataset (CSV/Parquet)
- `--features`: comma-separated columns to compare (default: all shared)
- `--labels`: names for the two datasets (default: "Dataset A,Dataset B")
- `--output`: output path for comparison report

## Workflow

### Stage 0: Environment Check

1. Check if `ml_utils.py` exists in `src/` -- if missing, copy from core plugin
2. Check if `drift_utils.py` exists in `src/` -- if missing, copy from this plugin's `templates/drift_utils.py`
3. Verify both dataset files exist and are readable

### Stage 1: Schema Comparison

1. Load both datasets and identify:
   - Columns only in dataset A
   - Columns only in dataset B
   - Shared columns (these are compared)
2. For shared columns, check type consistency
3. Report: schema diff summary, shared column count

### Stage 2: Statistical Comparison (Numerical Features)

For each shared numerical column:
1. Summary statistics side-by-side: count, mean, std, min, Q1, median, Q3, max
2. PSI score between distributions
3. KS test (D-statistic, p-value)
4. Jensen-Shannon divergence
5. Mean shift magnitude (in standard deviations)
6. Missing value rate comparison

### Stage 3: Statistical Comparison (Categorical Features)

For each shared categorical column:
1. Category frequency comparison (side-by-side percentages)
2. New categories in dataset B not present in dataset A
3. Disappeared categories (in A but not B)
4. Chi-squared test of independence
5. PSI across category bins
6. Missing value rate comparison

### Stage 4: Visualization

1. Side-by-side distribution plots per feature
2. Drift score comparison bar chart (features ranked by PSI)
3. Summary heatmap: features x metrics
4. Save figures to `reports/comparison_figures/`

### Stage 5: Report

```python
from ml_utils import save_agent_report
save_agent_report("drift-monitor", {
    "status": "completed",
    "report_type": "dataset_comparison",
    "dataset_a": {"path": path_a, "rows": rows_a, "cols": cols_a},
    "dataset_b": {"path": path_b, "rows": rows_b, "cols": cols_b},
    "shared_features": len(shared),
    "drifted_features": len(drifted),
    "comparison_results": per_feature_results,
    "schema_diff": schema_diff
})
```

Print feature-by-feature comparison table.
Print ranked list of features with largest distributional differences.
