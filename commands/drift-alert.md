# /drift-alert

Configure alerting thresholds and notification channels for drift monitoring.

## Usage

```
/drift-alert [--channel slack|email|webhook|pagerduty] [--config <path>] [--test]
```

- `--channel`: notification channel to configure (can specify multiple)
- `--config`: existing alert config file to update (default: `monitoring_config.yaml`)
- `--test`: send a test alert to verify configuration

## Workflow

### Stage 0: Environment Check

1. Check if `ml_utils.py` exists in `src/` -- if missing, copy from core plugin
2. Check if `drift_utils.py` exists in `src/` -- if missing, copy from this plugin's `templates/drift_utils.py`
3. Load existing monitoring config if present

### Stage 1: Threshold Configuration

1. Define drift alert thresholds:
   - PSI warning: 0.1, critical: 0.25
   - KS test p-value: 0.05 (warning), 0.01 (critical)
   - JSD warning: 0.1, critical: 0.3
   - Performance metric drop: 5% (warning), 10% (critical)
2. Allow per-feature threshold overrides
3. Configure composite rules (e.g., drift + performance drop together)
4. Save thresholds to config file

### Stage 2: Notification Channel Setup

For each `--channel`:

1. **Slack**:
   - Configure webhook URL (from env var `DRIFT_SLACK_WEBHOOK` or user input)
   - Set channel name and mention rules (@here for warning, @channel for critical)
   - Format: color-coded message with drift summary table

2. **Email**:
   - Configure SMTP settings (host, port, credentials from env vars)
   - Set recipient list (warning recipients, critical recipients)
   - Format: HTML email with embedded drift charts

3. **Webhook**:
   - Configure endpoint URL and authentication headers
   - Set payload template (JSON with drift metrics)
   - Configure retry policy (3 retries, exponential backoff)

4. **PagerDuty**:
   - Configure integration key (from env var `DRIFT_PAGERDUTY_KEY`)
   - Map severity levels to PagerDuty urgency
   - Set deduplication key to prevent duplicate incidents

### Stage 3: Alert Pipeline Configuration

1. Set deduplication window (don't re-alert same feature within 24h)
2. Set escalation rules:
   - Warning: notify via configured channels
   - Critical (persists > 1h): escalate to PagerDuty
   - Resolved: send resolution notification
3. Configure alert suppression during maintenance windows
4. Save full pipeline config

### Stage 4: Test Alerts (if --test)

1. Send test alert to each configured channel
2. Verify delivery (check webhook response codes)
3. Report: channel status (success/failure), sample alert content

### Stage 5: Report

```python
from ml_utils import save_agent_report
save_agent_report("alert-builder", {
    "status": "completed",
    "thresholds": configured_thresholds,
    "channels": configured_channels,
    "escalation_rules": escalation_rules,
    "config_path": config_path,
    "test_results": test_results if test else None
})
```

Print configured alert rules summary.
Print notification channel status.
