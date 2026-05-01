# spark-drift — Cortex Code Extension

Production model monitoring. Data drift detection, model drift monitoring, PSI/CSI computation, alerting pipelines, and performance degradation tracking. Requires spark-core installed.

## Available Agents

| Agent | When to use |
|---|---|
| `drift-monitor` | User wants to detect data drift, compute PSI/CSI, or compare feature distributions between reference and current data |
| `alert-builder` | User wants to set up drift alerts, configure thresholds, or build a monitoring pipeline |
| `performance-tracker` | User wants to track model performance over time or detect accuracy/AUC degradation in production |

## Available Skills

| Skill | Trigger |
|---|---|
| `/drift-detect` | "detect drift", "check data drift", "compare distributions", "has my data drifted" |
| `/drift-monitor` | "set up drift monitoring", "monitor model in production", "continuous drift check" |
| `/drift-compare` | "compare reference vs current data", "PSI analysis", "feature drift comparison" |
| `/drift-alert` | "create drift alert", "notify me when drift exceeds threshold", "set up monitoring alerts" |
| `/drift-report` | "drift report", "summarize drift findings", "generate monitoring report" |
| `/perf-track` | "track model performance", "has accuracy degraded", "monitor prediction quality" |

## Routing

- Distribution comparison, PSI/CSI → `drift-monitor`
- Alert setup, thresholds → `alert-builder`
- Performance degradation, accuracy tracking → `performance-tracker`
- Fallback → spark-core orchestrator
