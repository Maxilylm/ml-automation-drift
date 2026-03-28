---
name: drift-compare
description: "Compare two dataset versions feature-by-feature with statistical tests, distribution overlays, and schema diff. Useful for training batch comparison or A/B population analysis."
aliases: [compare datasets, dataset comparison, feature comparison, batch comparison, distribution comparison]
extends: ml-automation
user_invocable: true
---

# Drift Compare

Compare two dataset versions feature-by-feature using PSI, KS test, Jensen-Shannon divergence, chi-squared test, and summary statistics. Identifies schema differences, new/disappeared categories, and ranks features by distributional shift magnitude.

## Full Specification

See `commands/drift-compare.md` for the complete workflow.
