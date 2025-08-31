# ---------------------------------------------------------------------------
# File    : plots.py
# Purpose : Plot hydrological time series and error series (separate from analysis).
# Author  : Gerald Augusto Corzo Pérez
# Affil.  : IHE Delft — Hydroinformatics
# Year    : 2025
# Version : 2.3 (2025-08-31)
# License : MIT
# SPDX-License-Identifier: MIT
# ---------------------------------------------------------------------------


from typing import Optional, Tuple
import numpy as np
import matplotlib.pyplot as plt

def plot_time_series(T, P, title: str = "Measured vs Predicted") -> Tuple[plt.Figure, Tuple[plt.Axes, plt.Axes]]:
    T = np.asarray(T).ravel()
    P = np.asarray(P).ravel()

    fig = plt.figure(figsize=(8, 5), layout="constrained")
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(P, "r--", linewidth=1.8, label="Predicted")
    ax.plot(T, "b-",  linewidth=1.2, label="Target")
    ax.legend(loc="best")
    ax.set_title(title)
    ax.set_xlabel("Time"); ax.set_ylabel(r"Discharge (m$^3$/s)")
    ax.grid(True)
    return fig, (ax,)

def plot_error_series(Er, title: str = "Error (T - P)") -> Tuple[plt.Figure, Tuple[plt.Axes,]]:
    Er = np.asarray(Er).ravel()
    x = np.arange(Er.size)

    fig = plt.figure(figsize=(8, 4), layout="constrained")
    ax = fig.add_subplot(1, 1, 1)
    # Note: no 'use_line_collection' here (it breaks on some Matplotlib versions)
    markerline, stemlines, baseline = ax.stem(x, Er)
    ax.set_title(title)
    ax.set_xlabel("Time"); ax.set_ylabel("Error (T - P)")
    ax.grid(True)
    return fig, (ax,)
