# ---------------------------------------------------------------------------
# File    : error1.py
# Purpose : Compute standard error/skill metrics for hydrological series and plot.
# Author  : Gerald Augusto Corzo Pérez
# Affil.  : IHE Delft — Hydroinformatics
# Version : 2.1 (2025-08-31)
# License : MIT
# SPDX-License-Identifier: MIT
#
# Metrics returned (dict):
#   RMSE, NSC, Cor, NRMSE (%), MAE, StdT, StdP, MuT, MuP,
#   PERS, SSE, SSEN, RMSEN, NRMSEN (%), MARE, Er (array), Po, Pu, fig (matplotlib Figure or None)
#
# Conventions:
#   - Pairwise drop NaNs (like MATLAB nansum/nanmean usage in your script).
#   - NRMSE and NRMSEN are percentages of population std (ddof=0) to match `std(x,1)` in MATLAB.
#   - Coefficient of persistence: PERS = 1 - SSE / SSEN, where SSEN is the naive (persistence) SSE.
# ---------------------------------------------------------------------------

from __future__ import annotations
from typing import Dict, Any, Optional
import numpy as np

def error1(P, T, comment: str = "Target and Predicted", plot: bool = True) -> Dict[str, Any]:
    import matplotlib.pyplot as plt  # local import so the module works without plotting deps if needed

    P = np.asarray(P, dtype=float).ravel()
    T = np.asarray(T, dtype=float).ravel()
    if P.shape != T.shape:
        raise ValueError("P and T must have the same length.")
    mask = np.isfinite(P) & np.isfinite(T)
    P, T = P[mask], T[mask]

    n = P.size
    if n < 2:
        raise ValueError("Need at least 2 paired values after removing NaNs/Infs.")

    # Means & population std (ddof=0) to mirror MATLAB std(x,1)
    MuT = float(np.mean(T))
    MuP = float(np.mean(P))
    StdT = float(np.std(T, ddof=0))
    StdP = float(np.std(P, ddof=0))

    # Errors
    resid = P - T
    SSE  = float(np.sum(resid**2))
    RMSE = float(np.sqrt(SSE / n))
    MAE  = float(np.mean(np.abs(resid)))

    # NRMSE as % of Std(T)
    NRMSE = float(100.0 * RMSE / StdT) if StdT > 0 else np.inf

    # Nash–Sutcliffe (NSC/NSE)
    denom_nsc = float(np.sum((T - MuT) ** 2))
    NSC = float(1.0 - SSE / denom_nsc) if denom_nsc > 0 else np.nan

    # Pearson correlation (explicit formula to mirror MATLAB)
    num_cor = float(np.sum((P - MuP) * (T - MuT)))
    den_cor = float(np.sqrt(np.sum((P - MuP) ** 2) * np.sum((T - MuT) ** 2)))
    Cor = num_cor / den_cor if den_cor > 0 else np.nan

    # MARE: exclude zeros in T
    nz = np.abs(T) > 0
    MARE = float(np.mean(np.abs((T[nz] - P[nz]) / T[nz]))) if np.any(nz) else np.nan

    # Persistence baseline: T_hat[i] = T[i-1]
    T1 = T[:-1]
    T2 = T[1:]
    dT = T1 - T2
    SSEN = float(np.sum(dT**2))
    RMSEN = float(np.sqrt(SSEN / max(1, T2.size)))          # (n-1) terms
    stdT2 = float(np.std(T2, ddof=0))                       # match MATLAB std(T2,1)
    NRMSEN = float(100.0 * RMSEN / stdT2) if stdT2 > 0 else np.inf

    PERS = float(1.0 - SSE / SSEN) if SSEN > 0 else np.nan

    Er = T - P
    Po = float(np.sum(Er <= 0) / Er.size)  # proportion <= 0
    Pu = float(np.sum(Er >  0) / Er.size)  # proportion  > 0

    fig: Optional["plt.Figure"] = None
    if plot:
        fig = plt.figure(figsize=(8, 6), layout="constrained")
        fig.canvas.manager.set_window_title(comment) if hasattr(fig.canvas.manager, "set_window_title") else None
        import matplotlib.pyplot as plt_
        ax1 = fig.add_subplot(2, 1, 1)
        ax1.plot(P, "r--", linewidth=1.8, label="Predicted")
        ax1.plot(T, "b-",  linewidth=1.2, label="Target")
        ax1.legend(loc="lower right")
        ax1.set_title(f"Time series of target and predicted\n(RMSE = {RMSE:.4g})  {comment}")
        ax1.set_xlabel("Time"); ax1.set_ylabel(r"Discharge (m$^3$/s)")
        ax1.grid(True)

        ax2 = fig.add_subplot(2, 1, 2)
        ax2.stem(np.arange(Er.size), Er, use_line_collection=True)
        ax2.set_title(f"Error between target and predicted (NRMSE = {NRMSE:.2f}%)")
        ax2.set_xlabel("Time"); ax2.set_ylabel("Error (T - P)")
        ax2.grid(True)

    return {
        "RMSE": RMSE, "NSC": NSC, "Cor": Cor, "NRMSE": NRMSE, "MAE": MAE,
        "StdT": StdT, "StdP": StdP, "MuT": MuT, "MuP": MuP,
        "PERS": PERS, "SSE": SSE, "SSEN": SSEN, "RMSEN": RMSEN, "NRMSEN": NRMSEN,
        "MARE": MARE, "Er": Er, "Po": Po, "Pu": Pu, "fig": fig
    }
