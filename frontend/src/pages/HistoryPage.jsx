import { useEffect, useState } from 'react'
import { Clock, User, FileText } from 'lucide-react'
import { analysisApi } from '../services/api'

export default function HistoryPage() {
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const [userId, setUserId] = useState('')
  const [limit, setLimit] = useState(20)

  useEffect(() => {
    loadHistory()
  }, [])

  const loadHistory = async () => {
    setLoading(true)
    try {
      const params = {}
      if (userId) params.user_id = userId
      params.limit = limit
      const data = await analysisApi.getHistory(params)
      setHistory(data)
    } catch (error) {
      console.error('Failed to load history:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h2 className="text-3xl font-bold text-gray-900 mb-8">Analysis History</h2>

      {/* Filters */}
      <div className="card mb-6">
        <div className="flex gap-4 items-end">
          <div className="flex-1">
            <label className="label">Filter by User ID</label>
            <input
              type="text"
              className="input"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              placeholder="Enter user ID"
            />
          </div>
          <div className="w-32">
            <label className="label">Limit</label>
            <select className="input" value={limit} onChange={(e) => setLimit(Number(e.target.value))}>
              <option value={10}>10</option>
              <option value={20}>20</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
          </div>
          <button onClick={loadHistory} className="btn btn-primary">
            Apply Filters
          </button>
        </div>
      </div>

      {/* History List */}
      {loading ? (
        <div className="text-center py-12">Loading...</div>
      ) : history.length === 0 ? (
        <div className="card text-center py-12 text-gray-500">
          No analysis history found
        </div>
      ) : (
        <div className="space-y-4">
          {history.map((record) => (
            <HistoryCard key={record.id} record={record} />
          ))}
        </div>
      )}
    </div>
  )
}

function HistoryCard({ record }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <div className="card hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <div className="flex items-center space-x-3 mb-2">
            <FileText className="text-primary-600" size={20} />
            <h3 className="font-semibold text-lg">
              {record.name || `Analysis #${record.id}`}
            </h3>
          </div>

          <div className="flex flex-wrap gap-4 text-sm text-gray-600 mb-3">
            <div className="flex items-center space-x-1">
              <Clock size={14} />
              <span>{new Date(record.timestamp).toLocaleString()}</span>
            </div>
            <div className="flex items-center space-x-1">
              <User size={14} />
              <span>{record.n_points} data points</span>
            </div>
          </div>

          {/* Key Metrics */}
          <div className="grid grid-cols-4 gap-4 mb-3">
            <MetricPill label="RMSE" value={record.rmse} />
            <MetricPill label="NSC" value={record.nsc} />
            <MetricPill label="Correlation" value={record.correlation} />
            <MetricPill label="KGE" value={record.kge2009} />
          </div>

          {/* Full Metrics (Expandable) */}
          {expanded && record.metrics && (
            <div className="mt-4 p-4 bg-gray-50 rounded-lg">
              <h4 className="font-medium mb-2">All Metrics:</h4>
              <div className="grid grid-cols-3 gap-2 text-sm">
                {Object.entries(record.metrics)
                  .filter(([key]) => !['Er'].includes(key))
                  .map(([key, value]) => (
                    <div key={key} className="flex justify-between">
                      <span className="text-gray-600">{key}:</span>
                      <span className="font-mono font-semibold">
                        {typeof value === 'number' ? value.toFixed(4) : '—'}
                      </span>
                    </div>
                  ))}
              </div>
            </div>
          )}
        </div>

        <button
          onClick={() => setExpanded(!expanded)}
          className="btn btn-secondary text-sm ml-4"
        >
          {expanded ? 'Hide Details' : 'Show Details'}
        </button>
      </div>
    </div>
  )
}

function MetricPill({ label, value }) {
  return (
    <div className="bg-blue-50 rounded px-3 py-1">
      <p className="text-xs text-blue-600 font-medium">{label}</p>
      <p className="text-sm font-bold text-blue-900">
        {typeof value === 'number' ? value.toFixed(3) : '—'}
      </p>
    </div>
  )
}
