import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Activity, TrendingUp, Users, BarChart3 } from 'lucide-react'
import { analysisApi } from '../services/api'

export default function Dashboard() {
  const [systemStats, setSystemStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      const stats = await analysisApi.getSystemStats()
      setSystemStats(stats)
    } catch (error) {
      console.error('Failed to load stats:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">Loading...</div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      {/* Hero Section */}
      <div className="text-center mb-12">
        <h2 className="text-4xl font-bold text-gray-900 mb-4">
          Hydrological Time Series Analysis
        </h2>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Compute 28+ error metrics for predicted vs. observed time series.
          Includes NSE, KGE, correlation, persistence baselines, and more.
        </p>
        <div className="mt-8">
          <Link to="/analyze" className="btn btn-primary text-lg px-8 py-3">
            Start Analysis
          </Link>
        </div>
      </div>

      {/* Stats Cards */}
      {systemStats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <StatCard
            icon={<Activity className="text-primary-600" />}
            label="Total Analyses"
            value={systemStats.total_analyses}
          />
          <StatCard
            icon={<TrendingUp className="text-green-600" />}
            label="Last 24 Hours"
            value={systemStats.analyses_last_24h}
          />
          <StatCard
            icon={<Users className="text-blue-600" />}
            label="Unique Users"
            value={systemStats.unique_users}
          />
          <StatCard
            icon={<BarChart3 className="text-purple-600" />}
            label="Active Sessions"
            value={systemStats.total_sessions}
          />
        </div>
      )}

      {/* Average Metrics */}
      {systemStats?.average_metrics && (
        <div className="card mb-12">
          <h3 className="text-xl font-semibold mb-4">Average Metrics (All Analyses)</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <MetricDisplay label="RMSE" value={systemStats.average_metrics.rmse} />
            <MetricDisplay label="NSC/NSE" value={systemStats.average_metrics.nsc} />
            <MetricDisplay label="Correlation" value={systemStats.average_metrics.correlation} />
            <MetricDisplay label="KGE (2009)" value={systemStats.average_metrics.kge2009} />
          </div>
        </div>
      )}

      {/* Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <FeatureCard
          title="Error Metrics"
          description="RMSE, MAE, NSE, correlation, and 24+ other metrics"
          items={['Basic errors', 'Model skill', 'Bias metrics', 'Persistence']}
        />
        <FeatureCard
          title="Hydrology-Specific"
          description="Metrics designed for hydrological applications"
          items={['KGE (2009, 2012)', 'Index of Agreement', 'PBIAS', 'sMAPE']}
        />
        <FeatureCard
          title="Easy to Use"
          description="Upload data, get results instantly"
          items={['CSV/JSON input', 'Interactive charts', 'Export results', 'API access']}
        />
      </div>
    </div>
  )
}

function StatCard({ icon, label, value }) {
  return (
    <div className="card flex items-center space-x-4">
      <div className="flex-shrink-0">{icon}</div>
      <div>
        <p className="text-sm text-gray-600">{label}</p>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
      </div>
    </div>
  )
}

function MetricDisplay({ label, value }) {
  return (
    <div className="text-center">
      <p className="text-sm text-gray-600 mb-1">{label}</p>
      <p className="text-2xl font-semibold text-gray-900">
        {value ? value.toFixed(4) : '—'}
      </p>
    </div>
  )
}

function FeatureCard({ title, description, items }) {
  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600 text-sm mb-4">{description}</p>
      <ul className="space-y-1">
        {items.map((item, idx) => (
          <li key={idx} className="text-sm text-gray-700 flex items-center">
            <span className="text-primary-600 mr-2">•</span>
            {item}
          </li>
        ))}
      </ul>
    </div>
  )
}
