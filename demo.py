# ---------------------------------------------------------------------------
# File    : demo.py
# Purpose : Minimal example showing how to compute metrics and make plots.
# Author  : Gerald Augusto Corzo Pérez
# Affil.  : IHE Delft — Hydroinformatics
# Year    : 2025
# Version : 2.3 (2025-08-31)
# License : MIT
# SPDX-License-Identifier: MIT
# ---------------------------------------------------------------------------

from pathlib import Path
import numpy as np

# Imports
from src.Error1 import compute_error_metrics
from src.plots import plot_time_series, plot_error_series

# Data (replace with your series)
rng = np.random.default_rng(0)
t = np.linspace(0, 6, 200)
T = np.sin(t) + 0.10 * rng.normal(size=t.size)
P = T + 0.15 * rng.normal(size=t.size)

# 1) analysis
E = compute_error_metrics(P, T)
for k in ["RMSE","NSC","Cor","NRMSE","MAE","PERS","RMSEN","NRMSEN","MARE","Po","Pu"]:
    print(f"{k:6s}: {E[k]:.6f}")

# 2) plots (separate)
plot_time_series(T, P, title="Demo — Time Series")
plot_error_series(E["Er"], title=f"Demo — Error (NRMSE={E['NRMSE']:.2f}%)")
