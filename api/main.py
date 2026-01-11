# ---------------------------------------------------------------------------
# File    : api/main.py
# Purpose : FastAPI backend for TS-ErrorsAnalysis web service
# Author  : Generated for TS-ErrorsAnalysis
# Version : 1.0
# License : MIT
# SPDX-License-Identifier: MIT
# ---------------------------------------------------------------------------
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import numpy as np
import sys
from pathlib import Path
import uuid

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.errors import compute_error_metrics
from .database import get_db
from . import stats as stats_module
from . import timeseries as ts_module

app = FastAPI(
    title="TS-ErrorsAnalysis API",
    description="Hydrological time series error analysis and visualization API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class TimeSeriesInput(BaseModel):
    """Input model for time series analysis"""
    predicted: List[float] = Field(..., description="Predicted values", min_length=2)
    target: List[float] = Field(..., description="Target/observed values", min_length=2)
    user_id: Optional[str] = Field(None, description="Optional user ID for tracking")
    analysis_name: Optional[str] = Field(None, description="Optional name for this analysis")
    notes: Optional[str] = Field(None, description="Optional notes")

    class Config:
        json_schema_extra = {
            "example": {
                "predicted": [1.0, 2.5, 3.2, 4.1, 5.0],
                "target": [1.2, 2.3, 3.5, 3.9, 4.8],
                "user_id": "user123",
                "analysis_name": "River discharge comparison"
            }
        }

class ErrorMetricsResponse(BaseModel):
    """Response model for error metrics"""
    # Basic metrics
    RMSE: float
    NSC: float
    Cor: float
    NRMSE: float
    MAE: float

    # Statistical properties
    StdT: float
    StdP: float
    MuT: float
    MuP: float

    # Persistence metrics
    PERS: float
    SSE: float
    SSEN: float
    RMSEN: float
    NRMSEN: float
    MARE: float

    # Advanced metrics
    R2: float
    RSR: float
    PBIAS: float
    sMAPE: float
    KGE2009: float
    KGE2012: float
    d: float
    d1: float

    # Error analysis
    Er: List[float]
    Po: float
    Pu: float

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    service: str

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "TS-ErrorsAnalysis API"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for container orchestration"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "TS-ErrorsAnalysis API"
    }

@app.post("/api/v1/analyze", response_model=ErrorMetricsResponse)
async def analyze_time_series(
    data: TimeSeriesInput,
    db: Session = Depends(get_db),
    x_session_id: Optional[str] = Header(None)
):
    """
    Analyze time series: compute error metrics for predicted vs target values

    Returns 28+ metrics including:
    - RMSE, NSE/NSC, Correlation
    - KGE (2009, 2012)
    - Index of Agreement (d, d1)
    - Persistence metrics
    - Error series and proportions

    Automatically tracks usage statistics.
    """
    try:
        # Convert to numpy arrays
        P = np.array(data.predicted)
        T = np.array(data.target)

        # Validate lengths match
        if len(P) != len(T):
            raise HTTPException(
                status_code=400,
                detail=f"Length mismatch: predicted({len(P)}) vs target({len(T)})"
            )

        # Compute metrics
        result = compute_error_metrics(P, T)

        # Convert to response format
        response = {
            "RMSE": result.RMSE,
            "NSC": result.NSC,
            "Cor": result.Cor,
            "NRMSE": result.NRMSE,
            "MAE": result.MAE,
            "StdT": result.StdT,
            "StdP": result.StdP,
            "MuT": result.MuT,
            "MuP": result.MuP,
            "PERS": result.PERS,
            "SSE": result.SSE,
            "SSEN": result.SSEN,
            "RMSEN": result.RMSEN,
            "NRMSEN": result.NRMSEN,
            "MARE": result.MARE,
            "R2": result.R2,
            "RSR": result.RSR,
            "PBIAS": result.PBIAS,
            "sMAPE": result.sMAPE,
            "KGE2009": result.KGE2009,
            "KGE2012": result.KGE2012,
            "d": result.d,
            "d1": result.d1,
            "Er": result.Er.tolist(),
            "Po": result.Po,
            "Pu": result.Pu
        }

        # Log analysis to database
        session_id = x_session_id or str(uuid.uuid4())
        stats_module.get_or_create_session(db, session_id, data.user_id)
        stats_module.log_analysis(
            db=db,
            metrics=response,
            n_points=len(P),
            session_id=session_id,
            user_id=data.user_id,
            analysis_name=data.analysis_name,
            notes=data.notes
        )

        return response

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.get("/api/v1/metrics/info")
async def metrics_info():
    """
    Get information about all available metrics
    """
    return {
        "metrics": {
            "basic_errors": {
                "RMSE": "Root Mean Squared Error",
                "MAE": "Mean Absolute Error",
                "SSE": "Sum of Squared Errors",
                "NRMSE": "Normalized RMSE (% of std(T))"
            },
            "model_skill": {
                "NSC": "Nash-Sutcliffe Efficiency (NSE)",
                "Cor": "Pearson correlation coefficient",
                "R2": "Coefficient of determination",
                "RSR": "RMSE-to-StdDev ratio"
            },
            "bias_metrics": {
                "PBIAS": "Percent Bias",
                "sMAPE": "Symmetric Mean Absolute Percentage Error",
                "MARE": "Mean Absolute Relative Error"
            },
            "hydrology_specific": {
                "KGE2009": "Kling-Gupta Efficiency (2009)",
                "KGE2012": "Modified KGE (2012, CV ratio)",
                "d": "Index of Agreement (Willmott 1981)",
                "d1": "Modified Index of Agreement (absolute)"
            },
            "persistence": {
                "PERS": "Coefficient of persistence",
                "RMSEN": "RMSE of naive lag-1 forecast",
                "NRMSEN": "Normalized RMSEN",
                "SSEN": "SSE of persistence baseline"
            },
            "statistics": {
                "MuT": "Mean of target values",
                "MuP": "Mean of predicted values",
                "StdT": "Std dev of target (ddof=0)",
                "StdP": "Std dev of predicted (ddof=0)"
            },
            "error_analysis": {
                "Er": "Error series (T - P)",
                "Po": "Proportion overestimations (P > T)",
                "Pu": "Proportion underestimations (P < T)"
            }
        },
        "conventions": {
            "error_sign": "Er = T - P (positive = underestimate)",
            "std_method": "Population std (ddof=0) to match MATLAB",
            "nan_handling": "Pairwise deletion, requires ≥2 valid pairs"
        }
    }

@app.get("/api/v1/stats/user/{user_id}")
async def get_user_statistics(user_id: str, db: Session = Depends(get_db)):
    """Get statistics for a specific user"""
    return stats_module.get_user_stats(db, user_id)

@app.get("/api/v1/stats/system")
async def get_system_statistics(db: Session = Depends(get_db)):
    """Get overall system statistics"""
    return stats_module.get_system_stats(db)

@app.get("/api/v1/history")
async def get_analysis_history(
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get analysis history

    Query parameters:
    - user_id: Filter by user ID
    - session_id: Filter by session ID
    - limit: Max number of records (default 50)
    """
    return stats_module.get_analysis_history(db, user_id, session_id, limit)

# ============================================================================
# TIME SERIES PROCESSING ENDPOINTS
# ============================================================================

class TimeSeriesData(BaseModel):
    """Time series data input"""
    values: List[float] = Field(..., description="Time series values")
    indices: Optional[List[float]] = Field(None, description="Optional time indices")

class InterpolateRequest(BaseModel):
    """Spline interpolation request"""
    values: List[float]
    indices: Optional[List[float]] = None
    kind: str = Field('cubic', description="Interpolation kind: linear, quadratic, cubic")
    num_points: Optional[int] = Field(None, description="Number of output points")

class SmoothRequest(BaseModel):
    """Data smoothing request"""
    values: List[float]
    method: str = Field('moving_average', description="Smoothing method")
    window_size: int = Field(5, description="Window size for smoothing")
    polyorder: Optional[int] = Field(2, description="Polynomial order for Savitzky-Golay")
    alpha: Optional[float] = Field(0.3, description="Alpha for exponential smoothing")

class FillMissingRequest(BaseModel):
    """Fill missing data request"""
    values: List[float]
    method: str = Field('linear', description="Fill method: linear, forward, backward, mean, median")
    limit: Optional[int] = Field(None, description="Max consecutive NaNs to fill")

class DecomposeRequest(BaseModel):
    """Trend decomposition request"""
    values: List[float]
    period: int = Field(12, description="Seasonal period")
    model: str = Field('additive', description="Model type: additive or multiplicative")

class OutlierRequest(BaseModel):
    """Outlier detection request"""
    values: List[float]
    method: str = Field('zscore', description="Detection method: zscore or iqr")
    threshold: float = Field(3.0, description="Threshold for detection")

class ResampleRequest(BaseModel):
    """Resampling request"""
    values: List[float]
    indices: Optional[List[float]] = None
    target_points: int = Field(..., description="Target number of points")
    method: str = Field('linear', description="Interpolation method")

@app.post("/api/v1/timeseries/interpolate")
async def interpolate_timeseries(request: InterpolateRequest):
    """
    Perform spline interpolation on time series data

    Returns interpolated x and y values
    """
    try:
        values = np.array(request.values)
        indices = np.array(request.indices) if request.indices else np.arange(len(values))

        x_new, y_new = ts_module.spline_interpolate(
            indices, values,
            kind=request.kind,
            num_points=request.num_points
        )

        return {
            "indices": x_new.tolist(),
            "values": y_new.tolist(),
            "method": request.kind,
            "original_points": len(values),
            "interpolated_points": len(y_new)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/timeseries/smooth")
async def smooth_timeseries(request: SmoothRequest):
    """
    Smooth time series data using various methods

    Methods: moving_average, savitzky_golay, exponential
    """
    try:
        values = np.array(request.values)

        kwargs = {}
        if request.method == 'savitzky_golay':
            kwargs['polyorder'] = request.polyorder
        elif request.method == 'exponential':
            kwargs['alpha'] = request.alpha

        smoothed = ts_module.smooth_data(
            values,
            method=request.method,
            window_size=request.window_size,
            **kwargs
        )

        return {
            "original": values.tolist(),
            "smoothed": smoothed.tolist(),
            "method": request.method,
            "window_size": request.window_size
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/timeseries/fill-missing")
async def fill_missing_data(request: FillMissingRequest):
    """
    Fill missing (NaN) values in time series

    Methods: linear, forward, backward, mean, median
    """
    try:
        values = np.array(request.values, dtype=float)

        filled, mask = ts_module.fill_missing_data(
            values,
            method=request.method,
            limit=request.limit
        )

        return {
            "original": values.tolist(),
            "filled": filled.tolist(),
            "filled_indices": np.where(mask)[0].tolist(),
            "num_filled": int(np.sum(mask)),
            "method": request.method
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/timeseries/decompose")
async def decompose_trend(request: DecomposeRequest):
    """
    Decompose time series into trend, seasonal, and residual components
    """
    try:
        values = np.array(request.values)

        components = ts_module.decompose_trend(
            values,
            period=request.period,
            model=request.model
        )

        return {
            "original": components['original'].tolist(),
            "trend": components['trend'].tolist(),
            "seasonal": components['seasonal'].tolist(),
            "residual": components['residual'].tolist(),
            "period": request.period,
            "model": request.model
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/timeseries/detect-outliers")
async def detect_outliers(request: OutlierRequest):
    """
    Detect outliers in time series data

    Methods: zscore, iqr
    """
    try:
        values = np.array(request.values)

        outliers = ts_module.detect_outliers(
            values,
            method=request.method,
            threshold=request.threshold
        )

        return {
            "values": values.tolist(),
            "is_outlier": outliers.tolist(),
            "outlier_indices": np.where(outliers)[0].tolist(),
            "num_outliers": int(np.sum(outliers)),
            "method": request.method,
            "threshold": request.threshold
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/v1/timeseries/resample")
async def resample_timeseries(request: ResampleRequest):
    """
    Resample time series to a different number of points
    """
    try:
        values = np.array(request.values)
        indices = np.array(request.indices) if request.indices else np.arange(len(values))

        x_new, y_new = ts_module.resample_timeseries(
            indices, values,
            target_points=request.target_points,
            method=request.method
        )

        return {
            "original_points": len(values),
            "resampled_points": len(y_new),
            "indices": x_new.tolist(),
            "values": y_new.tolist(),
            "method": request.method
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
