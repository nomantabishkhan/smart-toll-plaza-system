import { useState, useEffect, useCallback } from 'react';
import { fetchLiveStats } from '../api';
import StatsBar from '../components/StatsBar';
import VehicleClassCards from '../components/VehicleClassCards';
import HourlyChart from '../components/HourlyChart';
import EventFeed from '../components/EventFeed';

export default function Dashboard({ lastEvent, connected }) {
  const [stats, setStats] = useState({
    total: 0,
    revenue_estimated: 0,
    by_class: [],
  });

  const refreshStats = useCallback(() => {
    fetchLiveStats().then(setStats).catch(console.error);
  }, []);

  useEffect(() => {
    refreshStats();
    const id = setInterval(refreshStats, 5_000);
    return () => clearInterval(id);
  }, [refreshStats]);

  // Refresh when a WebSocket detection arrives
  useEffect(() => {
    if (lastEvent?.type === 'vehicle_detected') {
      refreshStats();
    }
  }, [lastEvent, refreshStats]);

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Live Dashboard</h2>

      <StatsBar total={stats.total} revenue={stats.revenue_estimated} connected={connected} />

      <VehicleClassCards byClass={stats.by_class} />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <HourlyChart />
        <EventFeed latestWsEvent={lastEvent} />
      </div>
    </div>
  );
}
