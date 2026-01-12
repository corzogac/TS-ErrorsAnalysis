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
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.errors import compute_error_metrics
from .database import get_db
from . import stats as stats_module
from . import timeseries as ts_module
from . import batch as batch_module
from . import visualizations as viz_module
from . import cache as cache_module
from . import upload as upload_module

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

# ============================================================================
# BATCH PROCESSING & EXPORT ENDPOINTS (STAGE 6)
# ============================================================================

class BatchAnalysisRequest(BaseModel):
    """Request for batch analysis of multiple time series"""
    series: List[Dict[str, Any]] = Field(..., description="List of time series with 'predicted', 'target', 'name'")
    user_id: Optional[str] = Field(None, description="Optional user ID")

    class Config:
        json_schema_extra = {
            "example": {
                "series": [
                    {
                        "name": "Model A",
                        "predicted": [1.0, 2.5, 3.2],
                        "target": [1.2, 2.3, 3.5]
                    },
                    {
                        "name": "Model B",
                        "predicted": [1.1, 2.4, 3.3],
                        "target": [1.2, 2.3, 3.5]
                    }
                ]
            }
        }

class CompareRequest(BaseModel):
    """Request to compare multiple analysis results"""
    results: List[Dict[str, Any]] = Field(..., description="List of analysis results")
    metrics: Optional[List[str]] = Field(None, description="Specific metrics to compare")

@app.post("/api/v1/batch/analyze")
async def batch_analyze(
    request: BatchAnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze multiple time series in batch.

    Each series should have:
    - predicted: list of predicted values
    - target: list of target/observed values
    - name: descriptive name (optional)

    Returns analysis results for all series.
    """
    try:
        results = batch_module.batch_analyze(request.series)

        # Log successful analyses to database
        if request.user_id:
            for result in results:
                if result.get('success'):
                    stats_module.log_analysis(
                        db=db,
                        metrics=result['metrics'],
                        n_points=result['n_points'],
                        session_id=str(uuid.uuid4()),
                        user_id=request.user_id,
                        analysis_name=result['name']
                    )

        return {
            'num_series': len(request.series),
            'num_successful': sum(1 for r in results if r.get('success')),
            'num_failed': sum(1 for r in results if not r.get('success')),
            'results': results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")

@app.post("/api/v1/batch/export/csv")
async def export_batch_csv(request: Dict[str, Any]):
    """
    Export batch analysis results to CSV format.

    Expects 'results' key with list of analysis results.
    """
    try:
        from fastapi.responses import Response

        results = request.get('results', [])
        include_header = request.get('include_header', True)

        csv_content = batch_module.export_to_csv(results, include_header=include_header)

        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=batch_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CSV export failed: {str(e)}")

@app.post("/api/v1/batch/export/json")
async def export_batch_json(request: Dict[str, Any]):
    """
    Export batch analysis results to JSON format.

    Expects 'results' key with list of analysis results.
    """
    try:
        from fastapi.responses import Response

        results = request.get('results', [])
        pretty = request.get('pretty', True)

        json_content = batch_module.export_to_json(results, pretty=pretty)

        return Response(
            content=json_content,
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=batch_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"JSON export failed: {str(e)}")

@app.post("/api/v1/batch/compare")
async def compare_analyses(request: CompareRequest):
    """
    Compare multiple analysis results side-by-side.

    Provides:
    - Statistical comparison of metrics across all series
    - Rankings (best to worst) for each metric
    - Summary statistics (min, max, mean, std, median)
    """
    try:
        comparison = batch_module.compare_runs(
            request.results,
            metrics_to_compare=request.metrics
        )

        return comparison

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")

@app.post("/api/v1/batch/report")
async def generate_report(request: Dict[str, Any]):
    """
    Generate a human-readable summary report for batch analysis.

    Returns formatted text report.
    """
    try:
        from fastapi.responses import PlainTextResponse

        results = request.get('results', [])
        report = batch_module.generate_summary_report(results)

        return PlainTextResponse(content=report)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

# ============================================================================
# ADVANCED VISUALIZATIONS ENDPOINTS (STAGE 7)
# ============================================================================

class VisualizationRequest(BaseModel):
    """Request for visualization generation"""
    predicted: List[float] = Field(..., description="Predicted values")
    target: List[float] = Field(..., description="Target/observed values")

@app.post("/api/v1/visualize/3d-surface")
async def create_3d_surface(request: VisualizationRequest):
    """
    Create a 3D surface plot showing the error landscape.

    Visualizes how prediction error varies across the predicted-target space.
    Includes actual data points and perfect prediction line.
    """
    try:
        P = np.array(request.predicted)
        T = np.array(request.target)

        if len(P) != len(T):
            raise HTTPException(status_code=400, detail="Length mismatch")

        fig_dict = viz_module.create_3d_surface_plot(P, T)
        return fig_dict

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"3D visualization failed: {str(e)}")

@app.post("/api/v1/visualize/residuals")
async def create_residual_plot(request: VisualizationRequest):
    """
    Create comprehensive residual analysis plots.

    Returns 4-panel figure:
    1. Residuals vs Predicted
    2. Residuals histogram with normal overlay
    3. Residuals vs Time/Index
    4. Scale-Location plot
    """
    try:
        P = np.array(request.predicted)
        T = np.array(request.target)

        if len(P) != len(T):
            raise HTTPException(status_code=400, detail="Length mismatch")

        fig_dict = viz_module.create_residual_analysis_plot(P, T)
        return fig_dict

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Residual analysis failed: {str(e)}")

@app.post("/api/v1/visualize/qq-plot")
async def create_qq_plot(request: VisualizationRequest):
    """
    Create Q-Q plot for normality assessment of residuals.

    Shows whether residuals follow a normal distribution.
    Points close to the reference line indicate normality.
    """
    try:
        P = np.array(request.predicted)
        T = np.array(request.target)

        if len(P) != len(T):
            raise HTTPException(status_code=400, detail="Length mismatch")

        fig_dict = viz_module.create_qq_plot(P, T)
        return fig_dict

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Q-Q plot failed: {str(e)}")

@app.post("/api/v1/visualize/autocorrelation")
async def create_autocorrelation_plot(request: VisualizationRequest):
    """
    Create ACF and PACF plots for residual autocorrelation analysis.

    Helps identify patterns in residuals that might indicate:
    - Temporal dependencies
    - Model inadequacy
    - Need for time series modeling

    Requires statsmodels library.
    """
    try:
        P = np.array(request.predicted)
        T = np.array(request.target)

        if len(P) != len(T):
            raise HTTPException(status_code=400, detail="Length mismatch")

        max_lags = min(40, len(P) // 2 - 1)
        fig_dict = viz_module.create_autocorrelation_plot(P, T, max_lags=max_lags)
        return fig_dict

    except ImportError:
        raise HTTPException(
            status_code=501,
            detail="Autocorrelation plots require statsmodels library. Install with: pip install statsmodels"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Autocorrelation analysis failed: {str(e)}")

@app.post("/api/v1/visualize/error-distribution")
async def create_error_distribution(request: VisualizationRequest):
    """
    Create error distribution plot with statistical overlay.

    Shows:
    - Histogram of errors
    - Fitted normal distribution
    - Statistics (mean, std, skewness, kurtosis)
    """
    try:
        P = np.array(request.predicted)
        T = np.array(request.target)

        if len(P) != len(T):
            raise HTTPException(status_code=400, detail="Length mismatch")

        fig_dict = viz_module.create_error_distribution_plot(P, T)
        return fig_dict

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error distribution plot failed: {str(e)}")

# ============================================================================
# PERFORMANCE OPTIMIZATION ENDPOINTS (STAGE 8)
# ============================================================================

from fastapi import File, UploadFile, Form

@app.post("/api/v1/upload/csv")
async def upload_csv_file(
    file: UploadFile = File(...),
    predicted_col: int = Form(0),
    target_col: int = Form(1),
    skip_header: bool = Form(True),
    max_rows: Optional[int] = Form(None)
):
    """
    Upload and parse large CSV files with streaming.

    Handles large files efficiently by streaming and parsing in chunks.

    Parameters:
    - file: CSV file to upload
    - predicted_col: Column index for predicted values (0-based)
    - target_col: Column index for target values (0-based)
    - skip_header: Skip first row if True
    - max_rows: Maximum rows to read (None = all)
    """
    try:
        # Validate file type
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="Only CSV files are supported")

        # Parse CSV with streaming
        result = await upload_module.parse_csv_columns(
            file,
            predicted_col=predicted_col,
            target_col=target_col,
            skip_header=skip_header,
            max_rows=max_rows
        )

        # Check if we got enough data
        if len(result['predicted']) < 2:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient valid data points: {len(result['predicted'])} (need at least 2)"
            )

        return {
            'success': True,
            'data': {
                'predicted': result['predicted'],
                'target': result['target']
            },
            'metadata': result['metadata']
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

@app.get("/api/v1/cache/stats")
async def get_cache_stats():
    """
    Get cache statistics.

    Returns information about memory cache and Redis (if configured).
    """
    return cache_module.get_cache_stats()

@app.post("/api/v1/cache/clear")
async def clear_cache(prefix: Optional[str] = None):
    """
    Clear cache entries.

    Parameters:
    - prefix: Optional prefix to clear specific entries. If None, clears all.
    """
    try:
        cache_module.invalidate_cache(prefix)
        return {
            'success': True,
            'message': f'Cache cleared{" for prefix: " + prefix if prefix else " (all entries)"}'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cache clear failed: {str(e)}")

@app.get("/api/v1/cache/health")
async def check_cache_health():
    """
    Check cache system health.

    Returns health status for memory cache and Redis.
    """
    return await cache_module.check_cache_health()

@app.get("/api/v1/health/full")
async def full_health_check():
    """
    Comprehensive health check including cache and database.
    """
    health = {
        'api': 'healthy',
        'cache': await cache_module.check_cache_health(),
        'database': 'unknown'
    }

    # Check database
    try:
        from .database import engine
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        health['database'] = 'healthy'
    except Exception as e:
        health['database'] = f'unhealthy: {str(e)}'

    return health

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
