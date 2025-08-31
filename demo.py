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
import numpy as np, matplotlib.pyplot as plt
from src.errors import compute_error_metrics
from src.plots import plot_ts_error_panel


rng = np.random.default_rng(0)


t = np.linspace(0, 6, 200)
T = np.sin(t) + 0.10 * rng.normal(size=t.size)
P = T + 0.15 * rng.normal(size=t.size)

R = compute_error_metrics(P, T)  # pass the metrics object
print(sorted(R.to_dict().keys()))

plot_ts_error_panel(
    T, P, R=R,
    title="Demo — Hydrological Skill Panel",
    plot_table1=True,     # error classes
    plot_table2=True,     # metrics summary
    legend_fontsize=8,    # smaller legends
    sigma_k=1.0           # band = ±1σ (change to 2.0 for ±2σ)
)
plt.show()
