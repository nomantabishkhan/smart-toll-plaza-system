import { useState, useEffect } from 'react';
import { fetchHourlyStats, fetchLiveStats } from '../api';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts';

const COLORS = [
  '#f59e0b', '#3b82f6', '#22c55e', '#a855f7',
  '#ef4444', '#6366f1', '#f97316', '#14b8a6',
];

export default function Analytics() {
  const [hourly, setHourly] = useState([]);
  const [byClass, setByClass] = useState([]);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    fetchHourlyStats()
      .then((d) => {
        const mapped = d.hourly.map((count, h) => ({
          hour: `${String(h).padStart(2, '0')}:00`,
          vehicles: count,
        }));
        setHourly(mapped);
      })
      .catch(console.error);

    fetchLiveStats()
      .then((d) => {
        setTotal(d.total);
        setByClass(
          d.by_class.map((c) => ({
            name: c.vehicle_class__class_name,
            value: c.count,
          })),
        );
      })
      .catch(console.error);
  }, []);

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Analytics</h2>

      {/* Hourly traffic bar chart */}
      <div className="rounded-xl bg-white shadow border border-gray-200 p-6">
        <h3 className="text-sm font-semibold text-gray-600 uppercase tracking-wide mb-4">
          Hourly Vehicle Traffic — Today
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={hourly}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="hour" tick={{ fontSize: 11 }} interval={2} />
            <YAxis allowDecimals={false} />
            <Tooltip />
            <Bar dataKey="vehicles" fill="#3b82f6" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Per-class breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pie chart */}
        <div className="rounded-xl bg-white shadow border border-gray-200 p-6">
          <h3 className="text-sm font-semibold text-gray-600 uppercase tracking-wide mb-4">
            Vehicle Class Distribution
          </h3>
          {total === 0 ? (
            <p className="text-sm text-gray-400 text-center py-12">No data yet</p>
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={byClass}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label={({ name, percent }) =>
                    `${name} ${(percent * 100).toFixed(0)}%`
                  }
                >
                  {byClass.map((_, i) => (
                    <Cell key={i} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Table */}
        <div className="rounded-xl bg-white shadow border border-gray-200 p-6">
          <h3 className="text-sm font-semibold text-gray-600 uppercase tracking-wide mb-4">
            Breakdown Table
          </h3>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b">
                <th className="pb-2">Class</th>
                <th className="pb-2 text-right">Count</th>
                <th className="pb-2 text-right">Share</th>
              </tr>
            </thead>
            <tbody>
              {byClass.map((c, i) => (
                <tr key={c.name} className="border-b border-gray-100">
                  <td className="py-2 flex items-center gap-2">
                    <span
                      className="inline-block h-3 w-3 rounded-sm"
                      style={{ backgroundColor: COLORS[i % COLORS.length] }}
                    />
                    {c.name}
                  </td>
                  <td className="py-2 text-right font-medium">{c.value}</td>
                  <td className="py-2 text-right text-gray-400">
                    {total > 0 ? ((c.value / total) * 100).toFixed(1) : 0}%
                  </td>
                </tr>
              ))}
            </tbody>
            <tfoot>
              <tr className="font-semibold">
                <td className="pt-3">Total</td>
                <td className="pt-3 text-right">{total}</td>
                <td className="pt-3 text-right">100%</td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
    </div>
  );
}
