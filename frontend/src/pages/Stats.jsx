import { useEffect, useState } from 'react'
import { TrendingUp, Users, Activity, Clock } from 'lucide-react'
import { analysisApi } from '../services/api'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function Stats() {
  const [systemStats, setSystemStats] = useState(null)
  const [userStats, setUserStats] = useState(null)
  const [userId, setUserId] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadSystemStats()
  }, [])

  const loadSystemStats = async () => {
    setLoading(true)
    try {
      const stats = await analysisApi.getSystemStats()
      setSystemStats(stats)
    } catch (error) {
      console.error('Failed to load system stats:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadUserStats = async (e) => {
    e?.preventDefault()
    if (!userId) return

    try {
      const stats = await analysisApi.getUserStats(userId)
      setUserStats(stats)
    } catch (error) {
      console.error('Failed to load user stats:', error)
      setUserStats(null)
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
      <h2 className="text-3xl font-bold text-gray-900 mb-8">Statistics Dashboard</h2>

      {/* System Stats */}
      {systemStats && (
        <>
          <h3 className="text-xl font-semibold mb-4">System Overview</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <StatsCard
              icon={<Activity className="text-primary-600" size={24} />}
              label="Total Analyses"
              value={systemStats.total_analyses}
              color="blue"
            />
            <StatsCard
              icon={<Clock className="text-green-600" size={24} />}
              label="Last 24 Hours"
              value={systemStats.analyses_last_24h}
              color="green"
            />
            <StatsCard
              icon={<Users className="text-purple-600" size={24} />}
              label="Unique Users"
              value={systemStats.unique_users}
              color="purple"
            />
            <StatsCard
              icon={<TrendingUp className="text-orange-600" size={24} />}
              label="Active Sessions"
              value={systemStats.total_sessions}
              color="orange"
            />
          </div>

          {/* Average Metrics */}
          <div className="card mb-8">
            <h4 className="text-lg font-semibold mb-4">Average Metrics (All Time)</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <AvgMetric label="RMSE" value={systemStats.average_metrics.rmse} />
              <AvgMetric label="NSC/NSE" value={systemStats.average_metrics.nsc} />
              <AvgMetric label="Correlation" value={systemStats.average_metrics.correlation} />
              <AvgMetric label="KGE (2009)" value={systemStats.average_metrics.kge2009} />
            </div>
          </div>

          {/* Top Users */}
          {systemStats.top_users.length > 0 && (
            <div className="card mb-8">
              <h4 className="text-lg font-semibold mb-4">Top Users</h4>
              <TopUsersChart users={systemStats.top_users} />
            </div>
          )}
        </>
      )}

      {/* User Stats Lookup */}
      <div className="card">
        <h3 className="text-xl font-semibold mb-4">User Statistics</h3>
        <form onSubmit={loadUserStats} className="mb-6">
          <div className="flex gap-3">
            <input
              type="text"
              className="input flex-1"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              placeholder="Enter user ID"
            />
            <button type="submit" className="btn btn-primary">
              Load Stats
            </button>
          </div>
        </form>

        {userStats && (
          <div className="space-y-6">
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div className="border-l-4 border-blue-500 pl-4">
                <p className="text-sm text-gray-600">Total Analyses</p>
                <p className="text-2xl font-bold text-gray-900">{userStats.total_analyses}</p>
              </div>
              <div className="border-l-4 border-green-500 pl-4">
                <p className="text-sm text-gray-600">Recent (30 days)</p>
                <p className="text-2xl font-bold text-gray-900">{userStats.recent_analyses_30d}</p>
              </div>
              <div className="border-l-4 border-purple-500 pl-4">
                <p className="text-sm text-gray-600">User ID</p>
                <p className="text-lg font-mono text-gray-900">{userStats.user_id}</p>
              </div>
            </div>

            {/* User Average Metrics */}
            <div>
              <h5 className="font-medium mb-3">Average Metrics</h5>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <AvgMetric label="RMSE" value={userStats.average_metrics.rmse} />
                <AvgMetric label="NSC/NSE" value={userStats.average_metrics.nsc} />
                <AvgMetric label="Correlation" value={userStats.average_metrics.correlation} />
                <AvgMetric label="KGE (2009)" value={userStats.average_metrics.kge2009} />
              </div>
            </div>

            {/* Recent Analyses */}
            {userStats.recent_analyses.length > 0 && (
              <div>
                <h5 className="font-medium mb-3">Recent Analyses</h5>
                <div className="space-y-2">
                  {userStats.recent_analyses.map((analysis) => (
                    <div key={analysis.id} className="flex justify-between items-center p-3 bg-gray-50 rounded">
                      <div>
                        <p className="font-medium">{analysis.name || `Analysis #${analysis.id}`}</p>
                        <p className="text-xs text-gray-600">
                          {new Date(analysis.timestamp).toLocaleDateString()} • {analysis.n_points} points
                        </p>
                      </div>
                      <div className="flex gap-3 text-sm">
                        <span className="text-gray-600">NSC: <strong>{analysis.nsc?.toFixed(3)}</strong></span>
                        <span className="text-gray-600">RMSE: <strong>{analysis.rmse?.toFixed(3)}</strong></span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

function StatsCard({ icon, label, value, color }) {
  return (
    <div className="card flex items-center space-x-4">
      <div className="flex-shrink-0">{icon}</div>
      <div>
        <p className="text-sm text-gray-600">{label}</p>
        <p className="text-3xl font-bold text-gray-900">{value}</p>
      </div>
    </div>
  )
}

function AvgMetric({ label, value }) {
  return (
    <div className="text-center p-3 bg-blue-50 rounded">
      <p className="text-xs text-blue-600 font-medium mb-1">{label}</p>
      <p className="text-xl font-bold text-blue-900">
        {value ? value.toFixed(4) : '—'}
      </p>
    </div>
  )
}

function TopUsersChart({ users }) {
  const data = users.map(u => ({
    user: u.user_id.substring(0, 10),
    analyses: u.analysis_count
  }))

  return (
    <ResponsiveContainer width="100%" height={250}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="user" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Bar dataKey="analyses" fill="#2563eb" name="Analyses" />
      </BarChart>
    </ResponsiveContainer>
  )
}
