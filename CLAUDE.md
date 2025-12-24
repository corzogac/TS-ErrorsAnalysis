# CLAUDE.md - AI Assistant Guide for TS-ErrorsAnalysis

This document provides comprehensive guidance for AI assistants working with the TS-ErrorsAnalysis codebase.

---

## Project Overview

**TS-ErrorsAnalysis** is a hydrological time series error analysis toolkit that computes skill metrics for comparing predicted vs. observed values. It provides both **Python** and **MATLAB** implementations.

- **Author:** Gerald Augusto Corzo Pérez
- **Affiliation:** IHE Delft — Hydroinformatics (Department of Coastal & Urban Risk & Resilience)
- **License:** MIT
- **Version:** 2.3 (Python), 2.1 (MATLAB)
- **Last Updated:** August 31, 2025

### Purpose
Researchers and students need a one-liner to compute robust, interpretable skill metrics and quickly visualize model performance. This toolkit:
1. Separates concerns (analysis vs visualization)
2. Returns a single object with dot-access to all metrics
3. Includes persistence baselines and hydrology-friendly metrics

---

## Repository Structure

```
TS-ErrorsAnalysis/
├── .gitignore           # Python, MATLAB, and OS-specific ignores
├── LICENSE              # MIT License
├── README.md            # User-facing documentation
├── requirements.txt     # Python dependencies (numpy, matplotlib, pytest)
├── demo.py              # Minimal working example
├── src/                 # Python source code
│   ├── __init__.py      # Package marker (empty)
│   ├── errors.py        # Core metrics computation
│   └── plots.py         # Visualization functions
└── matlab/              # MATLAB implementation
    └── Error1.m         # MATLAB error analysis function
```

### Key Files

#### Python Implementation
- **src/errors.py** (137 lines)
  - Core metrics computation module
  - Main function: `compute_error_metrics(P, T) -> ErrorMetrics`
  - Backward-compatible alias: `error1(P, T)`
  - Returns dataclass with 28 metrics + error series

- **src/plots.py** (205 lines)
  - Visualization module
  - Main function: `plot_ts_error_panel(T, P, R=None, ...)`
  - Creates multi-panel plots with optional metrics tables

- **demo.py** (35 lines)
  - Minimal working example
  - Shows complete workflow: generate data → compute metrics → plot

#### MATLAB Implementation
- **matlab/Error1.m** (129 lines)
  - Standalone MATLAB function
  - Returns struct with error metrics
  - Automatically generates visualization

---

## Code Architecture & Design Patterns

### Separation of Concerns
The codebase strictly separates **computation** from **visualization**:
- `src/errors.py`: Pure computational logic, no plotting
- `src/plots.py`: Pure visualization logic, can compute fallback metrics if needed

### Data Flow Pattern
```
Raw Data (P, T)
    ↓
compute_error_metrics(P, T)
    ↓
ErrorMetrics object (R)
    ↓
plot_ts_error_panel(T, P, R)
    ↓
Matplotlib Figure
```

### Key Design Decisions

1. **Dataclass for Results**: `ErrorMetrics` uses Python dataclass for clean dot-access
   - Access via `R.RMSE`, `R.NSC`, etc.
   - Convertible to dict via `R.to_dict()`
   - Supports dict-style access: `R['RMSE']`

2. **NaN Handling**: Pairwise deletion of NaN/Inf values
   - Filters at the start of computation
   - Requires at least 2 valid paired values

3. **Statistical Conventions**:
   - Uses `ddof=0` (population std) to match MATLAB `std(x, 1)`
   - NRMSE normalized by std(T), not range (configurable)
   - Persistence baseline uses lag-1 naive forecast

4. **Error Safety**: Division-by-zero returns `math.nan`, not exceptions

---

## Core Metrics Computed

The toolkit computes **28 metrics** organized into categories:

### Basic Error Metrics
- **RMSE**: Root Mean Squared Error
- **MAE**: Mean Absolute Error
- **SSE**: Sum of Squared Errors
- **NRMSE**: Normalized RMSE (% of std(T))

### Model Skill Metrics
- **NSC/NSE**: Nash-Sutcliffe Efficiency
- **Cor**: Pearson correlation coefficient
- **R2**: Coefficient of determination
- **RSR**: RMSE-to-StdDev ratio

### Bias Metrics
- **PBIAS**: Percent Bias
- **sMAPE**: Symmetric Mean Absolute Percentage Error
- **MARE**: Mean Absolute Relative Error

### Hydrology-Specific Metrics
- **KGE2009**: Kling-Gupta Efficiency (2009 version)
- **KGE2012**: Modified KGE (2012, uses CV ratio)
- **d**: Index of Agreement (Willmott 1981)
- **d1**: Modified Index of Agreement (absolute version)

### Persistence Baseline
- **PERS**: Coefficient of persistence (1 - SSE/SSEN)
- **RMSEN**: RMSE of naive (lag-1) forecast
- **NRMSEN**: Normalized RMSEN
- **SSEN**: SSE of persistence baseline

### Statistical Properties
- **MuT, MuP**: Means of target and predicted
- **StdT, StdP**: Standard deviations (ddof=0)

### Error Analysis
- **Er**: Error series (T - P)
- **Po**: Proportion of overestimations (P > T)
- **Pu**: Proportion of underestimations (P < T)

---

## Development Conventions

### Python Code Style

1. **Type Hints**: Use for function signatures
   ```python
   def compute_error_metrics(P, T) -> ErrorMetrics:
   ```

2. **Imports**: Standard library → third-party → local
   ```python
   from __future__ import annotations
   from dataclasses import dataclass
   import math
   import numpy as np
   ```

3. **Docstrings**: Concise, describe conventions
   ```python
   """
   Returns an ErrorMetrics object; use like R.RMSE, R.NSC, etc.
   Conventions:
     - Pairwise drop NaNs/±inf.
     - Std uses ddof=0 to match MATLAB std(x,1).
   """
   ```

4. **Variable Naming**:
   - `P`: Predicted values
   - `T`: Target/observed values
   - `R`: Results object (ErrorMetrics)
   - `Er`: Error series (T - P, not P - T)
   - Single-letter uppercase for main arrays

5. **Error Handling**: Graceful degradation to NaN, not exceptions
   ```python
   def _safe_div(a: float, b: float) -> float:
       return a / b if b not in (0.0, -0.0) else math.nan
   ```

### MATLAB Code Style

1. **Function Header**: Extensive commenting with metadata
2. **Struct Output**: Fields accessible via `Error.RMSE`, etc.
3. **NaN Handling**: Use `'omitnan'` flag in aggregations
4. **Plotting**: Integrated into function (unlike Python)

---

## Common Workflows

### Adding a New Metric

1. **In src/errors.py**:
   ```python
   # Step 1: Add field to ErrorMetrics dataclass
   @dataclass
   class ErrorMetrics:
       # ... existing fields ...
       NewMetric: float

   # Step 2: Compute in compute_error_metrics()
   def compute_error_metrics(P, T) -> ErrorMetrics:
       # ... existing computations ...
       new_metric = compute_new_metric(P, T)

       return ErrorMetrics(
           # ... existing params ...
           NewMetric=new_metric
       )
   ```

2. **In src/plots.py** (optional):
   ```python
   # Add to _metrics_or_fallback() if used in tables
   vals = {k: _grab(R, k) for k in
           ["RMSE", ..., "NewMetric"]}

   # Add to table rendering if desired
   rows2 = [
       # ... existing rows ...
       ["New Metric", _fmt_float(M["NewMetric"])],
   ]
   ```

3. **Update MATLAB** (matlab/Error1.m):
   ```matlab
   % Compute
   NewMetric = compute_new_metric(P, T);

   % Pack into struct
   Error.NewMetric = NewMetric;
   ```

### Running the Code

**Python (with uv)**:
```bash
uv venv
uv pip install numpy matplotlib pytest
uv run python demo.py
```

**Python (traditional)**:
```bash
pip install numpy matplotlib
python demo.py
```

**MATLAB**:
```matlab
P = randn(100,1); T = randn(100,1);
Error = Error1(P, T, 'Test Run');
```

### Testing

- No formal test suite yet (pytest installed but no tests/)
- Validation via demo.py output
- When adding tests:
  - Create `tests/` directory
  - Test against known analytical results
  - Test edge cases (all NaN, single value, etc.)

---

## Key Implementation Details

### NaN/Inf Handling
Both Python and MATLAB versions:
1. Accept any length vectors
2. Filter to finite values pairwise
3. Require ≥2 valid pairs
4. Raise error if insufficient data

```python
mask = np.isfinite(P) & np.isfinite(T)
P, T = P[mask], T[mask]
if P.size < 2:
    raise ValueError("Need at least 2 paired values after removing NaNs/Infs.")
```

### Standard Deviation Convention
Uses **population std** (ddof=0) to match MATLAB:
```python
StdT = float(np.std(T, ddof=0))  # Python
StdT = std(T, 1, 'omitnan');     % MATLAB
```

### Error Sign Convention
Error is **Target - Predicted** (T - P):
- Positive error → model underestimates
- Negative error → model overestimates
- `Po`: proportion where P > T (overestimation)
- `Pu`: proportion where P < T (underestimation)

### Plotting Flexibility
The `plot_ts_error_panel()` function is highly configurable:
- `plot_table1`: Error classification table
- `plot_table2`: Metrics summary table
- `sigma_k`: Error band width (default 1σ, can use 2σ)
- `legend_fontsize`, `table_fontsize`: Typography control

---

## Dependencies

### Python
```
numpy==2.3.2          # Numerical computations
matplotlib==3.10.6    # Plotting
pytest==8.4.1         # Testing framework (for future tests)
```

Full dependency tree in `requirements.txt` includes transitive deps (colorama, pillow, etc.)

### MATLAB
- Base MATLAB (tested on recent versions)
- No toolboxes required
- Uses built-in functions: `mean`, `std`, `corr`, `plot`, `tiledlayout`

---

## Git Workflow

### Branch Strategy
- Development occurs on feature branches: `claude/feature-name-{sessionId}`
- Branch naming: Must start with `claude/` and end with session ID
- Push with: `git push -u origin <branch-name>`

### Commit Conventions
- Clear, descriptive messages
- Focus on "why" rather than "what"
- Recent commits show style:
  - "Adjust subplot spacing and improve tick label visibility in error panel plots"
  - "Add .gitignore, remove obsolete files, and implement Error1 metrics..."

### Ignored Files (.gitignore)
- Python: `__pycache__/`, `.venv/`, `*.pyc`, `.ipynb_checkpoints/`
- MATLAB: `*.asv`, `*.autosave`, `*.mex*`, `slprj/`
- OS: `.DS_Store`, `.vscode/`
- Project: `PRD*` (design docs)

---

## Common Pitfalls & Best Practices

### For AI Assistants

1. **Always Match MATLAB Behavior**: When modifying Python metrics, ensure MATLAB parity
   - Use `ddof=0` for std
   - Match error sign convention (T - P)
   - Test against MATLAB output

2. **Preserve Backward Compatibility**:
   - Keep `error1()` alias even though `compute_error_metrics()` is preferred
   - Don't change ErrorMetrics field names without migration path

3. **Respect Separation of Concerns**:
   - Never add plotting to `errors.py`
   - Never add metrics computation to `plots.py` (except fallback)

4. **Handle Edge Cases Gracefully**:
   - Division by zero → NaN
   - Empty data → clear error message
   - Mismatched lengths → raise ValueError early

5. **Maintain Documentation Consistency**:
   - Update README.md if changing public API
   - Keep version numbers in sync across files
   - Preserve SPDX license identifiers

6. **Testing Before Committing**:
   - Run `demo.py` successfully
   - Check plot renders correctly
   - Verify no NumPy/matplotlib deprecation warnings

7. **Code Style**:
   - Follow existing formatting (4-space indent, etc.)
   - Preserve ASCII art/separators in headers
   - Keep line length reasonable (~100 chars)

---

## Future Enhancements (Potential)

Based on codebase analysis, future additions might include:

1. **Testing Infrastructure**:
   - Formal pytest suite in `tests/`
   - Regression tests against known datasets
   - Numerical precision tests (Python vs MATLAB)

2. **Additional Metrics**:
   - VE (Volumetric Efficiency)
   - PBIAS variants (log-space, high-flow, low-flow)
   - Time-lag correlation

3. **I/O Utilities**:
   - CSV export of metrics: `R.to_csv('metrics.csv')`
   - JSON export for web apps
   - Pandas DataFrame integration

4. **Enhanced Plotting**:
   - Interactive plots (plotly)
   - Additional diagnostic plots (Q-Q, residual autocorrelation)
   - Customizable color schemes

5. **Performance Optimization**:
   - Numba JIT for large time series
   - Vectorized variants for multiple predictions

---

## Quick Reference

### Most Common Operations

**Compute metrics**:
```python
from src.errors import compute_error_metrics
R = compute_error_metrics(predicted, target)
print(f"RMSE: {R.RMSE}, NSE: {R.NSC}, r: {R.Cor}")
```

**Plot results**:
```python
from src.plots import plot_ts_error_panel
import matplotlib.pyplot as plt

fig, axes = plot_ts_error_panel(
    target, predicted, R=R,
    plot_table1=True,
    plot_table2=True
)
plt.show()
```

**Export metrics**:
```python
metrics_dict = R.to_dict()
# Or with error series:
metrics_full = R.to_dict(include_arrays=True)
```

**Access individual metric**:
```python
rmse = R.RMSE           # Dot access
nse = R['NSC']          # Dict-style access
```

---

## Contact & Attribution

When citing this work:
> Corzo Pérez, G.A. (2009; updated 2025). *Error Analysis*. MATLAB Central File Exchange.

For questions or contributions:
- Author: Gerald Augusto Corzo Pérez
- Institution: IHE Delft — Hydroinformatics
- License: MIT (see LICENSE file)

---

## Version History (in files)

- **2.5** (plots.py, 2025-08-31): Enhanced plotting with tables
- **2.3** (errors.py, 2025-08-31): Added KGE, d, d1 metrics
- **2.3** (demo.py, 2025-08-31): Updated example
- **2.1** (Error1.m, 2025-08-31): Cleaned NaN handling

---

*This CLAUDE.md file is intended for AI assistants to understand the codebase structure, conventions, and workflows. Keep it updated as the project evolves.*
