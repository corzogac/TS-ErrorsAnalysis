# ---------------------------------------------------------------------------
# File    : errors.py
# Purpose : Compute error/skill metrics for hydrological time series.
# Author  : Gerald Augusto Corzo Pérez
# Affil.  : IHE Delft — Hydroinformatics (Department of Coastal & Urban Risk & Resilience)
# Year    : 2025
# Version : 2.3 (2025-08-31)
# License : MIT
# SPDX-License-Identifier: MIT
# Copyright:
#   © 2025 Gerald Augusto Corzo Pérez. All rights reserved.
# Citation:
#   Corzo Pérez, G.A. (2009; updated 2025). Error Analysis. MATLAB Central File Exchange.
# Notes  :
#   Returns an object R so you can access metrics like R.RMSE, R.NSC, etc.
# ---------------------------------------------------------------------------


from typing import Dict, Any
import numpy as np

def compute_error_metrics(P, T) -> Dict[str, Any]:
    """
    Returns a dict with:
      RMSE, NSC, Cor, NRMSE (% of Std(T)), MAE, StdT, StdP, MuT, MuP,
      PERS, SSE, SSEN, RMSEN, NRMSEN (% of Std(T[1:])), MARE, Er, Po, Pu
    """
    P = np.asarray(P, dtype=float).ravel()
    T = np.asarray(T, dtype=float).ravel()
    if P.size != T.size:
        raise ValueError("P and T must have the same length.")

    mask = np.isfinite(P) & np.isfinite(T)
    P, T = P[mask], T[mask]
    n = P.size
    if n < 2:
        raise ValueError("Need at least 2 paired values after removing NaNs/Infs.")

    # Means & population std (ddof=0) to mirror MATLAB std(x,1)
    MuT = float(np.mean(T));  MuP = float(np.mean(P))
    StdT = float(np.std(T, ddof=0));  StdP = float(np.std(P, ddof=0))

    resid = P - T
    SSE  = float(np.sum(resid**2))
    RMSE = float(np.sqrt(SSE / n))
    MAE  = float(np.mean(np.abs(resid)))

    # NRMSE as % of Std(T)
    NRMSE = float(100.0 * RMSE / StdT) if StdT > 0 else float("inf")

    # Nash–Sutcliffe
    denom = float(np.sum((T - MuT) ** 2))
    NSC = float(1.0 - SSE / denom) if denom > 0 else np.nan

    # Pearson correlation (manual to mirror MATLAB)
    num = float(np.sum((P - MuP) * (T - MuT)))
    den = float(np.sqrt(np.sum((P - MuP) ** 2) * np.sum((T - MuT) ** 2)))
    Cor = num / den if den > 0 else np.nan

    # MARE (exclude zeros in T)
    nz = np.abs(T) > 0
    MARE = float(np.mean(np.abs((T[nz] - P[nz]) / T[nz]))) if np.any(nz) else np.nan

    # Persistence baseline: T_hat[i] = T[i-1]
    T1, T2 = T[:-1], T[1:]
    dT = T1 - T2
    SSEN = float(np.sum(dT**2))
    RMSEN = float(np.sqrt(SSEN / max(1, T2.size)))
    StdT2 = float(np.std(T2, ddof=0))
    NRMSEN = float(100.0 * RMSEN / StdT2) if StdT2 > 0 else float("inf")

    PERS = float(1.0 - SSE / SSEN) if SSEN > 0 else np.nan

    Er = T - P
    Po = float(np.sum(Er <= 0) / Er.size)
    Pu = float(np.sum(Er >  0) / Er.size)

    return {
        "RMSE": RMSE, "NSC": NSC, "Cor": Cor, "NRMSE": NRMSE, "MAE": MAE,
        "StdT": StdT, "StdP": StdP, "MuT": MuT, "MuP": MuP,
        "PERS": PERS, "SSE": SSE, "SSEN": SSEN, "RMSEN": RMSEN, "NRMSEN": NRMSEN,
        "MARE": MARE, "Er": Er, "Po": Po, "Pu": Pu,
    }

# Backward-compatible name if you were calling error1(...)
def error1(P, T, *_, **__):
    return compute_error_metrics(P, T)
