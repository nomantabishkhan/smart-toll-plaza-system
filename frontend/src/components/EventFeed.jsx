import { useState, useEffect, useRef } from 'react';
import { fetchRecentEvents } from '../api';

function timeAgo(isoString) {
  const diff = Math.floor((Date.now() - new Date(isoString).getTime()) / 1000);
  if (diff < 5) return 'just now';
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  return `${Math.floor(diff / 3600)}h ago`;
}

const CLASS_DOT_COLORS = {
  Auto: 'bg-yellow-500',
  Bus: 'bg-blue-500',
  Car: 'bg-green-500',
  LCV: 'bg-purple-500',
  Motorcycle: 'bg-red-500',
  Multiaxle: 'bg-indigo-500',
  Tractor: 'bg-orange-500',
  Truck: 'bg-teal-500',
};

export default function EventFeed({ latestWsEvent }) {
  const [events, setEvents] = useState([]);
  const prevRef = useRef(null);

  useEffect(() => {
    fetchRecentEvents(30).then(setEvents).catch(console.error);
  }, []);

  useEffect(() => {
    if (
      latestWsEvent &&
      latestWsEvent.type === 'vehicle_detected' &&
      latestWsEvent !== prevRef.current
    ) {
      prevRef.current = latestWsEvent;
      const ev = {
        id: crypto.randomUUID(),
        vehicle_class: latestWsEvent.data.vehicle_class,
        confidence: latestWsEvent.data.confidence,
        booth: latestWsEvent.data.booth,
        timestamp: latestWsEvent.data.timestamp || new Date().toISOString(),
      };
      setEvents((prev) => [ev, ...prev].slice(0, 100));
    }
  }, [latestWsEvent]);

  return (
    <div className="rounded-xl bg-white shadow border border-gray-200 overflow-hidden">
      <div className="px-5 py-3 border-b border-gray-200 bg-gray-50 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">
          Recent Crossings
        </h3>
        <span className="text-xs text-gray-400">{events.length} events</span>
      </div>
      <div className="max-h-96 overflow-y-auto divide-y divide-gray-100">
        {events.length === 0 && (
          <p className="p-5 text-sm text-gray-400 text-center">No crossings yet today</p>
        )}
        {events.map((evt) => (
          <div
            key={evt.id}
            className="flex items-center justify-between px-5 py-3 hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center gap-2">
              <span
                className={`inline-block h-2.5 w-2.5 rounded-full ${
                  CLASS_DOT_COLORS[evt.vehicle_class] || 'bg-gray-400'
                }`}
              />
              <span className="font-medium text-gray-800">{evt.vehicle_class}</span>
              {evt.booth && (
                <span className="text-xs text-gray-400">@ {evt.booth}</span>
              )}
            </div>
            <div className="text-right flex items-center gap-3">
              <span className="text-xs text-gray-500">
                {(evt.confidence * 100).toFixed(1)}%
              </span>
              <span className="text-xs text-gray-400">{timeAgo(evt.timestamp)}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
