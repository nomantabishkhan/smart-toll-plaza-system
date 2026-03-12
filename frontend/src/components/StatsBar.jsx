import { Car, IndianRupee, Wifi, WifiOff } from 'lucide-react';

export default function StatsBar({ total, revenue, connected }) {
  const cards = [
    {
      label: 'Vehicles Today',
      value: total,
      icon: <Car className="w-5 h-5 text-blue-500" />,
      color: 'border-blue-400',
    },
    {
      label: 'Est. Revenue',
      value: `₹${Number(revenue).toLocaleString()}`,
      icon: <IndianRupee className="w-5 h-5 text-green-500" />,
      color: 'border-green-400',
    },
    {
      label: 'Live Feed',
      value: connected ? 'Connected' : 'Disconnected',
      icon: connected
        ? <Wifi className="w-5 h-5 text-green-500" />
        : <WifiOff className="w-5 h-5 text-red-500" />,
      color: connected ? 'border-green-400' : 'border-red-400',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
      {cards.map((c) => (
        <div
          key={c.label}
          className={`rounded-xl bg-white shadow border-l-4 ${c.color} p-5`}
        >
          <p className="text-xs uppercase tracking-wide text-gray-500">{c.label}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1 flex items-center gap-2">
            {c.icon}
            {c.value}
          </p>
        </div>
      ))}
    </div>
  );
}
