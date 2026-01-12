import { useState, useEffect } from 'react'
import { Upload, Download, Save, FolderOpen } from 'lucide-react'
import { analysisApi } from '../services/api'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const STORAGE_KEY = 'ts-analysis-projects'

export default function Analyze() {
  const [predicted, setPredicted] = useState('')
  const [target, setTarget] = useState('')
  const [userId, setUserId] = useState('')
  const [analysisName, setAnalysisName] = useState('')
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [savedProjects, setSavedProjects] = useState([])
  const [showSaveDialog, setShowSaveDialog] = useState(false)
  const [showLoadDialog, setShowLoadDialog] = useState(false)

  // Load saved projects on mount
  useEffect(() => {
    loadSavedProjects()
  }, [])

  // Auto-save current state to localStorage
  useEffect(() => {
    const autoSaveTimer = setTimeout(() => {
      if (predicted || target || analysisName) {
        localStorage.setItem('ts-analysis-autosave', JSON.stringify({
          predicted,
          target,
          userId,
          analysisName,
          timestamp: new Date().toISOString()
        }))
      }
    }, 1000)

    return () => clearTimeout(autoSaveTimer)
  }, [predicted, target, userId, analysisName])

  const loadSavedProjects = () => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      if (stored) {
        setSavedProjects(JSON.parse(stored))
      }
    } catch (err) {
      console.error('Failed to load projects:', err)
    }
  }

  const saveCurrentProject = (projectName) => {
    if (!projectName.trim()) {
      alert('Please enter a project name')
      return
    }

    const project = {
      name: projectName,
      predicted,
      target,
      userId,
      analysisName,
      savedAt: new Date().toISOString(),
      results
    }

    const projects = [...savedProjects]
    const existingIndex = projects.findIndex(p => p.name === projectName)

    if (existingIndex >= 0) {
      // Update existing
      projects[existingIndex] = project
    } else {
      // Add new
      projects.push(project)
    }

    localStorage.setItem(STORAGE_KEY, JSON.stringify(projects))
    setSavedProjects(projects)
    setShowSaveDialog(false)
    alert(`Project "${projectName}" saved successfully!`)
  }

  const loadProject = (project) => {
    setPredicted(project.predicted)
    setTarget(project.target)
    setUserId(project.userId || '')
    setAnalysisName(project.analysisName || '')
    setResults(project.results || null)
    setShowLoadDialog(false)
  }

  const deleteProject = (projectName) => {
    if (confirm(`Delete project "${projectName}"?`)) {
      const projects = savedProjects.filter(p => p.name !== projectName)
      localStorage.setItem(STORAGE_KEY, JSON.stringify(projects))
      setSavedProjects(projects)
    }
  }

  const restoreAutoSave = () => {
    try {
      const autosave = localStorage.getItem('ts-analysis-autosave')
      if (autosave) {
        const data = JSON.parse(autosave)
        setPredicted(data.predicted || '')
        setTarget(data.target || '')
        setUserId(data.userId || '')
        setAnalysisName(data.analysisName || '')
        alert('Auto-saved data restored!')
      }
    } catch (err) {
      alert('No auto-saved data found')
    }
  }

  const handleAnalyze = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      // Parse input arrays
      const predictedArray = predicted.split(/[,\s]+/).map(Number).filter(x => !isNaN(x))
      const targetArray = target.split(/[,\s]+/).map(Number).filter(x => !isNaN(x))

      if (predictedArray.length < 2 || targetArray.length < 2) {
        throw new Error('Please provide at least 2 values in each array')
      }

      const data = {
        predicted: predictedArray,
        target: targetArray,
        user_id: userId || undefined,
        analysis_name: analysisName || undefined,
      }

      const result = await analysisApi.analyze(data)
      setResults(result)
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Analysis failed')
    } finally {
      setLoading(false)
    }
  }

  const loadExample = () => {
    setPredicted('1.0, 2.5, 3.2, 4.1, 5.0, 3.8, 2.9, 4.5, 5.2, 3.7')
    setTarget('1.2, 2.3, 3.5, 3.9, 4.8, 4.0, 3.1, 4.3, 5.0, 3.9')
    setAnalysisName('Example Analysis')
  }

  const downloadResults = () => {
    if (!results) return
    const json = JSON.stringify(results, null, 2)
    const blob = new Blob([json], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `analysis-${Date.now()}.json`
    a.click()
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="flex justify-between items-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900">Analyze Time Series</h2>
        <div className="flex gap-2">
          <button
            onClick={() => setShowLoadDialog(true)}
            className="btn btn-secondary flex items-center gap-2"
          >
            <FolderOpen size={18} />
            Load Project ({savedProjects.length})
          </button>
          <button
            onClick={() => setShowSaveDialog(true)}
            className="btn btn-secondary flex items-center gap-2"
          >
            <Save size={18} />
            Save Project
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Input Form */}
        <div className="card">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xl font-semibold">Input Data</h3>
            <button
              type="button"
              onClick={restoreAutoSave}
              className="text-xs text-blue-600 hover:text-blue-800"
            >
              Restore Auto-Save
            </button>
          </div>
          <form onSubmit={handleAnalyze} className="space-y-4">
            <div>
              <label className="label">Predicted Values</label>
              <textarea
                className="input font-mono text-sm"
                rows="4"
                value={predicted}
                onChange={(e) => setPredicted(e.target.value)}
                placeholder="1.0, 2.5, 3.2, 4.1, 5.0"
                required
              />
              <p className="text-xs text-gray-500 mt-1">Comma or space separated numbers</p>
            </div>

            <div>
              <label className="label">Target/Observed Values</label>
              <textarea
                className="input font-mono text-sm"
                rows="4"
                value={target}
                onChange={(e) => setTarget(e.target.value)}
                placeholder="1.2, 2.3, 3.5, 3.9, 4.8"
                required
              />
            </div>

            <div>
              <label className="label">User ID (optional)</label>
              <input
                type="text"
                className="input"
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
                placeholder="your-user-id"
              />
            </div>

            <div>
              <label className="label">Analysis Name (optional)</label>
              <input
                type="text"
                className="input"
                value={analysisName}
                onChange={(e) => setAnalysisName(e.target.value)}
                placeholder="My Analysis"
              />
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
                {error}
              </div>
            )}

            <div className="flex space-x-2">
              <button
                type="submit"
                className="btn btn-primary flex-1 flex items-center justify-center space-x-2"
                disabled={loading}
              >
                <Upload size={18} />
                <span>{loading ? 'Analyzing...' : 'Analyze'}</span>
              </button>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={loadExample}
              >
                Load Example
              </button>
            </div>
          </form>
        </div>

        {/* Results */}
        <div className="card">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xl font-semibold">Results</h3>
            {results && (
              <button onClick={downloadResults} className="btn btn-secondary flex items-center space-x-1">
                <Download size={16} />
                <span>Export</span>
              </button>
            )}
          </div>

          {!results && (
            <div className="text-center py-12 text-gray-500">
              Results will appear here after analysis
            </div>
          )}

          {results && (
            <div className="space-y-6">
              {/* Key Metrics */}
              <div className="grid grid-cols-2 gap-4">
                <MetricBox label="RMSE" value={results.RMSE} />
                <MetricBox label="NSC/NSE" value={results.NSC} />
                <MetricBox label="Correlation" value={results.Cor} />
                <MetricBox label="KGE (2009)" value={results.KGE2009} />
                <MetricBox label="R²" value={results.R2} />
                <MetricBox label="PBIAS (%)" value={results.PBIAS} />
              </div>

              {/* More Metrics */}
              <details className="border-t pt-4">
                <summary className="cursor-pointer font-medium text-gray-700 hover:text-primary-600">
                  View All Metrics (28+)
                </summary>
                <div className="mt-4 grid grid-cols-2 gap-2 text-sm">
                  {Object.entries(results)
                    .filter(([key]) => !['Er', 'Po', 'Pu'].includes(key))
                    .map(([key, value]) => (
                      <div key={key} className="flex justify-between py-1 border-b border-gray-100">
                        <span className="text-gray-600">{key}:</span>
                        <span className="font-mono font-semibold">
                          {typeof value === 'number' ? value.toFixed(4) : value}
                        </span>
                      </div>
                    ))}
                </div>
              </details>
            </div>
          )}
        </div>
      </div>

      {/* Visualization */}
      {results && (
        <div className="card mt-8">
          <h3 className="text-xl font-semibold mb-4">Visualization</h3>
          <TimeSeriesChart results={results} />
        </div>
      )}

      {/* Save Dialog */}
      {showSaveDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-semibold mb-4">Save Project</h3>
            <p className="text-sm text-gray-600 mb-4">
              Save your current work to continue later. You can load it anytime.
            </p>
            <input
              type="text"
              placeholder="Project name"
              className="input w-full mb-4"
              defaultValue={analysisName}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  saveCurrentProject(e.target.value)
                }
              }}
              id="project-name-input"
            />
            <div className="flex gap-2">
              <button
                onClick={() => {
                  const name = document.getElementById('project-name-input').value
                  saveCurrentProject(name)
                }}
                className="btn btn-primary flex-1"
              >
                Save
              </button>
              <button
                onClick={() => setShowSaveDialog(false)}
                className="btn btn-secondary flex-1"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Load Dialog */}
      {showLoadDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <h3 className="text-xl font-semibold mb-4">Load Project</h3>

            {savedProjects.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <p>No saved projects yet.</p>
                <p className="text-sm mt-2">Save your current work to start building your library!</p>
              </div>
            ) : (
              <div className="space-y-2">
                {savedProjects.map((project, idx) => (
                  <div
                    key={idx}
                    className="border border-gray-200 rounded-lg p-4 hover:border-blue-500 transition"
                  >
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h4 className="font-semibold text-gray-900">{project.name}</h4>
                        <p className="text-xs text-gray-500">
                          Saved: {new Date(project.savedAt).toLocaleString()}
                        </p>
                      </div>
                      <button
                        onClick={() => deleteProject(project.name)}
                        className="text-red-600 hover:text-red-800 text-sm"
                      >
                        Delete
                      </button>
                    </div>

                    <div className="text-sm text-gray-600 mb-3">
                      <p>Predicted: {project.predicted.substring(0, 50)}{project.predicted.length > 50 ? '...' : ''}</p>
                      <p>Target: {project.target.substring(0, 50)}{project.target.length > 50 ? '...' : ''}</p>
                    </div>

                    <button
                      onClick={() => loadProject(project)}
                      className="btn btn-primary w-full"
                    >
                      Load This Project
                    </button>
                  </div>
                ))}
              </div>
            )}

            <button
              onClick={() => setShowLoadDialog(false)}
              className="btn btn-secondary w-full mt-4"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

function MetricBox({ label, value }) {
  return (
    <div className="border border-gray-200 rounded p-3">
      <p className="text-xs text-gray-600 mb-1">{label}</p>
      <p className="text-xl font-bold text-gray-900">
        {typeof value === 'number' ? value.toFixed(4) : '—'}
      </p>
    </div>
  )
}

function TimeSeriesChart({ results }) {
  // Prepare data for chart
  const data = results.Er.map((error, idx) => ({
    index: idx + 1,
    error: error,
  }))

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="index" label={{ value: 'Time Index', position: 'insideBottom', offset: -5 }} />
        <YAxis label={{ value: 'Error (T - P)', angle: -90, position: 'insideLeft' }} />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="error" stroke="#2563eb" strokeWidth={2} dot={false} name="Error" />
        <Line type="monotone" dataKey={() => 0} stroke="#9ca3af" strokeWidth={1} strokeDasharray="5 5" name="Zero Line" dot={false} />
      </LineChart>
    </ResponsiveContainer>
  )
}
