"""
Drift detection utilities for the ml-automation-drift extension plugin.

Requires ml_utils.py from the ml-automation core plugin to be present
in the same directory (copied via Stage 0 of drift commands).
"""

import os
import json
import math
from pathlib import Path
from collections import Counter
from typing import List, Dict, Optional, Tuple, Any


# --- Relevance Detection ---

DRIFT_INDICATORS = {
    "evidently",
    "nannyml",
    "alibi_detect",
    "alibi-detect",
    "whylogs",
    "scipy.stats",
    "great_expectations",
    "deepchecks",
    "soda",
}

MONITORING_PATTERNS = [
    r"drift_snapshots?/",
    r"monitoring_config",
    r"reference.*snapshot",
    r"psi_threshold",
    r"drift.*report",
    r"production.*data",
]


def detect_drift_relevance(project_path="."):
    """Check if project has production monitoring indicators for relevance gating.

    Checks: monitoring library imports, reference/production data directories,
    drift configuration files, existing drift reports, timestamped prediction logs.

    Args:
        project_path: root directory of the project

    Returns:
        dict with 'is_drift_relevant': bool, 'indicators': list of found indicators
    """
    indicators = []
    project = Path(project_path)

    # Check for reference/production data directories
    for data_dir in ["data/reference", "data/production", "data/baseline",
                     "drift_snapshots", "monitoring_state"]:
        dir_path = project / data_dir
        if dir_path.is_dir():
            file_count = len(list(dir_path.glob("*")))
            if file_count > 0:
                indicators.append(f"{data_dir}/ directory with {file_count} files")

    # Check for drift reports
    drift_report_dir = project / "reports" / "drift"
    if drift_report_dir.is_dir():
        reports = list(drift_report_dir.glob("*.json"))
        if reports:
            indicators.append(f"Existing drift reports: {len(reports)} files")

    # Check for monitoring config
    for config_name in ["monitoring_config.yaml", "monitoring_config.yml",
                        "monitoring_config.json", "drift_config.yaml"]:
        if (project / config_name).exists():
            indicators.append(f"Monitoring config: {config_name}")

    # Check requirements for monitoring packages
    for req_file in ["requirements.txt", "pyproject.toml", "setup.py", "Pipfile"]:
        req_path = project / req_file
        if req_path.exists():
            try:
                content = req_path.read_text().lower()
                for pkg in DRIFT_INDICATORS:
                    if pkg.replace("_", "-") in content or pkg.replace("-", "_") in content:
                        indicators.append(f"{pkg} in {req_file}")
            except (UnicodeDecodeError, PermissionError):
                continue

    # Check Python files for monitoring imports
    py_files = list(project.glob("**/*.py"))[:50]  # limit scan
    for py_file in py_files:
        try:
            content = py_file.read_text()
            for pkg in DRIFT_INDICATORS:
                normalized = pkg.replace("-", "_")
                if f"import {normalized}" in content or f"from {normalized}" in content:
                    indicators.append(f"{pkg} import in {py_file.name}")
                    break
        except (UnicodeDecodeError, PermissionError):
            continue

    # Check for CSV/Parquet files with timestamp columns (production data signal)
    csv_files = list(project.glob("**/*.csv"))[:10]
    for csv_file in csv_files:
        try:
            with open(csv_file) as f:
                header = f.readline().strip().lower()
                if any(ts in header for ts in ["timestamp", "created_at", "prediction_date",
                                                "serving_date", "inference_time"]):
                    indicators.append(f"Timestamped data: {csv_file.name}")
        except (UnicodeDecodeError, PermissionError):
            continue

    return {
        "is_drift_relevant": len(indicators) > 0,
        "indicators": indicators,
    }


# --- Population Stability Index (PSI) ---

def compute_psi(reference: List[float], production: List[float],
                n_bins: int = 10, method: str = "quantile") -> Dict[str, Any]:
    """Compute Population Stability Index between two distributions.

    PSI measures how much a distribution has shifted from a reference.
    PSI < 0.1: no significant shift
    PSI 0.1-0.25: moderate shift (investigate)
    PSI > 0.25: significant shift (action required)

    Args:
        reference: list of values from reference distribution
        production: list of values from production distribution
        n_bins: number of bins (default: 10)
        method: binning method -- 'quantile' or 'fixed' (default: quantile)

    Returns:
        dict with 'psi': float, 'per_bin': list of dicts, 'status': str,
        'n_bins': int, 'reference_count': int, 'production_count': int
    """
    import numpy as np

    ref = np.array(reference, dtype=float)
    prod = np.array(production, dtype=float)

    # Remove NaNs
    ref = ref[~np.isnan(ref)]
    prod = prod[~np.isnan(prod)]

    if len(ref) == 0 or len(prod) == 0:
        return {
            "psi": float("nan"),
            "per_bin": [],
            "status": "error",
            "error": "Empty distribution after removing NaNs",
        }

    # Create bins from reference distribution
    if method == "quantile":
        quantiles = np.linspace(0, 100, n_bins + 1)
        bin_edges = np.unique(np.percentile(ref, quantiles))
    else:
        bin_edges = np.linspace(ref.min(), ref.max(), n_bins + 1)

    # Ensure production values outside reference range are captured
    bin_edges[0] = min(ref.min(), prod.min()) - 1e-6
    bin_edges[-1] = max(ref.max(), prod.max()) + 1e-6

    # Compute bin frequencies
    ref_counts, _ = np.histogram(ref, bins=bin_edges)
    prod_counts, _ = np.histogram(prod, bins=bin_edges)

    # Convert to proportions with smoothing to avoid division by zero
    epsilon = 1e-4
    ref_pct = (ref_counts + epsilon) / (ref_counts.sum() + epsilon * len(ref_counts))
    prod_pct = (prod_counts + epsilon) / (prod_counts.sum() + epsilon * len(prod_counts))

    # Compute PSI per bin
    per_bin = []
    psi_total = 0.0
    for i in range(len(ref_counts)):
        psi_i = (prod_pct[i] - ref_pct[i]) * math.log(prod_pct[i] / ref_pct[i])
        psi_total += psi_i
        per_bin.append({
            "bin_index": i,
            "bin_range": [float(bin_edges[i]), float(bin_edges[i + 1])],
            "reference_pct": round(float(ref_pct[i]), 6),
            "production_pct": round(float(prod_pct[i]), 6),
            "psi_contribution": round(float(psi_i), 6),
        })

    # Determine status
    if psi_total < 0.1:
        status = "stable"
    elif psi_total < 0.25:
        status = "moderate_shift"
    else:
        status = "significant_drift"

    return {
        "psi": round(float(psi_total), 6),
        "per_bin": per_bin,
        "status": status,
        "n_bins": len(per_bin),
        "reference_count": len(ref),
        "production_count": len(prod),
    }


# --- Characteristic Stability Index (CSI) ---

def compute_csi(reference_scores: List[float], production_scores: List[float],
                bin_edges: List[float]) -> Dict[str, Any]:
    """Compute Characteristic Stability Index for scorecard models.

    CSI is similar to PSI but uses predefined score bin edges (e.g.,
    scorecard ranges) to identify which score bands shifted most.

    Args:
        reference_scores: list of scores from reference period
        production_scores: list of scores from production period
        bin_edges: list of bin edge values defining score ranges

    Returns:
        dict with 'csi': float, 'per_bin': list of dicts, 'status': str
    """
    import numpy as np

    ref = np.array(reference_scores, dtype=float)
    prod = np.array(production_scores, dtype=float)

    ref = ref[~np.isnan(ref)]
    prod = prod[~np.isnan(prod)]

    edges = np.array(bin_edges, dtype=float)

    ref_counts, _ = np.histogram(ref, bins=edges)
    prod_counts, _ = np.histogram(prod, bins=edges)

    epsilon = 1e-4
    ref_pct = (ref_counts + epsilon) / (ref_counts.sum() + epsilon * len(ref_counts))
    prod_pct = (prod_counts + epsilon) / (prod_counts.sum() + epsilon * len(prod_counts))

    per_bin = []
    csi_total = 0.0
    for i in range(len(ref_counts)):
        csi_i = (prod_pct[i] - ref_pct[i]) * math.log(prod_pct[i] / ref_pct[i])
        csi_total += csi_i

        # Determine shift direction
        shift = "right_shift" if prod_pct[i] > ref_pct[i] else "left_shift"
        if abs(prod_pct[i] - ref_pct[i]) < 0.01:
            shift = "stable"

        per_bin.append({
            "bin_index": i,
            "bin_range": [float(edges[i]), float(edges[i + 1])],
            "reference_pct": round(float(ref_pct[i]), 6),
            "production_pct": round(float(prod_pct[i]), 6),
            "csi_contribution": round(float(csi_i), 6),
            "shift_direction": shift,
        })

    if csi_total < 0.1:
        status = "stable"
    elif csi_total < 0.25:
        status = "moderate_shift"
    else:
        status = "significant_drift"

    return {
        "csi": round(float(csi_total), 6),
        "per_bin": per_bin,
        "status": status,
    }


# --- Kolmogorov-Smirnov Test ---

def ks_test_features(reference_data: Dict[str, List[float]],
                     production_data: Dict[str, List[float]],
                     alpha: float = 0.05,
                     correction: str = "benjamini-hochberg") -> Dict[str, Any]:
    """Run two-sample KS test on each feature between reference and production.

    Args:
        reference_data: dict mapping feature names to value lists (reference)
        production_data: dict mapping feature names to value lists (production)
        alpha: significance level (default: 0.05)
        correction: multiple testing correction ('bonferroni' or 'benjamini-hochberg')

    Returns:
        dict with per-feature results and summary of significant features
    """
    from scipy import stats
    import numpy as np

    shared_features = set(reference_data.keys()) & set(production_data.keys())
    results = {}
    p_values = []
    feature_names = []

    for feature in sorted(shared_features):
        ref = np.array(reference_data[feature], dtype=float)
        prod = np.array(production_data[feature], dtype=float)

        ref = ref[~np.isnan(ref)]
        prod = prod[~np.isnan(prod)]

        if len(ref) < 2 or len(prod) < 2:
            results[feature] = {
                "d_statistic": float("nan"),
                "p_value": float("nan"),
                "significant": False,
                "error": "Insufficient non-NaN values",
            }
            continue

        d_stat, p_value = stats.ks_2samp(ref, prod)
        results[feature] = {
            "d_statistic": round(float(d_stat), 6),
            "p_value": float(p_value),
            "significant": False,  # updated after correction
        }
        p_values.append(p_value)
        feature_names.append(feature)

    # Multiple testing correction
    if p_values:
        if correction == "bonferroni":
            adjusted = [min(p * len(p_values), 1.0) for p in p_values]
        elif correction == "benjamini-hochberg":
            n = len(p_values)
            sorted_indices = sorted(range(n), key=lambda i: p_values[i])
            adjusted = [0.0] * n
            for rank, idx in enumerate(sorted_indices, 1):
                adjusted[idx] = min(p_values[idx] * n / rank, 1.0)
            # Enforce monotonicity
            for i in range(n - 2, -1, -1):
                idx = sorted_indices[i]
                next_idx = sorted_indices[i + 1]
                adjusted[idx] = min(adjusted[idx], adjusted[next_idx])
        else:
            adjusted = p_values

        for i, feature in enumerate(feature_names):
            results[feature]["p_value_adjusted"] = round(adjusted[i], 6)
            results[feature]["significant"] = adjusted[i] < alpha

    significant_features = [f for f in results if results[f].get("significant", False)]

    return {
        "per_feature": results,
        "significant_features": significant_features,
        "significant_count": len(significant_features),
        "total_features": len(shared_features),
        "alpha": alpha,
        "correction": correction,
    }


# --- Jensen-Shannon Divergence ---

def jensen_shannon_divergence(reference: List[float], production: List[float],
                              n_bins: int = 50) -> Dict[str, float]:
    """Compute Jensen-Shannon divergence between two distributions.

    JSD is a symmetric, bounded [0, 1] measure of distributional difference.
    JSD = 0.5 * KL(P || M) + 0.5 * KL(Q || M), where M = 0.5 * (P + Q).

    Args:
        reference: list of values from reference distribution
        production: list of values from production distribution
        n_bins: number of histogram bins (default: 50)

    Returns:
        dict with 'jsd': float (0 = identical, 1 = maximally different),
        'jsd_sqrt': float (square root of JSD, a proper metric)
    """
    import numpy as np

    ref = np.array(reference, dtype=float)
    prod = np.array(production, dtype=float)

    ref = ref[~np.isnan(ref)]
    prod = prod[~np.isnan(prod)]

    if len(ref) == 0 or len(prod) == 0:
        return {"jsd": float("nan"), "jsd_sqrt": float("nan")}

    # Common bin edges
    all_values = np.concatenate([ref, prod])
    bin_edges = np.linspace(all_values.min() - 1e-6, all_values.max() + 1e-6, n_bins + 1)

    ref_hist, _ = np.histogram(ref, bins=bin_edges)
    prod_hist, _ = np.histogram(prod, bins=bin_edges)

    # Normalize to probability distributions with smoothing
    epsilon = 1e-10
    p = (ref_hist + epsilon) / (ref_hist.sum() + epsilon * len(ref_hist))
    q = (prod_hist + epsilon) / (prod_hist.sum() + epsilon * len(prod_hist))

    # Mixture distribution
    m = 0.5 * (p + q)

    # KL divergences
    kl_pm = np.sum(p * np.log(p / m))
    kl_qm = np.sum(q * np.log(q / m))

    jsd = 0.5 * kl_pm + 0.5 * kl_qm
    jsd = max(0.0, min(float(jsd), 1.0))  # clamp to [0, 1]

    return {
        "jsd": round(jsd, 6),
        "jsd_sqrt": round(math.sqrt(jsd), 6),
    }


# --- Performance Tracking ---

def track_metric_over_time(timestamps: List[str], values: List[float],
                           window_size: int = 7) -> Dict[str, Any]:
    """Analyze a metric time series for trends and change points.

    Computes rolling statistics, linear trend, EWMA, and runs
    CUSUM control chart analysis for change point detection.

    Args:
        timestamps: list of ISO timestamp strings
        values: list of metric values corresponding to timestamps
        window_size: rolling window size in observations (default: 7)

    Returns:
        dict with 'trend', 'rolling_stats', 'change_points', 'current',
        'recommendation'
    """
    import numpy as np

    ts = list(timestamps)
    vals = np.array(values, dtype=float)

    if len(vals) < 3:
        return {
            "trend": "insufficient_data",
            "error": f"Need at least 3 observations, got {len(vals)}",
        }

    # Rolling statistics
    rolling_mean = []
    rolling_std = []
    for i in range(len(vals)):
        start = max(0, i - window_size + 1)
        window = vals[start:i + 1]
        rolling_mean.append(round(float(np.mean(window)), 6))
        rolling_std.append(round(float(np.std(window)), 6))

    # Linear trend
    x = np.arange(len(vals), dtype=float)
    slope, intercept = np.polyfit(x, vals, 1)

    if slope < -0.01:
        trend_direction = "declining"
    elif slope > 0.01:
        trend_direction = "improving"
    else:
        trend_direction = "stable"

    # EWMA
    alpha_ewma = 2.0 / (window_size + 1)
    ewma = [float(vals[0])]
    for i in range(1, len(vals)):
        ewma.append(alpha_ewma * float(vals[i]) + (1 - alpha_ewma) * ewma[-1])
    ewma = [round(v, 6) for v in ewma]

    # CUSUM change point detection
    target = float(np.mean(vals[:max(window_size, len(vals) // 3)]))
    std_ref = float(np.std(vals[:max(window_size, len(vals) // 3)]))
    if std_ref == 0:
        std_ref = 1e-6
    threshold = 4.0 * std_ref
    drift_allowance = 0.5 * std_ref

    cusum_pos = [0.0]
    cusum_neg = [0.0]
    change_points = []

    for i in range(1, len(vals)):
        s_pos = max(0, cusum_pos[-1] + (float(vals[i]) - target) - drift_allowance)
        s_neg = max(0, cusum_neg[-1] - (float(vals[i]) - target) - drift_allowance)
        cusum_pos.append(s_pos)
        cusum_neg.append(s_neg)

        if s_pos > threshold or s_neg > threshold:
            change_points.append({
                "index": i,
                "timestamp": ts[i] if i < len(ts) else None,
                "direction": "decrease" if s_neg > threshold else "increase",
                "magnitude": round(float(vals[i] - target), 6),
            })
            # Reset CUSUM after detection
            cusum_pos[-1] = 0.0
            cusum_neg[-1] = 0.0

    # Current performance
    current_value = float(vals[-1])
    baseline_value = float(np.mean(vals[:window_size]))
    relative_change = (current_value - baseline_value) / max(abs(baseline_value), 1e-6)

    # Recommendation
    if relative_change < -0.10 or len(change_points) >= 2:
        recommendation = "retrain"
        trigger_score = min(100, int(abs(relative_change) * 200) + len(change_points) * 20)
    elif relative_change < -0.05 or len(change_points) >= 1:
        recommendation = "investigate"
        trigger_score = min(100, int(abs(relative_change) * 150) + len(change_points) * 15)
    else:
        recommendation = "stable"
        trigger_score = max(0, int(abs(relative_change) * 100))

    return {
        "trend": {
            "direction": trend_direction,
            "slope": round(float(slope), 6),
            "intercept": round(float(intercept), 6),
        },
        "rolling_stats": {
            "mean": rolling_mean,
            "std": rolling_std,
        },
        "ewma": ewma,
        "change_points": change_points,
        "current": {
            "value": round(current_value, 6),
            "baseline": round(baseline_value, 6),
            "relative_change_pct": round(relative_change * 100, 2),
        },
        "trigger_score": trigger_score,
        "recommendation": recommendation,
    }


# --- Drift Report Generation ---

def generate_drift_report(drift_results: Dict[str, Any],
                          output_path: str = "reports/drift_report.json") -> str:
    """Generate a structured drift report from computed drift results.

    Aggregates PSI, KS, and JSD results across features into a single
    report with severity ranking and recommendations.

    Args:
        drift_results: dict with keys 'psi', 'ks_test', 'jensen_shannon'
            each mapping feature names to their respective metric results
        output_path: path to write the JSON report

    Returns:
        path to the generated report file
    """
    psi_results = drift_results.get("psi", {})
    ks_results = drift_results.get("ks_test", {})
    jsd_results = drift_results.get("jensen_shannon", {})

    all_features = set()
    all_features.update(psi_results.keys())
    all_features.update(ks_results.keys())
    all_features.update(jsd_results.keys())

    feature_summaries = []
    for feature in sorted(all_features):
        psi_val = psi_results.get(feature, {}).get("psi", None)
        psi_status = psi_results.get(feature, {}).get("status", "unknown")
        ks_sig = ks_results.get(feature, {}).get("significant", False)
        ks_d = ks_results.get(feature, {}).get("d_statistic", None)
        jsd_val = jsd_results.get(feature, {}).get("jsd", None)

        # Compute severity score (0-100)
        severity = 0
        if psi_val is not None and not math.isnan(psi_val):
            severity += min(50, psi_val * 200)
        if ks_sig:
            severity += 25
        if jsd_val is not None and not math.isnan(jsd_val):
            severity += min(25, jsd_val * 50)

        feature_summaries.append({
            "feature": feature,
            "psi": psi_val,
            "psi_status": psi_status,
            "ks_d_statistic": ks_d,
            "ks_significant": ks_sig,
            "jsd": jsd_val,
            "severity_score": round(severity, 1),
        })

    # Sort by severity
    feature_summaries.sort(key=lambda x: x["severity_score"], reverse=True)

    # Overall assessment
    drifted_count = sum(1 for f in feature_summaries if f["severity_score"] > 25)
    total_count = len(feature_summaries)

    if drifted_count == 0:
        overall_severity = "low"
    elif drifted_count / max(total_count, 1) < 0.2:
        overall_severity = "moderate"
    elif drifted_count / max(total_count, 1) < 0.5:
        overall_severity = "high"
    else:
        overall_severity = "critical"

    # Recommendations
    recommendations = []
    if overall_severity in ("high", "critical"):
        recommendations.append("Consider retraining the model with recent production data")
    if drifted_count > 0:
        top_drifted = [f["feature"] for f in feature_summaries[:5] if f["severity_score"] > 25]
        recommendations.append(f"Investigate top drifted features: {', '.join(top_drifted)}")
    if overall_severity == "low":
        recommendations.append("No action required -- distributions are stable")

    report = {
        "summary": {
            "total_features": total_count,
            "drifted_features": drifted_count,
            "overall_severity": overall_severity,
        },
        "feature_results": feature_summaries,
        "recommendations": recommendations,
    }

    # Write report
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w") as f:
        json.dump(report, f, indent=2)

    return str(output)
