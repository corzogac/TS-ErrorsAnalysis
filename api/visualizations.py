# ---------------------------------------------------------------------------
# File    : api/visualizations.py
# Purpose : Advanced visualizations for TS-ErrorsAnalysis (Stage 7)
# Version : 1.0
# License : MIT
# SPDX-License-Identifier: MIT
# ---------------------------------------------------------------------------
"""
Advanced visualization capabilities for time series analysis.

Features:
- 3D surface plots
- Residual analysis plots
- Autocorrelation plots (ACF/PACF)
- Q-Q plots for error distribution
- Interactive Plotly charts
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from scipy import stats
from scipy.stats import probplot
import sys
from pathlib import Path

# For statsmodels (ACF/PACF)
try:
    from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
    from statsmodels.tsa.stattools import acf, pacf
    HAS_STATSMODELS = True
except ImportError:
    HAS_STATSMODELS = False

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.errors import compute_error_metrics


def create_3d_surface_plot(
    predicted: np.ndarray,
    target: np.ndarray,
    grid_size: int = 30
) -> Dict[str, Any]:
    """
    Create a 3D surface plot showing predicted vs target values with error surface.

    Args:
        predicted: Predicted values
        target: Target/observed values
        grid_size: Grid resolution for surface

    Returns:
        Plotly figure as JSON
    """
    # Create grid
    p_min, p_max = predicted.min(), predicted.max()
    t_min, t_max = target.min(), target.max()

    p_range = np.linspace(p_min, p_max, grid_size)
    t_range = np.linspace(t_min, t_max, grid_size)
    P_grid, T_grid = np.meshgrid(p_range, t_range)

    # Compute error surface (RMSE-like metric)
    # For each point on grid, compute distance from actual data
    Z = np.sqrt((P_grid - T_grid) ** 2)

    # Create 3D surface
    fig = go.Figure()

    # Add error surface
    fig.add_trace(go.Surface(
        x=P_grid,
        y=T_grid,
        z=Z,
        colorscale='Viridis',
        name='Error Surface',
        opacity=0.7,
        colorbar=dict(title='Error Magnitude')
    ))

    # Add actual data points
    fig.add_trace(go.Scatter3d(
        x=predicted,
        y=target,
        z=np.abs(target - predicted),
        mode='markers',
        marker=dict(
            size=4,
            color=np.abs(target - predicted),
            colorscale='Reds',
            showscale=False
        ),
        name='Actual Points'
    ))

    # Add perfect prediction line (where P = T, Error = 0)
    diag_line = np.linspace(min(p_min, t_min), max(p_max, t_max), 50)
    fig.add_trace(go.Scatter3d(
        x=diag_line,
        y=diag_line,
        z=np.zeros_like(diag_line),
        mode='lines',
        line=dict(color='red', width=4),
        name='Perfect Prediction'
    ))

    fig.update_layout(
        title='3D Error Surface Analysis',
        scene=dict(
            xaxis_title='Predicted',
            yaxis_title='Target',
            zaxis_title='Error',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.2)
            )
        ),
        width=800,
        height=600
    )

    return fig.to_dict()


def create_residual_analysis_plot(
    predicted: np.ndarray,
    target: np.ndarray
) -> Dict[str, Any]:
    """
    Create comprehensive residual analysis plots.

    Returns a multi-panel figure with:
    1. Residuals vs Predicted
    2. Residuals histogram
    3. Residuals vs Time/Index
    4. Scale-Location plot

    Args:
        predicted: Predicted values
        target: Target/observed values

    Returns:
        Plotly figure as JSON
    """
    from plotly.subplots import make_subplots

    residuals = target - predicted
    standardized_residuals = residuals / np.std(residuals, ddof=1)

    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Residuals vs Predicted',
            'Residuals Histogram',
            'Residuals vs Index',
            'Scale-Location Plot'
        )
    )

    # 1. Residuals vs Predicted
    fig.add_trace(
        go.Scatter(
            x=predicted,
            y=residuals,
            mode='markers',
            marker=dict(color='blue', size=6, opacity=0.6),
            name='Residuals'
        ),
        row=1, col=1
    )
    fig.add_hline(y=0, line_dash="dash", line_color="red", row=1, col=1)

    # 2. Histogram of residuals
    fig.add_trace(
        go.Histogram(
            x=residuals,
            nbinsx=30,
            marker=dict(color='skyblue', line=dict(color='black', width=1)),
            name='Distribution',
            showlegend=False
        ),
        row=1, col=2
    )

    # Add normal distribution overlay
    mu, sigma = residuals.mean(), residuals.std()
    x_norm = np.linspace(residuals.min(), residuals.max(), 100)
    y_norm = stats.norm.pdf(x_norm, mu, sigma) * len(residuals) * (residuals.max() - residuals.min()) / 30

    fig.add_trace(
        go.Scatter(
            x=x_norm,
            y=y_norm,
            mode='lines',
            line=dict(color='red', width=2),
            name='Normal',
            showlegend=False
        ),
        row=1, col=2
    )

    # 3. Residuals vs Index (Time)
    indices = np.arange(len(residuals))
    fig.add_trace(
        go.Scatter(
            x=indices,
            y=residuals,
            mode='markers',
            marker=dict(color='green', size=6, opacity=0.6),
            name='Time Series',
            showlegend=False
        ),
        row=2, col=1
    )
    fig.add_hline(y=0, line_dash="dash", line_color="red", row=2, col=1)

    # 4. Scale-Location (sqrt of standardized residuals vs predicted)
    sqrt_std_residuals = np.sqrt(np.abs(standardized_residuals))
    fig.add_trace(
        go.Scatter(
            x=predicted,
            y=sqrt_std_residuals,
            mode='markers',
            marker=dict(color='purple', size=6, opacity=0.6),
            name='Scale-Location',
            showlegend=False
        ),
        row=2, col=2
    )

    # Add trend line to Scale-Location
    z = np.polyfit(predicted, sqrt_std_residuals, 2)
    p = np.poly1d(z)
    sorted_pred = np.sort(predicted)
    fig.add_trace(
        go.Scatter(
            x=sorted_pred,
            y=p(sorted_pred),
            mode='lines',
            line=dict(color='red', width=2, dash='dash'),
            name='Trend',
            showlegend=False
        ),
        row=2, col=2
    )

    # Update axes labels
    fig.update_xaxes(title_text="Predicted", row=1, col=1)
    fig.update_yaxes(title_text="Residuals", row=1, col=1)

    fig.update_xaxes(title_text="Residuals", row=1, col=2)
    fig.update_yaxes(title_text="Frequency", row=1, col=2)

    fig.update_xaxes(title_text="Index", row=2, col=1)
    fig.update_yaxes(title_text="Residuals", row=2, col=1)

    fig.update_xaxes(title_text="Predicted", row=2, col=2)
    fig.update_yaxes(title_text="√|Std. Residuals|", row=2, col=2)

    fig.update_layout(
        title_text="Residual Analysis",
        height=800,
        width=1000,
        showlegend=False
    )

    return fig.to_dict()


def create_qq_plot(
    predicted: np.ndarray,
    target: np.ndarray
) -> Dict[str, Any]:
    """
    Create Q-Q plot to assess normality of residuals.

    Args:
        predicted: Predicted values
        target: Target/observed values

    Returns:
        Plotly figure as JSON
    """
    residuals = target - predicted

    # Compute theoretical quantiles and sample quantiles
    (theoretical_quantiles, sample_quantiles), (slope, intercept, r) = probplot(residuals, dist="norm")

    fig = go.Figure()

    # Add Q-Q points
    fig.add_trace(go.Scatter(
        x=theoretical_quantiles,
        y=sample_quantiles,
        mode='markers',
        marker=dict(color='blue', size=8, opacity=0.6),
        name='Q-Q Points'
    ))

    # Add reference line (perfect normality)
    line_x = np.array([theoretical_quantiles.min(), theoretical_quantiles.max()])
    line_y = slope * line_x + intercept

    fig.add_trace(go.Scatter(
        x=line_x,
        y=line_y,
        mode='lines',
        line=dict(color='red', width=2, dash='dash'),
        name=f'Reference Line (R={r:.4f})'
    ))

    fig.update_layout(
        title='Q-Q Plot (Normality Assessment)',
        xaxis_title='Theoretical Quantiles',
        yaxis_title='Sample Quantiles',
        width=600,
        height=600,
        showlegend=True
    )

    return fig.to_dict()


def create_autocorrelation_plot(
    predicted: np.ndarray,
    target: np.ndarray,
    max_lags: int = 40
) -> Dict[str, Any]:
    """
    Create autocorrelation and partial autocorrelation plots for residuals.

    Args:
        predicted: Predicted values
        target: Target/observed values
        max_lags: Maximum number of lags to compute

    Returns:
        Plotly figure with ACF and PACF subplots as JSON
    """
    if not HAS_STATSMODELS:
        raise ImportError("statsmodels is required for autocorrelation plots")

    from plotly.subplots import make_subplots

    residuals = target - predicted
    max_lags = min(max_lags, len(residuals) // 2 - 1)

    # Compute ACF and PACF
    acf_values = acf(residuals, nlags=max_lags, fft=True)
    pacf_values = pacf(residuals, nlags=max_lags)

    # Confidence intervals (95%)
    confidence_interval = 1.96 / np.sqrt(len(residuals))

    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Autocorrelation Function (ACF)', 'Partial Autocorrelation Function (PACF)')
    )

    # ACF plot
    lags = np.arange(len(acf_values))
    fig.add_trace(
        go.Bar(
            x=lags,
            y=acf_values,
            marker=dict(color='steelblue'),
            name='ACF',
            showlegend=False
        ),
        row=1, col=1
    )

    # Add confidence interval lines for ACF
    fig.add_hline(y=confidence_interval, line_dash="dash", line_color="red", row=1, col=1)
    fig.add_hline(y=-confidence_interval, line_dash="dash", line_color="red", row=1, col=1)
    fig.add_hline(y=0, line_color="black", row=1, col=1)

    # PACF plot
    pacf_lags = np.arange(len(pacf_values))
    fig.add_trace(
        go.Bar(
            x=pacf_lags,
            y=pacf_values,
            marker=dict(color='darkorange'),
            name='PACF',
            showlegend=False
        ),
        row=2, col=1
    )

    # Add confidence interval lines for PACF
    fig.add_hline(y=confidence_interval, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=-confidence_interval, line_dash="dash", line_color="red", row=2, col=1)
    fig.add_hline(y=0, line_color="black", row=2, col=1)

    # Update axes
    fig.update_xaxes(title_text="Lag", row=1, col=1)
    fig.update_yaxes(title_text="ACF", row=1, col=1)
    fig.update_xaxes(title_text="Lag", row=2, col=1)
    fig.update_yaxes(title_text="PACF", row=2, col=1)

    fig.update_layout(
        title_text="Residual Autocorrelation Analysis",
        height=800,
        width=900
    )

    return fig.to_dict()


def create_error_distribution_plot(
    predicted: np.ndarray,
    target: np.ndarray
) -> Dict[str, Any]:
    """
    Create comprehensive error distribution visualization.

    Args:
        predicted: Predicted values
        target: Target/observed values

    Returns:
        Plotly figure as JSON
    """
    residuals = target - predicted

    fig = go.Figure()

    # Add histogram
    fig.add_trace(go.Histogram(
        x=residuals,
        nbinsx=50,
        name='Error Distribution',
        marker=dict(
            color='lightblue',
            line=dict(color='black', width=1)
        ),
        opacity=0.7,
        histnorm='probability density'
    ))

    # Fit normal distribution
    mu, sigma = residuals.mean(), residuals.std()
    x_range = np.linspace(residuals.min(), residuals.max(), 100)
    y_norm = stats.norm.pdf(x_range, mu, sigma)

    fig.add_trace(go.Scatter(
        x=x_range,
        y=y_norm,
        mode='lines',
        name=f'Normal(μ={mu:.3f}, σ={sigma:.3f})',
        line=dict(color='red', width=3)
    ))

    # Add statistics
    skewness = stats.skew(residuals)
    kurtosis = stats.kurtosis(residuals)

    fig.add_annotation(
        xref="paper", yref="paper",
        x=0.98, y=0.98,
        text=f"<b>Statistics:</b><br>Mean: {mu:.4f}<br>Std: {sigma:.4f}<br>Skewness: {skewness:.4f}<br>Kurtosis: {kurtosis:.4f}",
        showarrow=False,
        align="right",
        bgcolor="white",
        bordercolor="black",
        borderwidth=1,
        font=dict(size=10)
    )

    fig.update_layout(
        title='Error Distribution Analysis',
        xaxis_title='Error (Target - Predicted)',
        yaxis_title='Probability Density',
        width=800,
        height=500,
        showlegend=True
    )

    return fig.to_dict()
