export default function StatsBar({ total, revenue, connected }) {
  return (
    <div className="flex flex-wrap gap-4 mb-6">
      {/* Total vehicles today */}
      <div className="flex-1 min-w-[180px] rounded-xl bg-white shadow p-5 border border-gray-200">
        <p className="text-xs uppercase tracking-wide text-gray-500">
          Vehicles Today
        </p>
        <p className="text-3xl font-bold text-gray-900 mt-1">{total}</p>
      </div>

      {/* Estimated revenue */}
      <div className="flex-1 min-w-[180px] rounded-xl bg-white shadow p-5 border border-gray-200">
        <p className="text-xs uppercase tracking-wide text-gray-500">
          Est. Revenue
        </p>
        <p className="text-3xl font-bold text-gray-900 mt-1">
          ₹{revenue.toLocaleString()}
        </p>
      </div>

      {/* WebSocket status */}
      <div className="flex-1 min-w-[180px] rounded-xl bg-white shadow p-5 border border-gray-200">
        <p className="text-xs uppercase tracking-wide text-gray-500">
          Live Feed
        </p>
        <div className="flex items-center gap-2 mt-2">
          <span
            className={`inline-block h-3 w-3 rounded-full ${
              connected ? 'bg-green-500 animate-pulse' : 'bg-red-500'
            }`}
          />
          <span className="text-sm font-medium text-gray-700">
            {connected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>
    </div>
  );
}
