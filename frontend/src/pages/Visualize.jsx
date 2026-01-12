import { useState } from 'react';
import Plot from 'react-plotly.js';
import { Eye, Loader, AlertCircle } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const VISUALIZATION_TYPES = [
  {
    id: '3d-surface',
    name: '3D Error Surface',
    description: 'Visualize error landscape in 3D space',
    endpoint: '/api/v1/visualize/3d-surface'
  },
  {
    id: 'residuals',
    name: 'Residual Analysis',
    description: '4-panel residual diagnostic plots',
    endpoint: '/api/v1/visualize/residuals'
  },
  {
    id: 'qq-plot',
    name: 'Q-Q Plot',
    description: 'Normality assessment of residuals',
    endpoint: '/api/v1/visualize/qq-plot'
  },
  {
    id: 'autocorrelation',
    name: 'Autocorrelation (ACF/PACF)',
    description: 'Temporal dependency analysis',
    endpoint: '/api/v1/visualize/autocorrelation'
  },
  {
    id: 'error-distribution',
    name: 'Error Distribution',
    description: 'Error histogram with statistical overlay',
    endpoint: '/api/v1/visualize/error-distribution'
  }
];

export default function Visualize() {
  const [predicted, setPredicted] = useState('');
  const [target, setTarget] = useState('');
  const [selectedViz, setSelectedViz] = useState('3d-surface');
  const [plotData, setPlotData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const parseInput = (input) => {
    return input.trim().split(/[\s,]+/).map(v => parseFloat(v)).filter(v => !isNaN(v));
  };

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    setPlotData(null);

    try {
      const predictedValues = parseInput(predicted);
      const targetValues = parseInput(target);

      if (predictedValues.length === 0 || targetValues.length === 0) {
        throw new Error('Please enter valid numerical data');
      }

      if (predictedValues.length !== targetValues.length) {
        throw new Error('Predicted and target must have the same length');
      }

      const vizType = VISUALIZATION_TYPES.find(v => v.id === selectedViz);

      const response = await fetch(`${API_URL}${vizType.endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          predicted: predictedValues,
          target: targetValues
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Visualization failed');
      }

      const data = await response.json();
      setPlotData(data);

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadSampleData = () => {
    // Generate sample data with noise
    const n = 100;
    const x = Array.from({ length: n }, (_, i) => i);
    const actualTarget = x.map(i => Math.sin(i / 10) * 10 + 50);
    const actualPredicted = actualTarget.map(v => v + (Math.random() - 0.5) * 5);

    setTarget(actualTarget.map(v => v.toFixed(2)).join(', '));
    setPredicted(actualPredicted.map(v => v.toFixed(2)).join(', '));
  };

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Advanced Visualizations</h1>
        <p className="text-gray-600">Interactive diagnostic plots powered by Plotly</p>
      </div>

      {/* Input Section */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Data Input</h2>

        <div className="grid md:grid-cols-2 gap-6 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Predicted Values
            </label>
            <textarea
              value={predicted}
              onChange={(e) => setPredicted(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows="4"
              placeholder="1.0, 2.5, 3.2, 4.1, 5.0, ..."
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Target Values
            </label>
            <textarea
              value={target}
              onChange={(e) => setTarget(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows="4"
              placeholder="1.2, 2.3, 3.5, 3.9, 4.8, ..."
            />
          </div>
        </div>

        <button
          onClick={loadSampleData}
          className="text-sm text-blue-600 hover:text-blue-800 mb-4"
        >
          Load Sample Data
        </button>

        {/* Visualization Type Selection */}
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Visualization Type
          </label>
          <div className="grid md:grid-cols-3 gap-3">
            {VISUALIZATION_TYPES.map((viz) => (
              <button
                key={viz.id}
                onClick={() => setSelectedViz(viz.id)}
                className={`p-4 border-2 rounded-lg text-left transition ${
                  selectedViz === viz.id
                    ? 'border-blue-600 bg-blue-50'
                    : 'border-gray-200 hover:border-blue-300'
                }`}
              >
                <div className="font-semibold text-gray-900 mb-1">{viz.name}</div>
                <div className="text-sm text-gray-600">{viz.description}</div>
              </button>
            ))}
          </div>
        </div>

        <button
          onClick={handleGenerate}
          disabled={loading || !predicted || !target}
          className="w-full py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:bg-gray-400 disabled:cursor-not-allowed font-medium flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <Loader className="h-5 w-5 animate-spin" />
              Generating...
            </>
          ) : (
            <>
              <Eye className="h-5 w-5" />
              Generate Visualization
            </>
          )}
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-red-800">Error</p>
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        </div>
      )}

      {/* Plot Display */}
      {plotData && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center gap-2 mb-4">
            <Eye className="h-6 w-6 text-blue-600" />
            <h2 className="text-xl font-semibold text-gray-900">
              {VISUALIZATION_TYPES.find(v => v.id === selectedViz)?.name}
            </h2>
          </div>

          <div className="flex justify-center">
            <Plot
              data={plotData.data}
              layout={plotData.layout}
              config={{
                responsive: true,
                displayModeBar: true,
                modeBarButtonsToRemove: ['toImage'],
                displaylogo: false
              }}
              style={{ width: '100%', height: '100%' }}
            />
          </div>

          <div className="mt-4 p-4 bg-gray-50 rounded-lg">
            <h3 className="font-medium text-gray-900 mb-2">Interpretation Guide</h3>
            <div className="text-sm text-gray-700 space-y-1">
              {selectedViz === '3d-surface' && (
                <>
                  <p>• <strong>Error Surface:</strong> Shows how error magnitude varies across the predicted-target space</p>
                  <p>• <strong>Red Line:</strong> Perfect prediction line (zero error)</p>
                  <p>• <strong>Blue Points:</strong> Your actual data points colored by error magnitude</p>
                </>
              )}
              {selectedViz === 'residuals' && (
                <>
                  <p>• <strong>Top Left:</strong> Random scatter indicates good model fit</p>
                  <p>• <strong>Top Right:</strong> Bell-shaped histogram suggests normality</p>
                  <p>• <strong>Bottom Left:</strong> No trends over time indicates independence</p>
                  <p>• <strong>Bottom Right:</strong> Flat trend indicates constant variance (homoscedasticity)</p>
                </>
              )}
              {selectedViz === 'qq-plot' && (
                <>
                  <p>• <strong>Points on line:</strong> Residuals follow normal distribution</p>
                  <p>• <strong>S-curve:</strong> Heavy-tailed distribution</p>
                  <p>• <strong>Deviations at ends:</strong> Outliers present</p>
                </>
              )}
              {selectedViz === 'autocorrelation' && (
                <>
                  <p>• <strong>Bars within dashed lines:</strong> No significant autocorrelation (good)</p>
                  <p>• <strong>Bars exceeding lines:</strong> Temporal dependencies exist</p>
                  <p>• <strong>ACF:</strong> Overall correlation at each lag</p>
                  <p>• <strong>PACF:</strong> Direct correlation excluding intermediate lags</p>
                </>
              )}
              {selectedViz === 'error-distribution' && (
                <>
                  <p>• <strong>Red curve:</strong> Fitted normal distribution</p>
                  <p>• <strong>Skewness:</strong> Measure of asymmetry (0 = symmetric)</p>
                  <p>• <strong>Kurtosis:</strong> Measure of tail heaviness (0 = normal)</p>
                </>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Info Cards */}
      <div className="grid md:grid-cols-2 gap-6 mt-6">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="font-semibold text-blue-900 mb-2">Why Advanced Visualizations?</h3>
          <ul className="text-sm text-blue-800 space-y-2">
            <li>• Identify systematic patterns in residuals</li>
            <li>• Assess model assumptions (normality, independence)</li>
            <li>• Detect outliers and anomalies</li>
            <li>• Understand error characteristics</li>
            <li>• Guide model improvements</li>
          </ul>
        </div>

        <div className="bg-green-50 border border-green-200 rounded-lg p-6">
          <h3 className="font-semibold text-green-900 mb-2">Interactive Features</h3>
          <ul className="text-sm text-green-800 space-y-2">
            <li>• Zoom and pan with mouse</li>
            <li>• Hover for detailed values</li>
            <li>• Rotate 3D plots by dragging</li>
            <li>• Toggle traces on/off</li>
            <li>• Reset view with home button</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
