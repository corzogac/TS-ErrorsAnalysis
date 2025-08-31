# Error Analysis (Hydrology)

Implements common error/skill metrics for measured vs simulated time series,
including RMSE, NSE (NSC), correlation, NRMSE, coefficient of persistence, and naive (persistence) baselines.

## Python
```bash
pip install numpy matplotlib
python examples/demo.py

```
# TS-ErrorsAnalysis (Hydrology)

A tiny, reusable toolkit to evaluate **predicted vs. observed** time series for hydrological applications.  
It computes classic metrics (RMSE, NSE/NSC, correlation, persistence skill, …) and newer ones used in hydrology (KGE, d, d₁), returns them as a single object **`R`** (dot access like `R.RMSE`), and keeps **plotting** in a separate module.

- **Author:** Gerald Augusto Corzo Pérez  
- **Affiliation:** IHE Delft — Hydroinformatics (Department of Coastal & Urban Risk & Resilience)  
- **License:** MIT (see `LICENSE`)  
- **Citation:** Corzo Pérez, G.A. (2009; updated 2025). *Error Analysis*. MATLAB Central File Exchange.

---

## Why this repo?

Researchers and students often need a **one-liner** to compute robust, interpretable skill metrics and quickly visualize what a model is doing. This repo:

1. **Separates concerns** — `errors.py` (analysis) vs `plots.py` (visuals).  
2. **Returns a single object** `R` with dot access (`R.RMSE`, `R.NSC`, …) that you can save to CSV.  
3. **Includes persistence baselines** and hydrology-friendly metrics, not just generic stats.

---

## Install & run (with `uv`)

> You don’t have to activate a venv manually; `uv run` handles it.

```bash
# From the repo root
uv venv
uv pip install numpy matplotlib pytest
uv run python demo.py
