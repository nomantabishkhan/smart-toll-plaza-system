import { useState, useEffect } from 'react';
import { fetchHourlyStats } from '../api';

export default function HourlyChart() {
  const [hourly, setHourly] = useState(Array(24).fill(0));

  useEffect(() => {
    fetchHourlyStats()
      .then((data) => setHourly(data.hourly))
      .catch(console.error);

    const id = setInterval(() => {
      fetchHourlyStats()
        .then((data) => setHourly(data.hourly))
        .catch(console.error);
    }, 30_000);
    return () => clearInterval(id);
  }, []);

  const max = Math.max(...hourly, 1);

  return (
    <div className="rounded-xl bg-white shadow border border-gray-200 p-5">
      <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-4">
        Hourly Traffic
      </h3>
      <div className="flex items-end gap-1 h-40">
        {hourly.map((count, hour) => {
          const pct = (count / max) * 100;
          const now = new Date().getHours();
          const isCurrent = hour === now;
          return (
            <div
              key={hour}
              className="flex-1 flex flex-col items-center group relative"
            >
              {/* Tooltip */}
              <span className="absolute -top-6 hidden group-hover:block text-xs bg-gray-800 text-white rounded px-2 py-0.5 whitespace-nowrap">
                {hour}:00 — {count}
              </span>
              <div
                className={`w-full rounded-t transition-all ${
                  isCurrent
                    ? 'bg-blue-500'
                    : count > 0
                      ? 'bg-blue-300'
                      : 'bg-gray-200'
                }`}
                style={{ height: `${Math.max(pct, 2)}%` }}
              />
              {hour % 3 === 0 && (
                <span className="text-[10px] text-gray-400 mt-1">{hour}</span>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
