# ---------------------------------------------------------------------------
# File    : api/batch.py
# Purpose : Batch processing and export utilities for TS-ErrorsAnalysis
# Version : 1.0
# License : MIT
# SPDX-License-Identifier: MIT
# ---------------------------------------------------------------------------
"""
Batch processing and export functionality for time series analysis.

Features:
- Batch analyze multiple time series at once
- Export results to CSV, JSON formats
- Compare multiple model runs side-by-side
"""

from typing import List, Dict, Any, Optional
import numpy as np
import csv
import json
from io import StringIO
from datetime import datetime
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.errors import compute_error_metrics


def batch_analyze(time_series_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Analyze multiple time series in batch.

    Args:
        time_series_list: List of dicts with 'predicted', 'target', 'name' keys

    Returns:
        List of analysis results with metrics for each series
    """
    results = []

    for idx, ts_data in enumerate(time_series_list):
        try:
            P = np.array(ts_data['predicted'])
            T = np.array(ts_data['target'])
            name = ts_data.get('name', f'Series_{idx+1}')

            # Validate lengths
            if len(P) != len(T):
                results.append({
                    'name': name,
                    'success': False,
                    'error': f'Length mismatch: predicted({len(P)}) vs target({len(T)})'
                })
                continue

            # Compute metrics
            metrics = compute_error_metrics(P, T)

            # Convert to dict (exclude error series for batch results)
            result_dict = {
                'name': name,
                'success': True,
                'n_points': len(P),
                'metrics': {
                    'RMSE': metrics.RMSE,
                    'NSC': metrics.NSC,
                    'Cor': metrics.Cor,
                    'NRMSE': metrics.NRMSE,
                    'MAE': metrics.MAE,
                    'R2': metrics.R2,
                    'RSR': metrics.RSR,
                    'PBIAS': metrics.PBIAS,
                    'sMAPE': metrics.sMAPE,
                    'KGE2009': metrics.KGE2009,
                    'KGE2012': metrics.KGE2012,
                    'd': metrics.d,
                    'd1': metrics.d1,
                    'PERS': metrics.PERS,
                    'MARE': metrics.MARE,
                    'MuT': metrics.MuT,
                    'MuP': metrics.MuP,
                    'StdT': metrics.StdT,
                    'StdP': metrics.StdP,
                    'Po': metrics.Po,
                    'Pu': metrics.Pu
                }
            }

            results.append(result_dict)

        except Exception as e:
            results.append({
                'name': ts_data.get('name', f'Series_{idx+1}'),
                'success': False,
                'error': str(e)
            })

    return results


def export_to_csv(results: List[Dict[str, Any]], include_header: bool = True) -> str:
    """
    Export analysis results to CSV format.

    Args:
        results: List of analysis result dicts
        include_header: Whether to include header row

    Returns:
        CSV string
    """
    output = StringIO()

    # Collect all unique metric names
    metric_names = set()
    for result in results:
        if result.get('success') and 'metrics' in result:
            metric_names.update(result['metrics'].keys())

    metric_names = sorted(metric_names)

    # Define CSV columns
    fieldnames = ['name', 'success', 'n_points'] + metric_names + ['error']

    writer = csv.DictWriter(output, fieldnames=fieldnames)

    if include_header:
        writer.writeheader()

    # Write rows
    for result in results:
        row = {
            'name': result.get('name', ''),
            'success': result.get('success', False),
            'n_points': result.get('n_points', ''),
            'error': result.get('error', '')
        }

        # Add metrics if available
        if result.get('success') and 'metrics' in result:
            for metric_name in metric_names:
                row[metric_name] = result['metrics'].get(metric_name, '')

        writer.writerow(row)

    return output.getvalue()


def export_to_json(results: List[Dict[str, Any]], pretty: bool = True) -> str:
    """
    Export analysis results to JSON format.

    Args:
        results: List of analysis result dicts
        pretty: Whether to pretty-print JSON

    Returns:
        JSON string
    """
    # Add metadata
    output = {
        'export_timestamp': datetime.utcnow().isoformat() + 'Z',
        'num_analyses': len(results),
        'num_successful': sum(1 for r in results if r.get('success')),
        'num_failed': sum(1 for r in results if not r.get('success')),
        'results': results
    }

    if pretty:
        return json.dumps(output, indent=2)
    else:
        return json.dumps(output)


def compare_runs(results: List[Dict[str, Any]], metrics_to_compare: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Compare multiple model runs side-by-side.

    Args:
        results: List of analysis results
        metrics_to_compare: List of metric names to compare (None = all)

    Returns:
        Comparison summary with statistics
    """
    if not results:
        return {'error': 'No results to compare'}

    # Filter successful results
    successful_results = [r for r in results if r.get('success')]

    if not successful_results:
        return {'error': 'No successful analyses to compare'}

    # Determine metrics to compare
    if metrics_to_compare is None:
        # Use all available metrics from first result
        metrics_to_compare = list(successful_results[0]['metrics'].keys())

    # Build comparison table
    comparison = {
        'num_series': len(successful_results),
        'series_names': [r['name'] for r in successful_results],
        'metrics_compared': metrics_to_compare,
        'comparison_table': {},
        'rankings': {}
    }

    # For each metric, collect values and compute stats
    for metric_name in metrics_to_compare:
        values = []
        series_values = {}

        for result in successful_results:
            if metric_name in result['metrics']:
                val = result['metrics'][metric_name]
                values.append(val)
                series_values[result['name']] = val

        if not values:
            continue

        # Compute statistics
        values_array = np.array(values)
        comparison['comparison_table'][metric_name] = {
            'values': series_values,
            'min': float(np.min(values_array)),
            'max': float(np.max(values_array)),
            'mean': float(np.mean(values_array)),
            'std': float(np.std(values_array, ddof=0)),
            'median': float(np.median(values_array))
        }

        # Ranking: higher is better for NSC, Cor, KGE, d, d1, PERS
        # Lower is better for RMSE, MAE, NRMSE, etc.
        higher_is_better = metric_name in ['NSC', 'Cor', 'R2', 'KGE2009', 'KGE2012', 'd', 'd1', 'PERS']

        # Sort and rank
        sorted_items = sorted(series_values.items(), key=lambda x: x[1], reverse=higher_is_better)
        ranking = [{'rank': i+1, 'name': name, 'value': val} for i, (name, val) in enumerate(sorted_items)]

        comparison['rankings'][metric_name] = {
            'higher_is_better': higher_is_better,
            'ranking': ranking,
            'best': ranking[0]['name'],
            'worst': ranking[-1]['name']
        }

    return comparison


def generate_summary_report(results: List[Dict[str, Any]]) -> str:
    """
    Generate a human-readable summary report.

    Args:
        results: List of analysis results

    Returns:
        Formatted text report
    """
    report = []
    report.append("=" * 80)
    report.append("TIME SERIES ANALYSIS BATCH REPORT")
    report.append("=" * 80)
    report.append(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    report.append(f"Total analyses: {len(results)}")

    successful = [r for r in results if r.get('success')]
    failed = [r for r in results if not r.get('success')]

    report.append(f"Successful: {len(successful)}")
    report.append(f"Failed: {len(failed)}")
    report.append("")

    # Success details
    if successful:
        report.append("-" * 80)
        report.append("SUCCESSFUL ANALYSES")
        report.append("-" * 80)

        for result in successful:
            report.append(f"\n{result['name']}:")
            report.append(f"  Data points: {result['n_points']}")

            # Key metrics
            m = result['metrics']
            report.append(f"  RMSE:     {m['RMSE']:.4f}")
            report.append(f"  NSE/NSC:  {m['NSC']:.4f}")
            report.append(f"  R:        {m['Cor']:.4f}")
            report.append(f"  KGE2012:  {m['KGE2012']:.4f}")
            report.append(f"  PBIAS:    {m['PBIAS']:.2f}%")

    # Failure details
    if failed:
        report.append("\n" + "-" * 80)
        report.append("FAILED ANALYSES")
        report.append("-" * 80)

        for result in failed:
            report.append(f"\n{result['name']}:")
            report.append(f"  Error: {result.get('error', 'Unknown error')}")

    report.append("\n" + "=" * 80)

    return "\n".join(report)
