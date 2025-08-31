# ---------------------------------------------------------------------------
# File    : errors.py
# Purpose : Compute error/skill metrics for hydrological time series.
# Author  : Gerald Augusto Corzo Pérez
# Version : 2.3 (2025-08-31)
# License : MIT
# SPDX-License-Identifier: MIT
# ---------------------------------------------------------------------------

from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional
import math
import numpy as np

@dataclass
class ErrorMetrics:
    # core metrics
    RMSE: float; NSC: float; Cor: float; NRMSE: float; MAE: float
    StdT: float; StdP: float; MuT: float; MuP: float
    PERS: float; SSE: float; SSEN: float; RMSEN: float; NRMSEN: float
    MARE: float
    # extras
    R2: float; RSR: float; PBIAS: float; sMAPE: float
    KGE2009: float; KGE2012: float; d: float; d1: float
    # series diagnostics
    Er: np.ndarray; Po: float; Pu: float

    def to_dict(self, include_arrays: bool = False) -> Dict[str, Any]:
        d = asdict(self)
        if include_arrays:
            d["Er"] = self.Er.tolist()
        else:
            d.pop("Er", None)
        return d

    # allow dict-style access too: R['RMSE']
    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

def _safe_div(a: float, b: float) -> float:
    return a / b if b not in (0.0, -0.0) else math.nan

def compute_error_metrics(P, T) -> ErrorMetrics:
    """
    Returns an ErrorMetrics object; use like R.RMSE, R.NSC, etc.
    Conventions:
      - Pairwise drop NaNs/±inf.
      - Std uses ddof=0 to match MATLAB std(x,1).
      - NRMSE = 100 * RMSE / Std(T), NRMSEN analogous with Std(T[1:]).
      - PERS = 1 - SSE / SSEN (persistence baseline).
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

    MuT = float(np.mean(T));  MuP = float(np.mean(P))
    StdT = float(np.std(T, ddof=0));  StdP = float(np.std(P, ddof=0))

    resid = P - T
    SSE  = float(np.sum(resid**2))
    RMSE = float(np.sqrt(SSE / n))
    MAE  = float(np.mean(np.abs(resid)))
    NRMSE = float(100.0 * _safe_div(RMSE, StdT))

    # NSE / NSC
    denom_nsc = float(np.sum((T - MuT) ** 2))
    NSC = float(1.0 - _safe_div(SSE, denom_nsc))

    # Correlation
    num_cor = float(np.sum((P - MuP) * (T - MuT)))
    den_cor = float(np.sqrt(np.sum((P - MuP) ** 2) * np.sum((T - MuT) ** 2)))
    Cor = float(_safe_div(num_cor, den_cor))
    R2 = float(Cor**2) if np.isfinite(Cor) else math.nan

    # MARE (0-safe)
    nz = np.abs(T) > 0
    MARE = float(np.mean(np.abs((T[nz] - P[nz]) / T[nz]))) if np.any(nz) else math.nan

    # Persistence baseline
    T1, T2 = T[:-1], T[1:]
    dT = T1 - T2
    SSEN  = float(np.sum(dT**2))
    RMSEN = float(np.sqrt(_safe_div(SSEN, max(1, T2.size))))
    StdT2 = float(np.std(T2, ddof=0))
    NRMSEN = float(100.0 * _safe_div(RMSEN, StdT2))
    PERS = float(1.0 - _safe_div(SSE, SSEN)) if SSEN > 0 else math.nan

    # Additional hydrology-friendly metrics
    RSR = float(_safe_div(RMSE, StdT))                      # RMSE / Std(T)
    PBIAS = float(100.0 * _safe_div(np.sum(P - T), np.sum(T))) if np.abs(np.sum(T)) > 0 else math.nan
    # sMAPE (skip zero denom pairs)
    denom = np.abs(P) + np.abs(T)
    good = denom > 0
    sMAPE = float(100.0 * np.mean(2.0 * np.abs(P[good] - T[good]) / denom[good])) if np.any(good) else math.nan

    # Kling-Gupta Efficiency (2009)
    r = Cor
    alpha = _safe_div(StdP, StdT)
    beta  = _safe_div(MuP, MuT)
    KGE2009 = float(1.0 - math.sqrt((r - 1.0)**2 + (alpha - 1.0)**2 + (beta - 1.0)**2))

    # KGE' (2012): use variability via coeff. of variation ratio
    cvP = _safe_div(StdP, MuP); cvT = _safe_div(StdT, MuT)
    gamma = _safe_div(cvP, cvT)
    KGE2012 = float(1.0 - math.sqrt((r - 1.0)**2 + (gamma - 1.0)**2 + (beta - 1.0)**2))

    # Index of Agreement (Willmott 1981) and modified d1 (abs version)
    denom_d = float(np.sum((np.abs(P - MuT) + np.abs(T - MuT))**2))
    d = float(1.0 - _safe_div(SSE, denom_d))
    denom_d1 = float(np.sum(np.abs(P - MuT) + np.abs(T - MuT)))
    d1 = float(1.0 - _safe_div(np.sum(np.abs(P - T)), denom_d1))

    Er = T - P
    Po = float(np.sum(Er <= 0) / Er.size)
    Pu = float(np.sum(Er >  0) / Er.size)

    return ErrorMetrics(
        RMSE=RMSE, NSC=NSC, Cor=Cor, NRMSE=NRMSE, MAE=MAE,
        StdT=StdT, StdP=StdP, MuT=MuT, MuP=MuP,
        PERS=PERS, SSE=SSE, SSEN=SSEN, RMSEN=RMSEN, NRMSEN=NRMSEN,
        MARE=MARE, R2=R2, RSR=RSR, PBIAS=PBIAS, sMAPE=sMAPE,
        KGE2009=KGE2009, KGE2012=KGE2012, d=d, d1=d1,
        Er=Er, Po=Po, Pu=Pu
    )

# Backward-compatible alias if you were calling error1(...)
def error1(P, T, *_, **__):  # returns the same ErrorMetrics object
    return compute_error_metrics(P, T)
