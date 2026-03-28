---
name: drift-detect
description: "Detect data drift between reference and production datasets using PSI, CSI, KS test, and Jensen-Shannon divergence. Flags features with significant distributional shift."
aliases: [detect drift, data drift, psi check, distribution shift, feature drift]
extends: ml-automation
user_invocable: true
---

# Drift Detect

Run statistical drift detection between a reference dataset (training distribution) and a production dataset (serving distribution). Computes PSI, KS test, and Jensen-Shannon divergence per feature, flags drifted features by severity, and recommends actions.

## Full Specification

See `commands/drift-detect.md` for the complete workflow.
