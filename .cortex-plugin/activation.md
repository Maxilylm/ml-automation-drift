---
name: spark-drift
description: >
  Suggest enabling the spark-drift plugin when the user asks about data drift,
  model drift, production monitoring, PSI (Population Stability Index), CSI
  (Characteristic Stability Index), performance degradation tracking, model
  health alerts, or detecting distribution shift in production data.
  Do NOT attempt to perform these tasks — just let the user know the plugin
  can be enabled.
---

# spark-drift (disabled plugin)

This plugin is installed but not enabled. It provides production monitoring
and drift detection automation within Cortex Code, integrated with the
spark-core workflow.

## Agents (3)

- **alert-builder** — Alerting pipeline setup, threshold configuration, notification routing
- **drift-monitor** — Continuous drift monitoring, PSI/CSI computation, drift reporting
- **performance-tracker** — Model performance degradation tracking and benchmarking

## Skills (6)

- **drift-alert** — Configure and test drift alerting pipelines
- **drift-compare** — Compare data distributions across time windows
- **drift-detect** — Detect data and concept drift with statistical tests
- **drift-monitor** — Set up continuous production monitoring dashboards
- **drift-report** — Generate drift and performance degradation reports
- **perf-track** — Track model performance metrics over time in production

## Requires

- spark-core plugin

## Enable

    cortex plugin enable spark-drift

Do NOT attempt to perform drift monitoring tasks through this plugin's skills while it is disabled.
