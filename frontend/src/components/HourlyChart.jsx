import { useState, useEffect } from 'react';
import { fetchHourlyStats } from '../api';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

export default function HourlyChart() {
  const [data, setData] = useState([]);

  useEffect(() => {
    const load = () =>
      fetchHourlyStats()
        .then((d) =>
          setData(
            d.hourly.map((count, h) => ({
              hour: `${String(h).padStart(2, '0')}:00`,
              vehicles: count,
            })),
          ),
        )
        .catch(console.error);

    load();
    const id = setInterval(load, 30_000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="rounded-xl bg-white shadow border border-gray-200 p-5">
      <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-4">
        Hourly Traffic
      </h3>
      <ResponsiveContainer width="100%" height={220}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="colorVehicles" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="hour" tick={{ fontSize: 10 }} interval={2} />
          <YAxis allowDecimals={false} tick={{ fontSize: 10 }} />
          <Tooltip />
          <Area
            type="monotone"
            dataKey="vehicles"
            stroke="#3b82f6"
            fill="url(#colorVehicles)"
            strokeWidth={2}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

