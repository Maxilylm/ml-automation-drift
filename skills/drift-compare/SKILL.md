---
name: drift-compare
description: "Compare two dataset versions feature-by-feature with statistical tests, distribution overlays, and schema diff. Useful for training batch comparison or A/B population analysis."
aliases: [compare datasets, dataset comparison, feature comparison, batch comparison, distribution comparison]
extends: spark
user_invocable: true
---

# Drift Compare

Compare two dataset versions feature-by-feature using PSI, KS test, Jensen-Shannon divergence, chi-squared test, and summary statistics. Identifies schema differences, new/disappeared categories, and ranks features by distributional shift magnitude.

Use this whenever two datasets need side-by-side statistical comparison, even if the user doesn't mention "drift" -- any request to compare training batches, validate A/B population balance, or diff dataset versions is a drift-compare trigger.

## When to Use

- You have two training batches from different time periods and want to verify consistency before retraining.
- An A/B test requires confirmation that control and treatment populations have balanced feature distributions.
- A new data vendor or pipeline change has landed and you need to validate that the output schema and distributions match the previous version.
- You want a detailed feature-by-feature breakdown rather than an aggregate drift score.

## Workflow

1. **Env Check** -- Verify runtime dependencies (numpy, scipy, pandas) are available.
2. **Schema Comparison** -- Align column names and types between the two datasets, flag added/removed columns, detect type mismatches.
3. **Feature-by-Feature Statistical Tests** -- For each shared feature, compute PSI, KS test, Jensen-Shannon divergence, and chi-squared test (for categoricals). Rank features by shift magnitude.
4. **Distribution Overlays** -- Generate side-by-side distribution plots for the top shifted features, annotated with test statistics and severity labels.

## Report Bus Integration

```python
from ml_utils import save_agent_report

save_agent_report("drift-monitor", {
    "stage": "drift-compare",
    "dataset_a": "data/train_v1.csv",
    "dataset_b": "data/train_v2.csv",
    "schema_diff": {"added": ["new_col"], "removed": [], "type_mismatches": []},
    "top_shifted": ["income", "age", "zip_code"],
    "summary": { "total_features": 38, "significant_features": 4 }
})
```

## Full Specification

Usage: `/drift-compare <dataset_a> <dataset_b> [--features <cols>] [--labels "baseline,current"]`

See `commands/drift-compare.md` for the complete workflow.
