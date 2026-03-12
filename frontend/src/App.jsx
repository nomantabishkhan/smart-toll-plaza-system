import { useState, useEffect, useCallback } from 'react';
import { fetchLiveStats } from './api';
import { useWebSocket } from './hooks/useWebSocket';
import StatsBar from './components/StatsBar';
import VehicleClassCards from './components/VehicleClassCards';
import HourlyChart from './components/HourlyChart';
import EventFeed from './components/EventFeed';
import VideoUpload from './components/VideoUpload';

function App() {
  const [stats, setStats] = useState({
    total: 0,
    revenue_estimated: 0,
    by_class: [],
  });

  const { lastEvent, connected } = useWebSocket();

  // Fetch stats on mount + periodically
  const refreshStats = useCallback(() => {
    fetchLiveStats()
      .then(setStats)
      .catch(console.error);
  }, []);

  useEffect(() => {
    refreshStats();
    const id = setInterval(refreshStats, 5_000);
    return () => clearInterval(id);
  }, [refreshStats]);

  // Also refresh when a WebSocket event arrives
  useEffect(() => {
    if (lastEvent?.type === 'vehicle_detected') {
      refreshStats();
    }
  }, [lastEvent, refreshStats]);

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🛣️</span>
            <div>
              <h1 className="text-xl font-bold text-gray-900">
                Smart Toll Plaza System
              </h1>
              <p className="text-xs text-gray-500">
                Real-Time Vehicle Detection &amp; Classification
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span
              className={`inline-block h-2.5 w-2.5 rounded-full ${
                connected ? 'bg-green-500 animate-pulse' : 'bg-red-500'
              }`}
            />
            <span className="text-xs text-gray-500">
              {connected ? 'Live' : 'Offline'}
            </span>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 py-6 space-y-6">
        <StatsBar
          total={stats.total}
          revenue={stats.revenue_estimated}
          connected={connected}
        />

        <VehicleClassCards byClass={stats.by_class} />

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <HourlyChart />
          <EventFeed latestWsEvent={lastEvent} />
        </div>

        <VideoUpload />
      </main>

      {/* Footer */}
      <footer className="text-center text-xs text-gray-400 py-6">
        Smart Toll Plaza System &copy; {new Date().getFullYear()} — The Islamia
        University of Bahawalpur
      </footer>
    </div>
  );
}

export default App;
