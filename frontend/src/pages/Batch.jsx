import { useState } from 'react';
import { FileText, Download, TrendingUp, Upload, X } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function Batch() {
  const [series, setSeries] = useState([]);
  const [batchResults, setBatchResults] = useState(null);
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Add a new empty series
  const addSeries = () => {
    setSeries([...series, {
      id: Date.now(),
      name: `Series ${series.length + 1}`,
      predicted: '',
      target: ''
    }]);
  };

  // Remove a series
  const removeSeries = (id) => {
    setSeries(series.filter(s => s.id !== id));
  };

  // Update series data
  const updateSeries = (id, field, value) => {
    setSeries(series.map(s =>
      s.id === id ? { ...s, [field]: value } : s
    ));
  };

  // Parse input (comma or space separated)
  const parseInput = (input) => {
    return input.trim().split(/[\s,]+/).map(v => parseFloat(v)).filter(v => !isNaN(v));
  };

  // Batch analyze
  const handleBatchAnalyze = async () => {
    setLoading(true);
    setError(null);
    setBatchResults(null);
    setComparison(null);

    try {
      // Parse all series
      const parsedSeries = series.map(s => ({
        name: s.name,
        predicted: parseInput(s.predicted),
        target: parseInput(s.target)
      }));

      // Validate
      if (parsedSeries.length === 0) {
        throw new Error('Please add at least one series');
      }

      for (const s of parsedSeries) {
        if (s.predicted.length === 0 || s.target.length === 0) {
          throw new Error(`Series "${s.name}" has empty data`);
        }
      }

      // Call batch analyze API
      const response = await fetch(`${API_URL}/api/v1/batch/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ series: parsedSeries })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Batch analysis failed');
      }

      const data = await response.json();
      setBatchResults(data);

      // Auto-compare if multiple successful results
      if (data.num_successful > 1) {
        const successfulResults = data.results.filter(r => r.success);
        await compareResults(successfulResults);
      }

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Compare results
  const compareResults = async (results) => {
    try {
      const response = await fetch(`${API_URL}/api/v1/batch/compare`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ results })
      });

      if (!response.ok) {
        throw new Error('Comparison failed');
      }

      const comparisonData = await response.json();
      setComparison(comparisonData);

    } catch (err) {
      console.error('Comparison error:', err);
    }
  };

  // Export to CSV
  const exportCSV = async () => {
    if (!batchResults) return;

    try {
      const response = await fetch(`${API_URL}/api/v1/batch/export/csv`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ results: batchResults.results })
      });

      if (!response.ok) throw new Error('Export failed');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `batch_analysis_${new Date().getTime()}.csv`;
      a.click();
      window.URL.revokeObjectURL(url);

    } catch (err) {
      alert('Export failed: ' + err.message);
    }
  };

  // Export to JSON
  const exportJSON = async () => {
    if (!batchResults) return;

    try {
      const response = await fetch(`${API_URL}/api/v1/batch/export/json`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ results: batchResults.results, pretty: true })
      });

      if (!response.ok) throw new Error('Export failed');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `batch_analysis_${new Date().getTime()}.json`;
      a.click();
      window.URL.revokeObjectURL(url);

    } catch (err) {
      alert('Export failed: ' + err.message);
    }
  };

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Batch Analysis</h1>
        <p className="text-gray-600">Analyze and compare multiple time series at once</p>
      </div>

      {/* Input Section */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Time Series Input</h2>
          <button
            onClick={addSeries}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            <Upload className="h-4 w-4" />
            Add Series
          </button>
        </div>

        <div className="space-y-4">
          {series.map((s, idx) => (
            <div key={s.id} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <input
                  type="text"
                  value={s.name}
                  onChange={(e) => updateSeries(s.id, 'name', e.target.value)}
                  className="text-lg font-medium border-b border-transparent focus:border-blue-600 outline-none"
                  placeholder="Series name"
                />
                <button
                  onClick={() => removeSeries(s.id)}
                  className="text-red-600 hover:text-red-800"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Predicted Values
                  </label>
                  <textarea
                    value={s.predicted}
                    onChange={(e) => updateSeries(s.id, 'predicted', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    rows="3"
                    placeholder="1.0, 2.5, 3.2, 4.1"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Target Values
                  </label>
                  <textarea
                    value={s.target}
                    onChange={(e) => updateSeries(s.id, 'target', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    rows="3"
                    placeholder="1.2, 2.3, 3.5, 3.9"
                  />
                </div>
              </div>
            </div>
          ))}

          {series.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <FileText className="h-12 w-12 mx-auto mb-3 opacity-50" />
              <p>No series added yet. Click "Add Series" to start.</p>
            </div>
          )}
        </div>

        {series.length > 0 && (
          <button
            onClick={handleBatchAnalyze}
            disabled={loading}
            className="mt-6 w-full py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition disabled:bg-gray-400 disabled:cursor-not-allowed font-medium"
          >
            {loading ? 'Analyzing...' : `Analyze ${series.length} Series`}
          </button>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 rounded-lg p-4 mb-6">
          <p className="font-medium">Error:</p>
          <p>{error}</p>
        </div>
      )}

      {/* Results Section */}
      {batchResults && (
        <div className="space-y-6">
          {/* Summary */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">Results Summary</h2>
              <div className="flex gap-2">
                <button
                  onClick={exportCSV}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
                >
                  <Download className="h-4 w-4" />
                  CSV
                </button>
                <button
                  onClick={exportJSON}
                  className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition"
                >
                  <Download className="h-4 w-4" />
                  JSON
                </button>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4 mb-6">
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-gray-600 text-sm">Total Series</p>
                <p className="text-2xl font-bold text-gray-900">{batchResults.num_series}</p>
              </div>
              <div className="bg-green-50 rounded-lg p-4">
                <p className="text-gray-600 text-sm">Successful</p>
                <p className="text-2xl font-bold text-green-600">{batchResults.num_successful}</p>
              </div>
              <div className="bg-red-50 rounded-lg p-4">
                <p className="text-gray-600 text-sm">Failed</p>
                <p className="text-2xl font-bold text-red-600">{batchResults.num_failed}</p>
              </div>
            </div>

            {/* Individual Results */}
            <div className="space-y-3">
              {batchResults.results.map((result, idx) => (
                <div
                  key={idx}
                  className={`border rounded-lg p-4 ${
                    result.success ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold text-gray-900">{result.name}</h3>
                    {result.success && (
                      <span className="text-sm text-gray-600">{result.n_points} points</span>
                    )}
                  </div>

                  {result.success ? (
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                      <div>
                        <span className="text-gray-600">RMSE:</span>
                        <span className="ml-2 font-medium">{result.metrics.RMSE.toFixed(4)}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">NSE:</span>
                        <span className="ml-2 font-medium">{result.metrics.NSC.toFixed(4)}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">R:</span>
                        <span className="ml-2 font-medium">{result.metrics.Cor.toFixed(4)}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">KGE:</span>
                        <span className="ml-2 font-medium">{result.metrics.KGE2012.toFixed(4)}</span>
                      </div>
                    </div>
                  ) : (
                    <p className="text-red-700 text-sm">{result.error}</p>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Comparison Section */}
          {comparison && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center gap-2 mb-6">
                <TrendingUp className="h-6 w-6 text-blue-600" />
                <h2 className="text-xl font-semibold text-gray-900">Comparison</h2>
              </div>

              {/* Key Metrics Comparison Chart */}
              <div className="mb-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Key Metrics Overview</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart
                    data={comparison.series_names.map((name, idx) => {
                      const data = { name };
                      ['RMSE', 'NSC', 'KGE2012'].forEach(metric => {
                        if (comparison.comparison_table[metric]) {
                          data[metric] = comparison.comparison_table[metric].values[name];
                        }
                      });
                      return data;
                    })}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="RMSE" fill="#ef4444" />
                    <Bar dataKey="NSC" fill="#3b82f6" />
                    <Bar dataKey="KGE2012" fill="#10b981" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Rankings */}
              <div className="grid md:grid-cols-2 gap-6">
                {['NSC', 'RMSE', 'KGE2012', 'Cor'].map(metric => {
                  const ranking = comparison.rankings[metric];
                  if (!ranking) return null;

                  return (
                    <div key={metric} className="border border-gray-200 rounded-lg p-4">
                      <h4 className="font-semibold text-gray-900 mb-3">
                        {metric} Ranking
                        <span className="text-sm text-gray-500 ml-2">
                          ({ranking.higher_is_better ? '↑ Higher Better' : '↓ Lower Better'})
                        </span>
                      </h4>
                      <div className="space-y-2">
                        {ranking.ranking.map((item, idx) => (
                          <div
                            key={idx}
                            className={`flex items-center justify-between p-2 rounded ${
                              idx === 0 ? 'bg-yellow-50 border border-yellow-200' : 'bg-gray-50'
                            }`}
                          >
                            <div className="flex items-center gap-3">
                              <span className="font-bold text-gray-600">#{item.rank}</span>
                              <span className="font-medium">{item.name}</span>
                            </div>
                            <span className="font-mono text-sm">{item.value.toFixed(4)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
