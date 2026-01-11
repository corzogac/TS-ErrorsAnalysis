# Docker Deployment Guide

## Quick Start

### Using Make (Recommended)
```bash
# Build the image
make build

# Run in development mode
make run

# View logs
make logs

# Stop containers
make stop
```

### Using Docker Compose Directly
```bash
# Development mode (with hot reload)
docker-compose up -d

# Production mode
docker-compose -f docker-compose.prod.yml up -d

# Stop
docker-compose down
```

### Using Docker Only
```bash
# Build
docker build -t ts-errors-api .

# Run
docker run -d -p 8000:8000 --name ts-errors ts-errors-api
```

## Access Points

Once running:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Environment Variables

Set these in `docker-compose.yml` or via `-e` flag:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./ts_analysis.db` | Database connection string |
| `PYTHONUNBUFFERED` | `1` | Python logging output |

## Data Persistence

The SQLite database is persisted in the `./data` directory:
```bash
ls -la data/
# Should show ts_analysis.db
```

## Development Workflow

1. **Start containers**:
   ```bash
   make run
   ```

2. **Make code changes** - changes auto-reload

3. **View logs**:
   ```bash
   make logs
   ```

4. **Open shell for debugging**:
   ```bash
   make shell
   python
   >>> from api.main import app
   ```

5. **Stop when done**:
   ```bash
   make stop
   ```

## Production Deployment

### Local Production Mode
```bash
make run-prod
```

### Google Cloud Run

1. **Build and tag**:
   ```bash
   docker build -t gcr.io/YOUR-PROJECT/ts-errors-api .
   ```

2. **Push to GCR**:
   ```bash
   docker push gcr.io/YOUR-PROJECT/ts-errors-api
   ```

3. **Deploy**:
   ```bash
   gcloud run deploy ts-errors-api \
     --image gcr.io/YOUR-PROJECT/ts-errors-api \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars DATABASE_URL=postgresql://...
   ```

### Docker Hub
```bash
# Login
docker login

# Tag
docker tag ts-errors-api yourusername/ts-errors-api:latest

# Push
docker push yourusername/ts-errors-api:latest
```

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs api

# Check health
docker ps
```

### Database issues
```bash
# Reset database
make clean
make run
```

### Port already in use
```bash
# Change port in docker-compose.yml
ports:
  - "8080:8000"  # Use 8080 instead
```

### Hot reload not working
Make sure volume mounts are correct in `docker-compose.yml`:
```yaml
volumes:
  - ./src:/app/src
  - ./api:/app/api
```

## Multi-Stage Build

The Dockerfile uses multi-stage builds for smaller images:
- **Builder stage**: Installs all dependencies
- **Production stage**: Only runtime dependencies
- Final image: ~200MB

## Health Checks

Container includes health check that:
- Runs every 30 seconds
- Calls `/health` endpoint
- Marks unhealthy after 3 failures
- Useful for orchestration (Kubernetes, Cloud Run)

## Next Steps

- Stage 4: Add React frontend container
- Stage 8: Configure for Google Cloud Run with managed PostgreSQL
