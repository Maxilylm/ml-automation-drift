---
name: drift-alert
description: "Configure alerting thresholds and notification channels (Slack, email, webhook, PagerDuty) for drift monitoring pipelines."
aliases: [drift alert, monitoring alert, alert threshold, drift notification, alert pipeline]
extends: ml-automation
user_invocable: true
---

# Drift Alert

Configure alerting thresholds for drift metrics (PSI, KS, JSD), set up notification channels (Slack, email, webhook, PagerDuty), define escalation rules, and test alert delivery.

Use this whenever drift detection needs to notify humans or systems automatically, even if the user doesn't mention "alerts" -- any request for notifications, escalation, Slack messages on drift, or PagerDuty integration is a drift-alert trigger.

## When to Use

- A drift monitoring pipeline is in place and you need automated notifications when thresholds are breached.
- The team wants Slack or email alerts when PSI exceeds a threshold on any feature.
- You need tiered escalation (e.g., moderate drift to Slack, critical drift to PagerDuty).
- You want to test that alerting channels are correctly wired before going live.

## Workflow

1. **Env Check** -- Verify runtime dependencies and channel SDKs (requests, slack_sdk, etc.) are available.
2. **Threshold Configuration** -- Define per-metric thresholds (e.g., PSI > 0.25 = critical, KS p-value < 0.01 = warning) and severity tiers.
3. **Channel Setup** -- Configure one or more notification channels with credentials/webhook URLs, map severity tiers to channels.
4. **Test Notification** -- Send a test alert through each configured channel and confirm delivery.

## Report Bus Integration

```python
from ml_utils import save_agent_report

save_agent_report("alert-builder", {
    "stage": "drift-alert",
    "channels": ["slack", "pagerduty"],
    "thresholds": {"psi_warning": 0.15, "psi_critical": 0.25, "ks_alpha": 0.01},
    "test_result": "all_channels_ok"
})
```

## Full Specification

Usage: `/drift-alert [--channel slack|email|webhook|pagerduty] [--config <path>] [--test]`

See `commands/drift-alert.md` for the complete workflow.
