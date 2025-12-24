import { useState } from 'react'
import { Wand2, TrendingUp, Filter, AlertTriangle } from 'lucide-react'
import { analysisApi } from '../services/api'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ScatterChart, Scatter } from 'recharts'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function Tools() {
  const [activeTab, setActiveTab] = useState('interpolate')
  const [inputData, setInputData] = useState('1, 2.5, 3.2, 4.1, 5.0, 4.2, 3.8, 4.5, 5.2, 4.9')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const parseInput = () => {
    return inputData.split(/[,\s]+/).map(Number).filter(x => !isNaN(x))
  }

  const handleInterpolate = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const values = parseInput()
      const response = await axios.post(`${API_BASE_URL}/api/v1/timeseries/interpolate`, {
        values,
        kind: 'cubic',
        num_points: values.length * 2
      })
      setResult({ type: 'interpolate', data: response.data })
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleSmooth = async (method) => {
    setLoading(true)
    setError(null)

    try {
      const values = parseInput()
      const response = await axios.post(`${API_BASE_URL}/api/v1/timeseries/smooth`, {
        values,
        method,
        window_size: 5
      })
      setResult({ type: 'smooth', data: response.data })
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleDecompose = async () => {
    setLoading(true)
    setError(null)

    try {
      const values = parseInput()
      const response = await axios.post(`${API_BASE_URL}/api/v1/timeseries/decompose`, {
        values,
        period: 12,
        model: 'additive'
      })
      setResult({ type: 'decompose', data: response.data })
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleOutliers = async () => {
    setLoading(true)
    setError(null)

    try {
      const values = parseInput()
      const response = await axios.post(`${API_BASE_URL}/api/v1/timeseries/detect-outliers`, {
        values,
        method: 'zscore',
        threshold: 2.0
      })
      setResult({ type: 'outliers', data: response.data })
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h2 className="text-3xl font-bold text-gray-900 mb-8">Advanced Time Series Tools</h2>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Sidebar with Tools */}
        <div className="space-y-4">
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">Input Data</h3>
            <textarea
              className="input font-mono text-sm"
              rows="4"
              value={inputData}
              onChange={(e) => setInputData(e.target.value)}
              placeholder="Enter comma-separated values"
            />
            <p className="text-xs text-gray-500 mt-2">
              Enter time series values separated by commas or spaces
            </p>
          </div>

          <div className="card space-y-3">
            <h3 className="text-lg font-semibold mb-2">Tools</h3>

            <ToolButton
              icon={<Wand2 size={18} />}
              label="Spline Interpolation"
              onClick={handleInterpolate}
              disabled={loading}
            />

            <div>
              <p className="text-sm font-medium text-gray-700 mb-2">Smoothing</p>
              <div className="space-y-2">
                <ToolButton
                  label="Moving Average"
                  onClick={() => handleSmooth('moving_average')}
                  disabled={loading}
                  small
                />
                <ToolButton
                  label="Savitzky-Golay"
                  onClick={() => handleSmooth('savitzky_golay')}
                  disabled={loading}
                  small
                />
                <ToolButton
                  label="Exponential"
                  onClick={() => handleSmooth('exponential')}
                  disabled={loading}
                  small
                />
              </div>
            </div>

            <ToolButton
              icon={<TrendingUp size={18} />}
              label="Decompose Trend"
              onClick={handleDecompose}
              disabled={loading}
            />

            <ToolButton
              icon={<AlertTriangle size={18} />}
              label="Detect Outliers"
              onClick={handleOutliers}
              disabled={loading}
            />
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded text-sm">
              {error}
            </div>
          )}
        </div>

        {/* Results Panel */}
        <div className="lg:col-span-2">
          <div className="card">
            <h3 className="text-xl font-semibold mb-4">Results</h3>

            {!result && !loading && (
              <div className="text-center py-12 text-gray-500">
                Select a tool and click to see results
              </div>
            )}

            {loading && (
              <div className="text-center py-12 text-gray-500">
                Processing...
              </div>
            )}

            {result && result.type === 'interpolate' && (
              <InterpolateResult data={result.data} />
            )}

            {result && result.type === 'smooth' && (
              <SmoothResult data={result.data} />
            )}

            {result && result.type === 'decompose' && (
              <DecomposeResult data={result.data} />
            )}

            {result && result.type === 'outliers' && (
              <OutliersResult data={result.data} />
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

function ToolButton({ icon, label, onClick, disabled, small }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`w-full flex items-center gap-2 px-4 ${small ? 'py-2' : 'py-3'} bg-white border border-gray-300 rounded-md hover:bg-gray-50 hover:border-primary-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-left`}
    >
      {icon}
      <span className={small ? 'text-sm' : ''}>{label}</span>
    </button>
  )
}

function InterpolateResult({ data }) {
  const chartData = data.indices.map((x, i) => ({ x, y: data.values[i] }))

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div className="bg-blue-50 p-3 rounded">
          <p className="text-blue-600 font-medium">Original Points</p>
          <p className="text-2xl font-bold text-blue-900">{data.original_points}</p>
        </div>
        <div className="bg-green-50 p-3 rounded">
          <p className="text-green-600 font-medium">Interpolated Points</p>
          <p className="text-2xl font-bold text-green-900">{data.interpolated_points}</p>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="x" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="y" stroke="#2563eb" strokeWidth={2} name="Interpolated" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

function SmoothResult({ data }) {
  const chartData = data.original.map((orig, i) => ({
    index: i,
    original: orig,
    smoothed: data.smoothed[i]
  }))

  return (
    <div className="space-y-4">
      <div className="bg-blue-50 p-3 rounded text-sm">
        <p className="text-blue-600 font-medium">Method: <span className="text-blue-900 font-semibold">{data.method}</span></p>
        <p className="text-blue-600 font-medium">Window: <span className="text-blue-900 font-semibold">{data.window_size}</span></p>
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="index" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="original" stroke="#9ca3af" strokeWidth={1} name="Original" strokeDasharray="5 5" />
          <Line type="monotone" dataKey="smoothed" stroke="#2563eb" strokeWidth={2} name="Smoothed" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}

function DecomposeResult({ data }) {
  const trendData = data.trend.map((val, i) => ({ index: i, value: val }))
  const seasonalData = data.seasonal.map((val, i) => ({ index: i, value: val }))

  return (
    <div className="space-y-6">
      <div className="bg-blue-50 p-3 rounded text-sm">
        <p className="text-blue-600 font-medium">Period: <span className="text-blue-900 font-semibold">{data.period}</span></p>
        <p className="text-blue-600 font-medium">Model: <span className="text-blue-900 font-semibold">{data.model}</span></p>
      </div>

      <div>
        <h4 className="text-sm font-semibold mb-2">Trend Component</h4>
        <ResponsiveContainer width="100%" height={150}>
          <LineChart data={trendData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="index" hide />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="value" stroke="#2563eb" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div>
        <h4 className="text-sm font-semibold mb-2">Seasonal Component</h4>
        <ResponsiveContainer width="100%" height={150}>
          <LineChart data={seasonalData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="index" hide />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="value" stroke="#059669" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

function OutliersResult({ data }) {
  const chartData = data.values.map((val, i) => ({
    index: i,
    value: val,
    isOutlier: data.is_outlier[i]
  }))

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div className="bg-red-50 p-3 rounded">
          <p className="text-red-600 font-medium">Outliers Detected</p>
          <p className="text-2xl font-bold text-red-900">{data.num_outliers}</p>
        </div>
        <div className="bg-blue-50 p-3 rounded">
          <p className="text-blue-600 font-medium">Method</p>
          <p className="text-lg font-bold text-blue-900">{data.method} (t={data.threshold})</p>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <ScatterChart>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="index" name="Index" />
          <YAxis dataKey="value" name="Value" />
          <Tooltip cursor={{ strokeDasharray: '3 3' }} />
          <Legend />
          <Scatter name="Normal" data={chartData.filter(d => !d.isOutlier)} fill="#2563eb" />
          <Scatter name="Outliers" data={chartData.filter(d => d.isOutlier)} fill="#dc2626" />
        </ScatterChart>
      </ResponsiveContainer>

      {data.outlier_indices.length > 0 && (
        <div className="bg-red-50 p-3 rounded text-sm">
          <p className="text-red-700 font-medium">Outlier indices: {data.outlier_indices.join(', ')}</p>
        </div>
      )}
    </div>
  )
}
