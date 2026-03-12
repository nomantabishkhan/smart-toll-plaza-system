import { Routes, Route, NavLink } from 'react-router-dom';
import { LayoutDashboard, BarChart3, Upload as UploadIcon, Radar } from 'lucide-react';
import { useWebSocket } from './hooks/useWebSocket';
import Dashboard from './pages/Dashboard';
import Analytics from './pages/Analytics';
import Upload from './pages/Upload';

const NAV = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/analytics', label: 'Analytics', icon: BarChart3 },
  { to: '/upload', label: 'Upload', icon: UploadIcon },
];

function App() {
  const { lastEvent, connected } = useWebSocket();

  return (
    <div className="min-h-screen flex bg-gray-50">
      {/* Sidebar */}
      <aside className="w-56 bg-gray-900 text-white flex flex-col shrink-0">
        <div className="px-5 py-6 border-b border-gray-700">
          <h1 className="text-lg font-bold leading-tight flex items-center gap-2">
            <Radar className="w-5 h-5 text-blue-400" />
            Smart Toll Plaza
          </h1>
          <p className="text-[11px] text-gray-400 mt-1">Vehicle Detection System</p>
        </div>
        <nav className="flex-1 py-4 space-y-1 px-3">
          {NAV.map((n) => (
            <NavLink
              key={n.to}
              to={n.to}
              end={n.to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                }`
              }
            >
              <n.icon className="w-4 h-4" />
              {n.label}
            </NavLink>
          ))}
        </nav>
        <div className="px-5 py-4 border-t border-gray-700 text-xs text-gray-500">
          <div className="flex items-center gap-2">
            <span
              className={`inline-block h-2 w-2 rounded-full ${
                connected ? 'bg-green-400 animate-pulse' : 'bg-red-500'
              }`}
            />
            {connected ? 'WebSocket Live' : 'WebSocket Offline'}
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        <main className="flex-1 p-6 overflow-y-auto">
          <Routes>
            <Route path="/" element={<Dashboard lastEvent={lastEvent} connected={connected} />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/upload" element={<Upload />} />
          </Routes>
        </main>
        <footer className="text-center text-xs text-gray-400 py-4 border-t border-gray-200">
          Smart Toll Plaza System &copy; {new Date().getFullYear()} — The Islamia University of Bahawalpur
        </footer>
      </div>
    </div>
  );
}

export default App;

