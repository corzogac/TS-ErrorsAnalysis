import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Activity, TrendingUp, Users, BarChart3, Layers, Eye, Wand2, History, ArrowRight } from 'lucide-react'
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
        <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-2">
          Compute 28+ error metrics for predicted vs. observed time series.
        </p>
        <p className="text-lg text-gray-500 max-w-2xl mx-auto">
          Includes NSE, KGE, correlation, persistence baselines, batch processing, and advanced visualizations
        </p>
      </div>

      {/* Stats Cards */}
      {systemStats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <StatCard
            icon={<Activity className="text-primary-600" size={24} />}
            label="Total Analyses"
            value={systemStats.total_analyses}
          />
          <StatCard
            icon={<TrendingUp className="text-green-600" size={24} />}
            label="Last 24 Hours"
            value={systemStats.analyses_last_24h}
          />
          <StatCard
            icon={<Users className="text-blue-600" size={24} />}
            label="Unique Users"
            value={systemStats.unique_users}
          />
          <StatCard
            icon={<BarChart3 className="text-purple-600" size={24} />}
            label="Active Sessions"
            value={systemStats.total_sessions}
          />
        </div>
      )}

      {/* Main Features Navigation */}
      <div className="mb-12">
        <h3 className="text-2xl font-bold text-gray-900 mb-6">Get Started</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <NavigationCard
            to="/analyze"
            icon={<TrendingUp size={32} />}
            title="Analyze"
            description="Single time series analysis with 28+ metrics"
            color="blue"
            features={['Upload data', 'Instant results', 'Save projects', 'Export metrics']}
          />

          <NavigationCard
            to="/batch"
            icon={<Layers size={32} />}
            title="Batch Analysis"
            description="Compare multiple models side-by-side"
            color="green"
            features={['Multi-series', 'Rankings', 'CSV/JSON export', 'Visual comparison']}
          />

          <NavigationCard
            to="/visualize"
            icon={<Eye size={32} />}
            title="Advanced Visualizations"
            description="Interactive diagnostic plots with Plotly"
            color="purple"
            features={['3D surfaces', 'Residual analysis', 'Q-Q plots', 'ACF/PACF']}
          />

          <NavigationCard
            to="/tools"
            icon={<Wand2 size={32} />}
            title="Time Series Tools"
            description="Process and transform your data"
            color="orange"
            features={['Interpolate', 'Smooth', 'Decompose', 'Detect outliers']}
          />

          <NavigationCard
            to="/history"
            icon={<History size={32} />}
            title="History"
            description="Browse past analyses and results"
            color="indigo"
            features={['View all runs', 'Filter by user', 'Reload data', 'Track progress']}
          />

          <NavigationCard
            to="/stats"
            icon={<BarChart3 size={32} />}
            title="Statistics"
            description="System-wide analytics and insights"
            color="pink"
            features={['User stats', 'Trends', 'Performance', 'Aggregates']}
          />
        </div>
      </div>

      {/* Average Metrics */}
      {systemStats?.average_metrics && (
        <div className="card mb-12">
          <h3 className="text-xl font-semibold mb-4">Average Metrics Across All Analyses</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <MetricDisplay label="RMSE" value={systemStats.average_metrics.rmse} />
            <MetricDisplay label="NSC/NSE" value={systemStats.average_metrics.nsc} />
            <MetricDisplay label="Correlation" value={systemStats.average_metrics.correlation} />
            <MetricDisplay label="KGE (2009)" value={systemStats.average_metrics.kge2009} />
          </div>
        </div>
      )}

      {/* Key Features Grid */}
      <div className="mb-12">
        <h3 className="text-2xl font-bold text-gray-900 mb-6">Why Choose TS-ErrorsAnalysis?</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <FeatureHighlight
            title="Comprehensive Metrics"
            description="28+ error metrics covering all aspects of model performance"
            items={['Basic errors (RMSE, MAE, SSE)', 'Model skill (NSE, R², Correlation)', 'Bias metrics (PBIAS, sMAPE)', 'Hydrology-specific (KGE, d, d1)', 'Persistence baselines']}
          />
          <FeatureHighlight
            title="Advanced Analysis"
            description="Professional-grade tools for deep insights"
            items={['Batch processing', '3D interactive plots', 'Residual diagnostics', 'Autocorrelation analysis', 'Project management']}
          />
          <FeatureHighlight
            title="Easy & Fast"
            description="Designed for researchers and engineers"
            items={['Instant analysis', 'No coding required', 'Export to CSV/JSON', 'Browser-based', 'Free to use']}
          />
        </div>
      </div>
    </div>
  )
}

function StatCard({ icon, label, value }) {
  return (
    <div className="card flex items-center space-x-4 hover:shadow-lg transition-shadow">
      <div className="flex-shrink-0">{icon}</div>
      <div>
        <p className="text-sm text-gray-600">{label}</p>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
      </div>
    </div>
  )
}

function NavigationCard({ to, icon, title, description, color, features }) {
  const colorClasses = {
    blue: 'from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700',
    green: 'from-green-500 to-green-600 hover:from-green-600 hover:to-green-700',
    purple: 'from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700',
    orange: 'from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700',
    indigo: 'from-indigo-500 to-indigo-600 hover:from-indigo-600 hover:to-indigo-700',
    pink: 'from-pink-500 to-pink-600 hover:from-pink-600 hover:to-pink-700',
  }

  return (
    <Link
      to={to}
      className="block group"
    >
      <div className="card hover:shadow-xl transition-all duration-300 border-2 border-transparent hover:border-gray-300 h-full">
        <div className={`w-16 h-16 rounded-lg bg-gradient-to-br ${colorClasses[color]} flex items-center justify-center text-white mb-4 group-hover:scale-110 transition-transform`}>
          {icon}
        </div>

        <h4 className="text-xl font-bold text-gray-900 mb-2 group-hover:text-primary-600 transition-colors">
          {title}
        </h4>

        <p className="text-gray-600 mb-4 text-sm">
          {description}
        </p>

        <ul className="space-y-1.5 mb-4">
          {features.map((feature, idx) => (
            <li key={idx} className="text-sm text-gray-700 flex items-center">
              <ArrowRight size={14} className="text-gray-400 mr-2 flex-shrink-0" />
              {feature}
            </li>
          ))}
        </ul>

        <div className="flex items-center text-primary-600 font-medium text-sm group-hover:text-primary-700">
          Open {title} <ArrowRight size={16} className="ml-1 group-hover:translate-x-1 transition-transform" />
        </div>
      </div>
    </Link>
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

function FeatureHighlight({ title, description, items }) {
  return (
    <div className="card bg-gradient-to-br from-gray-50 to-white border-2 border-gray-100">
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600 text-sm mb-4">{description}</p>
      <ul className="space-y-2">
        {items.map((item, idx) => (
          <li key={idx} className="text-sm text-gray-700 flex items-start">
            <span className="text-primary-600 mr-2 mt-0.5">✓</span>
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}
