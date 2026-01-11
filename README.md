# TS-ErrorsAnalysis

**Hydrological time series error analysis toolkit** with FastAPI backend, React frontend, and advanced time series processing tools.

---

## 🌐 **Deploy Your Own (FREE - 5 Minutes)**

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/corzogac/TS-ErrorsAnalysis)

[![Deploy to Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/corzogac/TS-ErrorsAnalysis&project-name=ts-errors-analysis&root-directory=frontend&env=VITE_API_URL)

**Quick Steps:**
1. Click "Deploy to Render" → deploys backend + database
2. Copy your Render URL (e.g., `https://ts-errors-api.onrender.com`)
3. Click "Deploy to Vercel" → deploys frontend
4. Set environment variable `VITE_API_URL` to your Render URL
5. **Done!** Your app is live 🎉

**Full Guide**: See [DEPLOYMENT.md](DEPLOYMENT.md)

---

## ✨ Features

### Error Analysis
- **28+ metrics**: RMSE, NSE/NSC, KGE (2009, 2012), correlation, R², PBIAS, sMAPE, Index of Agreement
- **Persistence baseline**: Compare against naive lag-1 forecast
- **Hydrology-focused**: Metrics designed for hydrological applications

### Advanced Time Series Tools
- **Interpolation**: Cubic, quadratic, linear splines
- **Smoothing**: Moving average, Savitzky-Golay, exponential
- **Decomposition**: Trend + seasonal + residual components
- **Outlier detection**: Z-score and IQR methods
- **Resampling**: Change sampling rate with interpolation

### Modern Web Interface
- **Dashboard**: System overview with statistics
- **Analyze**: Upload data, get instant results with charts
- **Tools**: Interactive time series processing
- **History**: Browse past analyses
- **Stats**: User and system statistics

### Developer Features
- **RESTful API** with automatic OpenAPI docs (`/docs`)
- **Docker containerized** for easy deployment
- **Database tracking** of all analyses (SQLite/PostgreSQL)
- **Session management** with user statistics
- **CORS enabled** for frontend integration

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)
```bash
git clone https://github.com/corzogac/TS-ErrorsAnalysis.git
cd TS-ErrorsAnalysis

# Build and run
make build
make run

# Access the app
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Manual Setup
```bash
# Backend
pip install -r requirements.txt -r api/requirements.txt
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

---

## 📊 API Examples

### Analyze Time Series
```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "predicted": [1.0, 2.5, 3.2, 4.1, 5.0],
    "target": [1.2, 2.3, 3.5, 3.9, 4.8],
    "user_id": "researcher_123",
    "analysis_name": "River Discharge Model"
  }'
```

### Smooth Data
```bash
curl -X POST http://localhost:8000/api/v1/timeseries/smooth \
  -H "Content-Type: application/json" \
  -d '{
    "values": [1.0, 2.5, 3.2, 4.1, 5.0, 4.2, 3.8],
    "method": "savitzky_golay",
    "window_size": 5
  }'
```

### Get Statistics
```bash
curl http://localhost:8000/api/v1/stats/system
```

---

## 🛠️ Tech Stack

**Backend**:
- FastAPI (Python 3.11+)
- SQLAlchemy (ORM)
- NumPy, SciPy (numerical computing)
- Pydantic (validation)

**Frontend**:
- React 18 + Vite
- Tailwind CSS
- Recharts (visualization)
- Axios (API client)

**Database**:
- PostgreSQL (production)
- SQLite (development)

**Deployment**:
- Docker + docker-compose
- Vercel (frontend)
- Render/Railway (backend)

---

## 📚 Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Complete deployment guide (Vercel, Render, Railway)
- **[DOCKER.md](DOCKER.md)** - Docker setup and commands
- **[CLAUDE.md](CLAUDE.md)** - AI assistant development guide
- **[API Docs](http://localhost:8000/docs)** - Interactive API documentation (when running)

---

## 🧪 Testing

```bash
# Run comprehensive test suite
python test_all_stages.py

# Tests cover:
# - All API endpoints
# - Database operations
# - Time series tools
# - Error handling
# - Integration workflows
```

---

## 📦 Project Structure

```
TS-ErrorsAnalysis/
├── api/                    # FastAPI backend
│   ├── main.py            # API endpoints
│   ├── database.py        # Database models
│   ├── stats.py           # Statistics functions
│   └── timeseries.py      # Time series processing
├── frontend/              # React frontend
│   ├── src/
│   │   ├── pages/        # Dashboard, Analyze, Tools, History, Stats
│   │   ├── services/     # API client
│   │   └── App.jsx       # Main app component
│   └── package.json
├── src/                   # Core Python modules
│   ├── errors.py         # Error metrics computation
│   └── plots.py          # Visualization
├── matlab/               # MATLAB implementation
│   └── Error1.m
├── Dockerfile            # Container image
├── docker-compose.yml    # Local development
├── render.yaml           # Render deployment config
└── test_all_stages.py    # Test suite
```

---

## 🎯 Metrics Computed

### Basic Errors
- RMSE, MAE, SSE, NRMSE

### Model Skill
- NSC/NSE (Nash-Sutcliffe)
- Correlation (Pearson r)
- R² (Coefficient of determination)
- RSR (RMSE-to-StdDev ratio)

### Bias Metrics
- PBIAS (Percent Bias)
- sMAPE (Symmetric MAPE)
- MARE (Mean Absolute Relative Error)

### Hydrology-Specific
- KGE2009, KGE2012 (Kling-Gupta Efficiency)
- d, d1 (Index of Agreement)

### Persistence
- PERS (Coefficient of persistence)
- RMSEN (Naive forecast RMSE)

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python test_all_stages.py`
5. Submit a pull request

---

## 📝 License

MIT License - See [LICENSE](LICENSE)

---

## 👤 Author

**Gerald Augusto Corzo Pérez**
IHE Delft — Hydroinformatics
Department of Coastal & Urban Risk & Resilience

---

## 🌟 Citation

```bibtex
@software{corzo2025errors,
  author = {Corzo Pérez, Gerald Augusto},
  title = {TS-ErrorsAnalysis: Hydrological Time Series Error Analysis},
  year = {2025},
  publisher = {GitHub},
  url = {https://github.com/corzogac/TS-ErrorsAnalysis}
}
```

---

## 💡 Need Help?

- 📖 Check [DEPLOYMENT.md](DEPLOYMENT.md) for deployment issues
- 🐛 [Open an issue](https://github.com/corzogac/TS-ErrorsAnalysis/issues)
- 📧 Contact the author

---

**Made with ❤️ for the hydrology community**
