# TS-ErrorsAnalysis API

FastAPI backend for hydrological time series error analysis.

## Quick Start

### Development Mode

```bash
# Install dependencies
pip install -r api/requirements.txt

# Run the API server
cd api
python main.py

# Or with uvicorn directly
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

### Analyze Time Series
```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "predicted": [1.0, 2.5, 3.2, 4.1, 5.0, 3.8, 2.9],
    "target": [1.2, 2.3, 3.5, 3.9, 4.8, 4.0, 3.1]
  }'
```

### Get Metrics Info
```bash
curl http://localhost:8000/api/v1/metrics/info
```

## Response Format

The `/api/v1/analyze` endpoint returns 28+ metrics:

```json
{
  "RMSE": 0.234,
  "NSC": 0.892,
  "Cor": 0.945,
  "KGE2009": 0.876,
  "Er": [0.2, -0.2, 0.3, ...],
  ...
}
```

## Testing

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/analyze",
    json={
        "predicted": [1.0, 2.0, 3.0, 4.0, 5.0],
        "target": [1.1, 2.1, 2.9, 4.2, 4.8]
    }
)

print(response.json())
```

## CORS Configuration

Currently set to allow all origins (`*`) for development.

**For production**, update `main.py`:
```python
allow_origins=["https://yourdomain.com"]
```

## Next Steps

- Stage 2: User statistics tracking
- Stage 3: Dockerization
- Stage 4: React frontend
