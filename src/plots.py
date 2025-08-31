# ---------------------------------------------------------------------------
# File    : plots.py
# Purpose : Hydrology plots: (1) TS vs Pred, (2) Error with ±1σ band,
#           optional right-side tables (Table 2: metrics list, Table 1: error classes).
# Author  : Gerald Augusto Corzo Pérez
# Affil.  : IHE Delft — Hydroinformatics
# Year    : 2025
# Version : 2.5 (2025-08-31)
# License : MIT
# SPDX-License-Identifier: MIT
# ---------------------------------------------------------------------------
from typing import Optional, Tuple, Sequence, Any
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

def _fmt_float(x: float, p: int = 4) -> str:
    return "—" if x is None or not np.isfinite(x) else f"{x:.{p}g}"

def _fmt_pct(x: float, p: int = 1) -> str:
    return "—" if x is None or not np.isfinite(x) else f"{x:.{p}f}%"

def _render_table(ax: plt.Axes, title: str, header: Sequence[str], rows: Sequence[Sequence[str]],
                  fontsize: int = 9, zebra: bool = True, col_widths: Optional[Sequence[float]] = None) -> None:
    ax.set_title(title, pad=6, fontsize=fontsize + 1)
    ax.axis("off")
    tbl = ax.table(cellText=rows, colLabels=header, colLoc="center", cellLoc="right",
                   loc="center", colWidths=col_widths)
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(fontsize)
    for (r, c), cell in tbl.get_celld().items():
        cell.set_edgecolor("0.75"); cell.set_linewidth(0.4)
        if r == 0:
            cell.set_facecolor("#f0f0f0"); cell.set_text_props(weight="bold")
        elif zebra and (r % 2 == 1):
            cell.set_facecolor("#fafafa")

def _grab(obj: Any, key: str):
    if obj is None:
        return None
    if isinstance(obj, dict):
        return obj.get(key, None)
    return getattr(obj, key, None)

def _metrics_or_fallback(R, T, P):
    """Use metrics in R if present; otherwise compute a minimal set locally."""
    vals = {k: _grab(R, k) for k in
            ["RMSE","NSC","Cor","R2","NRMSE","MAE","PBIAS","sMAPE","KGE2009","KGE2012","d","d1","RMSEN","NRMSEN","PERS"]}
    if any(v is not None and np.isfinite(v) for v in vals.values()):
        return vals  # we have usable metrics

    # Fallback quick compute (ddof=0, matches MATLAB std(x,1))
    T = np.asarray(T, float).ravel(); P = np.asarray(P, float).ravel()
    m = np.isfinite(T) & np.isfinite(P); T, P = T[m], P[m]
    n = T.size
    muT, muP = np.mean(T), np.mean(P)
    sT, sP = np.std(T, ddof=0), np.std(P, ddof=0)
    e = P - T
    sse = np.sum(e**2)
    rmse = np.sqrt(sse / max(1, n))
    mae  = np.mean(np.abs(e))
    nrmse = 100.0 * (rmse / sT) if sT > 0 else np.nan
    den = np.sum((T - muT)**2)
    nsc = 1.0 - (sse/den) if den > 0 else np.nan
    num = np.sum((P - muP)*(T - muT))
    denr= np.sqrt(np.sum((P - muP)**2) * np.sum((T - muT)**2))
    r = num/denr if denr > 0 else np.nan
    r2 = r**2 if np.isfinite(r) else np.nan
    pbias = 100.0 * (np.sum(P - T) / np.sum(T)) if np.abs(np.sum(T)) > 0 else np.nan
    denom = np.abs(P) + np.abs(T); ok = denom > 0
    smape = 100.0 * np.mean(2.0*np.abs(P[ok] - T[ok]) / denom[ok]) if np.any(ok) else np.nan
    alpha = (sP/sT) if sT>0 else np.nan
    beta  = (muP/muT) if muT!=0 else np.nan
    kge2009 = 1.0 - np.sqrt((r-1.0)**2 + (alpha-1.0)**2 + (beta-1.0)**2) if np.isfinite(r) else np.nan
    cvP = (sP/muP) if muP!=0 else np.nan
    cvT = (sT/muT) if muT!=0 else np.nan
    gamma = (cvP/cvT) if np.isfinite(cvP) and np.isfinite(cvT) else np.nan
    kge2012 = 1.0 - np.sqrt((r-1.0)**2 + (gamma-1.0)**2 + (beta-1.0)**2) if np.isfinite(r) else np.nan
    den_d = np.sum((np.abs(P - muT) + np.abs(T - muT))**2)
    d = 1.0 - (sse/den_d) if den_d > 0 else np.nan
    den_d1 = np.sum(np.abs(P - muT) + np.abs(T - muT))
    d1 = 1.0 - (np.sum(np.abs(P - T))/den_d1) if den_d1 > 0 else np.nan
    dT = T[:-1] - T[1:]
    ssen = np.sum(dT**2)
    rmsen = np.sqrt(ssen / max(1, dT.size))
    stdT2 = np.std(T[1:], ddof=0)
    nrmsen = 100.0 * (rmsen/stdT2) if stdT2 > 0 else np.nan
    pers = 1.0 - (sse/ssen) if ssen > 0 else np.nan
    return {"RMSE":rmse,"NSC":nsc,"Cor":r,"R2":r2,"NRMSE":nrmse,"MAE":mae,"PBIAS":pbias,
            "sMAPE":smape,"KGE2009":kge2009,"KGE2012":kge2012,"d":d,"d1":d1,
            "RMSEN":rmsen,"NRMSEN":nrmsen,"PERS":pers}

def plot_ts_error_panel(
    T, P, title: str = "Target vs Predicted", R: Optional[object] = None,
    *, plot_table1: bool = True, plot_table2: bool = False,
    table_fontsize: int = 9, legend_fontsize: int = 8, sigma_k: float = 1.0
) -> Tuple[plt.Figure, Tuple[plt.Axes, plt.Axes, Optional[plt.Axes], Optional[plt.Axes]]]:
    """
    Composite panel with option flags:
      - plot_table1: right 'Error classes' table
      - plot_table2: right 'Metrics summary' table (above table1)
      - legend_fontsize: legend size for both plots
      - sigma_k: band half-width = ±sigma_k * std(error)
    """
    T = np.asarray(T, float).ravel(); P = np.asarray(P, float).ravel()
    m = np.isfinite(T) & np.isfinite(P); T, P = T[m], P[m]
    Er = (getattr(R, "Er", None) if R is not None else None)
    if Er is None or len(Er) != len(T):
        Er = (T - P)
    n = Er.size; x = np.arange(n)

    sigma_e = float(np.std(Er, ddof=0))
    band = sigma_k * sigma_e
    over_mask, under_mask = (P > T), (P < T)
    low_mask = (np.abs(Er) <= band); high_mask = ~low_mask
    pct_over  = 100.0 * np.mean(over_mask) if n else np.nan
    pct_under = 100.0 * np.mean(under_mask) if n else np.nan
    pct_low   = 100.0 * np.mean(low_mask) if n else np.nan
    pct_high  = 100.0 * np.mean(high_mask) if n else np.nan

    any_table = plot_table1 or plot_table2
    if any_table:
        fig = plt.figure(figsize=(12, 7))
        gs = GridSpec(2, 2, figure=fig, width_ratios=[3.0, 1.35], height_ratios=[2.0, 1.4], hspace=0.05, wspace=0.25)
        ax_ts  = fig.add_subplot(gs[0, 0])
        ax_err = fig.add_subplot(gs[1, 0], sharex=ax_ts)
        if plot_table1 and plot_table2:
            ax_tbl2 = fig.add_subplot(gs[0, 1]); ax_tbl1 = fig.add_subplot(gs[1, 1])
        elif plot_table2:
            ax_tbl2 = fig.add_subplot(gs[:, 1]); ax_tbl1 = None
        else:
            ax_tbl2 = None; ax_tbl1 = fig.add_subplot(gs[:, 1])
    else:
        fig = plt.figure(figsize=(10, 6))
        gs = GridSpec(2, 1, figure=fig, height_ratios=[2.0, 1.4], hspace=0.05)
        ax_ts  = fig.add_subplot(gs[0, 0])
        ax_err = fig.add_subplot(gs[1, 0], sharex=ax_ts)
        ax_tbl2 = ax_tbl1 = None

    # top-left
    ax_ts.plot(P, "--", linewidth=1.6, label="Predicted")
    ax_ts.plot(T, "-",  linewidth=1.2, label="Target")
    ax_ts.set_title(title)
    ax_ts.set_ylabel(r"Discharge (m$^3$/s)")
    ax_ts.legend(loc="upper right", fontsize=legend_fontsize)
    ax_ts.grid(True)

    # bottom-left
    ax_err.plot(x, Er, linewidth=1.0, label="Error (T - P)")
    ax_err.axhline(0.0, linewidth=1.0)
    ax_err.fill_between(x, -band, band, alpha=0.2, label=f"±{sigma_k}σ error band")
    hi_pos = Er > +band; hi_neg = Er < -band
    if np.any(hi_pos):
        ax_err.scatter(x[hi_pos], Er[hi_pos], marker="^", s=24, label=f"> +{sigma_k}σ")
    if np.any(hi_neg):
        ax_err.scatter(x[hi_neg], Er[hi_neg], marker="v", s=24, label=f"< -{sigma_k}σ")
    ax_err.set_xlabel("Time")
    ax_err.set_ylabel("Error (T - P)")
    ax_err.grid(True)
    ax_err.legend(loc="upper right", fontsize=legend_fontsize)

    # right tables
    if plot_table2 and ax_tbl2 is not None:
        M = _metrics_or_fallback(R, T, P)
        rows2 = [
            ["RMSE", _fmt_float(M["RMSE"])],
            ["NSE/NSC", _fmt_float(M["NSC"])],
            ["R (corr.)", _fmt_float(M["Cor"])],
            ["R²", _fmt_float(M["R2"])],
            ["NRMSE", _fmt_pct(M["NRMSE"])],
            ["MAE", _fmt_float(M["MAE"])],
            ["PBIAS", _fmt_pct(M["PBIAS"])],
            ["sMAPE", _fmt_pct(M["sMAPE"])],
            ["KGE (2009)", _fmt_float(M["KGE2009"])],
            ["KGE' (2012)", _fmt_float(M["KGE2012"])],
            ["d (IA)", _fmt_float(M["d"])],
            ["d₁ (mod IA)", _fmt_float(M["d1"])],
            ["RMSEN", _fmt_float(M["RMSEN"])],
            ["NRMSEN", _fmt_pct(M["NRMSEN"])],
            ["PERS", _fmt_float(M["PERS"])],
        ]
        _render_table(ax_tbl2, "Metrics summary", ["Metric", "Value"], rows2,
                      fontsize=table_fontsize, col_widths=[0.68, 0.32])

    if plot_table1 and ax_tbl1 is not None:
        rows1 = [
            ["Overestimation (P > T)", _fmt_pct(pct_over)],
            ["Underestimation (P < T)", _fmt_pct(pct_under)],
            ["Low error (|e| ≤ band)", _fmt_pct(pct_low)],
            ["High error (|e| > band)", _fmt_pct(pct_high)],
            [f"band = {sigma_k}σ", _fmt_float(band)],
        ]
        _render_table(ax_tbl1, "Error classes", ["Statistic", "Value"], rows1,
                      fontsize=table_fontsize, col_widths=[0.72, 0.28])

    ax_err.set_xlim(ax_ts.get_xlim())
    return fig, (ax_ts, ax_err, ax_tbl2, ax_tbl1)
