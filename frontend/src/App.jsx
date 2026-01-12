import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import { BarChart3, Home, History, TrendingUp, Wand2, Layers, Eye } from 'lucide-react'
import Dashboard from './pages/Dashboard'
import Analyze from './pages/Analyze'
import HistoryPage from './pages/HistoryPage'
import Stats from './pages/Stats'
import Tools from './pages/Tools'
import Batch from './pages/Batch'
import Visualize from './pages/Visualize'

function App() {
  return (
    <Router>
      <div className="min-h-screen flex flex-col">
        {/* Header */}
        <header className="bg-white shadow-sm border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center space-x-3">
                <BarChart3 className="h-8 w-8 text-primary-600" />
                <div>
                  <h1 className="text-xl font-bold text-gray-900">TS-ErrorsAnalysis</h1>
                  <p className="text-xs text-gray-500">Hydrological Time Series Analysis</p>
                </div>
              </div>
              <nav className="flex space-x-4">
                <NavLink to="/" icon={<Home size={18} />}>Dashboard</NavLink>
                <NavLink to="/analyze" icon={<TrendingUp size={18} />}>Analyze</NavLink>
                <NavLink to="/batch" icon={<Layers size={18} />}>Batch</NavLink>
                <NavLink to="/visualize" icon={<Eye size={18} />}>Visualize</NavLink>
                <NavLink to="/tools" icon={<Wand2 size={18} />}>Tools</NavLink>
                <NavLink to="/history" icon={<History size={18} />}>History</NavLink>
                <NavLink to="/stats" icon={<BarChart3 size={18} />}>Stats</NavLink>
              </nav>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/analyze" element={<Analyze />} />
            <Route path="/batch" element={<Batch />} />
            <Route path="/visualize" element={<Visualize />} />
            <Route path="/tools" element={<Tools />} />
            <Route path="/history" element={<HistoryPage />} />
            <Route path="/stats" element={<Stats />} />
          </Routes>
        </main>

        {/* Footer */}
        <footer className="bg-white border-t border-gray-200 mt-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <p className="text-center text-sm text-gray-500">
              TS-ErrorsAnalysis v1.0 | MIT License | IHE Delft
            </p>
          </div>
        </footer>
      </div>
    </Router>
  )
}

function NavLink({ to, icon, children }) {
  return (
    <Link
      to={to}
      className="flex items-center space-x-1 px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-100 hover:text-primary-600 transition-colors"
    >
      {icon}
      <span>{children}</span>
    </Link>
  )
}

export default App
