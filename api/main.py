# ---------------------------------------------------------------------------
# File    : api/main.py
# Purpose : FastAPI backend for TS-ErrorsAnalysis web service
# Author  : Generated for TS-ErrorsAnalysis
# Version : 1.0
# License : MIT
# SPDX-License-Identifier: MIT
# ---------------------------------------------------------------------------
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import numpy as np
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.errors import compute_error_metrics

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

    class Config:
        json_schema_extra = {
            "example": {
                "predicted": [1.0, 2.5, 3.2, 4.1, 5.0],
                "target": [1.2, 2.3, 3.5, 3.9, 4.8]
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
async def analyze_time_series(data: TimeSeriesInput):
    """
    Analyze time series: compute error metrics for predicted vs target values

    Returns 28+ metrics including:
    - RMSE, NSE/NSC, Correlation
    - KGE (2009, 2012)
    - Index of Agreement (d, d1)
    - Persistence metrics
    - Error series and proportions
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
