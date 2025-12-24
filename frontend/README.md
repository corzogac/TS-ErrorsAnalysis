# TS-ErrorsAnalysis Frontend

Modern React dashboard for hydrological time series error analysis.

## Tech Stack

- **React 18** with Vite (fast dev server & builds)
- **Tailwind CSS** for styling
- **Recharts** for data visualization
- **React Router** for navigation
- **Axios** for API calls

## Quick Start

### Development Mode

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

The app will be available at http://localhost:3000

### Production Build

```bash
npm run build
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/      # Reusable UI components
│   ├── pages/          # Page components (Dashboard, Analyze, etc.)
│   ├── services/       # API service layer
│   ├── utils/          # Utility functions
│   ├── types/          # TypeScript types (future)
│   ├── App.jsx         # Main app component
│   ├── main.jsx        # Entry point
│   └── index.css       # Global styles + Tailwind
├── public/             # Static assets
├── index.html          # HTML template
├── package.json        # Dependencies
├── vite.config.js      # Vite configuration
└── tailwind.config.js  # Tailwind configuration
```

## Features

### Pages

1. **Dashboard** (`/`)
   - System statistics overview
   - Average metrics
   - Feature highlights
   - Quick access to analysis

2. **Analyze** (`/analyze`)
   - Input predicted & target time series
   - Real-time analysis
   - 28+ error metrics display
   - Error visualization chart
   - Export results as JSON

3. **History** (`/history`)
   - View past analyses
   - Filter by user ID
   - Expandable metric details
   - Pagination support

4. **Stats** (`/stats`)
   - System-wide statistics
   - User-specific statistics
   - Top users chart
   - Average metrics over time

### API Integration

The frontend connects to the FastAPI backend at `http://localhost:8000`:

- `POST /api/v1/analyze` - Run analysis
- `GET /api/v1/stats/system` - System stats
- `GET /api/v1/stats/user/{id}` - User stats
- `GET /api/v1/history` - Analysis history

Session ID is automatically generated and persisted in localStorage.

## Environment Variables

Create `.env` file in frontend directory:

```env
VITE_API_URL=http://localhost:8000
```

## Customization

### Styling

Edit `tailwind.config.js` to customize colors, fonts, etc:

```js
theme: {
  extend: {
    colors: {
      primary: { /* your colors */ }
    }
  }
}
```

### API Endpoint

Update `src/services/api.js`:

```js
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://your-api-url'
```

## Docker Deployment

The frontend will be added to `docker-compose.yml` in Stage 4:

```bash
# Build
docker build -t ts-errors-frontend .

# Run
docker run -p 3000:3000 ts-errors-frontend
```

## Next Steps

- Stage 5: Add advanced time series tools (spline, interpolation)
- Stage 6: Implement spatial analysis
- Stage 7: Add 2D/3D visualization
- Add TypeScript for type safety
- Add unit tests with Vitest
- Add E2E tests with Playwright
