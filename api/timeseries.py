# ---------------------------------------------------------------------------
# File    : api/timeseries.py
# Purpose : Advanced time series processing functions
# License : MIT
# ---------------------------------------------------------------------------
import numpy as np
from scipy import interpolate, signal
from typing import Tuple, Optional, Dict, Any
import warnings

def spline_interpolate(
    x: np.ndarray,
    y: np.ndarray,
    kind: str = 'cubic',
    num_points: Optional[int] = None,
    fill_value: str = 'extrapolate'
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Perform spline interpolation on time series data

    Args:
        x: x-values (time indices)
        y: y-values (observations)
        kind: 'linear', 'quadratic', 'cubic'
        num_points: Number of interpolated points (default: 2x original)
        fill_value: How to handle extrapolation

    Returns:
        x_new, y_new: Interpolated arrays
    """
    # Remove NaN values
    mask = np.isfinite(y)
    x_clean, y_clean = x[mask], y[mask]

    if len(x_clean) < 2:
        raise ValueError("Need at least 2 valid points for interpolation")

    # Create interpolator
    if kind in ['linear', 'quadratic', 'cubic']:
        f = interpolate.interp1d(x_clean, y_clean, kind=kind, fill_value=fill_value)
    else:
        raise ValueError(f"Unknown interpolation kind: {kind}")

    # Generate new x values
    if num_points is None:
        num_points = len(x) * 2

    x_new = np.linspace(x_clean[0], x_clean[-1], num_points)
    y_new = f(x_new)

    return x_new, y_new

def smooth_data(
    y: np.ndarray,
    method: str = 'moving_average',
    window_size: int = 5,
    **kwargs
) -> np.ndarray:
    """
    Smooth time series data using various methods

    Args:
        y: Input data
        method: 'moving_average', 'savitzky_golay', 'exponential'
        window_size: Window size for smoothing
        **kwargs: Additional method-specific parameters

    Returns:
        Smoothed data array
    """
    if method == 'moving_average':
        return moving_average(y, window_size)

    elif method == 'savitzky_golay':
        polyorder = kwargs.get('polyorder', 2)
        if window_size % 2 == 0:
            window_size += 1  # Must be odd
        return signal.savgol_filter(y, window_size, polyorder)

    elif method == 'exponential':
        alpha = kwargs.get('alpha', 0.3)
        return exponential_smoothing(y, alpha)

    else:
        raise ValueError(f"Unknown smoothing method: {method}")

def moving_average(y: np.ndarray, window_size: int) -> np.ndarray:
    """Simple moving average"""
    if window_size < 1:
        raise ValueError("Window size must be >= 1")

    cumsum = np.cumsum(np.insert(y, 0, 0))
    result = (cumsum[window_size:] - cumsum[:-window_size]) / window_size

    # Pad to maintain original length
    pad_size = len(y) - len(result)
    if pad_size > 0:
        result = np.concatenate([np.full(pad_size, result[0]), result])

    return result

def exponential_smoothing(y: np.ndarray, alpha: float = 0.3) -> np.ndarray:
    """Exponential smoothing (simple exponential moving average)"""
    if not 0 < alpha <= 1:
        raise ValueError("Alpha must be in (0, 1]")

    result = np.zeros_like(y)
    result[0] = y[0]

    for i in range(1, len(y)):
        result[i] = alpha * y[i] + (1 - alpha) * result[i - 1]

    return result

def fill_missing_data(
    y: np.ndarray,
    method: str = 'linear',
    limit: Optional[int] = None
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Fill missing (NaN) values in time series

    Args:
        y: Input data with potential NaN values
        method: 'linear', 'forward', 'backward', 'mean', 'median'
        limit: Maximum number of consecutive NaNs to fill

    Returns:
        filled_data, mask (True where data was filled)
    """
    y_filled = y.copy()
    mask = np.isnan(y)

    if not np.any(mask):
        return y_filled, np.zeros_like(y, dtype=bool)

    if method == 'linear':
        # Linear interpolation
        indices = np.arange(len(y))
        valid = ~mask
        if np.sum(valid) >= 2:
            y_filled[mask] = np.interp(indices[mask], indices[valid], y[valid])

    elif method == 'forward':
        # Forward fill
        y_filled = forward_fill(y, limit)

    elif method == 'backward':
        # Backward fill
        y_filled = backward_fill(y, limit)

    elif method == 'mean':
        # Fill with mean
        mean_val = np.nanmean(y)
        y_filled[mask] = mean_val

    elif method == 'median':
        # Fill with median
        median_val = np.nanmedian(y)
        y_filled[mask] = median_val

    else:
        raise ValueError(f"Unknown fill method: {method}")

    return y_filled, mask

def forward_fill(y: np.ndarray, limit: Optional[int] = None) -> np.ndarray:
    """Forward fill NaN values"""
    result = y.copy()
    mask = np.isnan(result)

    last_valid = None
    consecutive_nans = 0

    for i in range(len(result)):
        if not mask[i]:
            last_valid = result[i]
            consecutive_nans = 0
        elif last_valid is not None:
            consecutive_nans += 1
            if limit is None or consecutive_nans <= limit:
                result[i] = last_valid

    return result

def backward_fill(y: np.ndarray, limit: Optional[int] = None) -> np.ndarray:
    """Backward fill NaN values"""
    result = y.copy()
    mask = np.isnan(result)

    next_valid = None
    consecutive_nans = 0

    for i in range(len(result) - 1, -1, -1):
        if not mask[i]:
            next_valid = result[i]
            consecutive_nans = 0
        elif next_valid is not None:
            consecutive_nans += 1
            if limit is None or consecutive_nans <= limit:
                result[i] = next_valid

    return result

def decompose_trend(
    y: np.ndarray,
    period: int = 12,
    model: str = 'additive'
) -> Dict[str, np.ndarray]:
    """
    Decompose time series into trend, seasonal, and residual components

    Args:
        y: Time series data
        period: Seasonal period
        model: 'additive' or 'multiplicative'

    Returns:
        Dictionary with 'trend', 'seasonal', 'residual' components
    """
    from scipy.ndimage import uniform_filter1d

    n = len(y)

    # Compute trend using moving average
    if period % 2 == 0:
        # Even period: use centered moving average
        trend = uniform_filter1d(y, period, mode='nearest')
    else:
        trend = uniform_filter1d(y, period, mode='nearest')

    # Detrend
    if model == 'additive':
        detrended = y - trend
    elif model == 'multiplicative':
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            detrended = y / (trend + 1e-10)
    else:
        raise ValueError(f"Unknown model: {model}")

    # Compute seasonal component
    seasonal = np.zeros(n)
    for i in range(period):
        indices = np.arange(i, n, period)
        seasonal[indices] = np.nanmean(detrended[indices])

    # Compute residual
    if model == 'additive':
        residual = y - trend - seasonal
    else:
        residual = y / ((trend + 1e-10) * (seasonal + 1e-10))

    return {
        'trend': trend,
        'seasonal': seasonal,
        'residual': residual,
        'original': y
    }

def detect_outliers(
    y: np.ndarray,
    method: str = 'zscore',
    threshold: float = 3.0
) -> np.ndarray:
    """
    Detect outliers in time series

    Args:
        y: Input data
        method: 'zscore' or 'iqr'
        threshold: Z-score threshold (or IQR multiplier)

    Returns:
        Boolean array (True for outliers)
    """
    if method == 'zscore':
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            z_scores = np.abs((y - np.nanmean(y)) / (np.nanstd(y) + 1e-10))
        return z_scores > threshold

    elif method == 'iqr':
        q1 = np.nanpercentile(y, 25)
        q3 = np.nanpercentile(y, 75)
        iqr = q3 - q1
        lower_bound = q1 - threshold * iqr
        upper_bound = q3 + threshold * iqr
        return (y < lower_bound) | (y > upper_bound)

    else:
        raise ValueError(f"Unknown method: {method}")

def resample_timeseries(
    x: np.ndarray,
    y: np.ndarray,
    target_points: int,
    method: str = 'linear'
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Resample time series to a different number of points

    Args:
        x: Original x values
        y: Original y values
        target_points: Desired number of points
        method: Interpolation method

    Returns:
        x_new, y_new: Resampled arrays
    """
    # Remove NaN
    mask = np.isfinite(y)
    x_clean, y_clean = x[mask], y[mask]

    if len(x_clean) < 2:
        raise ValueError("Need at least 2 valid points")

    # Create new x array
    x_new = np.linspace(x_clean[0], x_clean[-1], target_points)

    # Interpolate
    if method == 'linear':
        y_new = np.interp(x_new, x_clean, y_clean)
    else:
        f = interpolate.interp1d(x_clean, y_clean, kind=method, fill_value='extrapolate')
        y_new = f(x_new)

    return x_new, y_new
