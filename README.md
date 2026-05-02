# spark-drift

Production monitoring extension for [ml-automation](https://github.com/BLEND360/ml-automation-core).

## Prerequisites

- [ml-automation](https://github.com/BLEND360/ml-automation-core) core plugin (>= v1.8.0)
- Claude Code CLI
- Python with numpy and scipy for drift computation

## Installation

```bash
claude plugin add /path/to/spark-drift
```

## What's Included

### Agents

| Agent | Purpose | Hooks Into |
|---|---|---|
| `drift-monitor` | Data drift detection -- PSI, CSI, KS test, feature distributions | `after-evaluation` |
| `performance-tracker` | Model performance degradation, concept drift, retraining triggers | `after-deploy` |
| `alert-builder` | Alerting pipelines for drift and performance thresholds | *(direct invocation)* |

### Commands

| Command | Purpose |
|---|---|
| `/drift-detect` | Detect data drift between reference and production datasets |
| `/drift-monitor` | Set up continuous drift monitoring pipeline |
| `/drift-report` | Generate drift monitoring report with visualizations |
| `/perf-track` | Track model performance metrics over time |
| `/drift-alert` | Configure alerting thresholds and notification channels |
| `/drift-compare` | Compare two dataset versions feature-by-feature |

## Getting Started

```bash
# Detect drift between reference and production data
/drift-detect data/reference.csv data/production.csv --method psi,ks,js --threshold 0.25

# Set up continuous monitoring
/drift-monitor data/training.csv --schedule daily --output-dir reports/drift/

# Generate a drift report
/drift-report data/reference.csv data/production.csv --format html

# Track model performance over time
/perf-track logs/metrics.csv --metrics accuracy,auc,f1 --window 7d

# Configure alerting
/drift-alert --channel slack,email --test

# Compare two dataset versions
/drift-compare data/batch_v1.csv data/batch_v2.csv --labels "Jan 2026,Feb 2026"
```

## How It Integrates

When installed alongside the core plugin:

1. **Automatic routing** -- Tasks mentioning drift detection, PSI, CSI, monitoring, or performance degradation are routed to drift agents
2. **Core workflow hooks** -- When running `/team-coldstart`:
   - `drift-monitor` fires at `after-evaluation` to check for data drift in production datasets
   - `performance-tracker` fires at `after-deploy` to set up performance tracking
3. **Core agent reuse** -- Commands use eda-analyst, developer, ml-theory-advisor from core

## License

MIT
