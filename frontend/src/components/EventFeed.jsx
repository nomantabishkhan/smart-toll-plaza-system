import { useState, useEffect, useRef } from 'react';
import { fetchRecentEvents } from '../api';

function timeAgo(isoString) {
  const diff = Math.floor((Date.now() - new Date(isoString).getTime()) / 1000);
  if (diff < 60) return `${diff}s ago`;
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  return `${Math.floor(diff / 3600)}h ago`;
}

export default function EventFeed({ latestWsEvent }) {
  const [events, setEvents] = useState([]);
  const prevWsEventRef = useRef(null);

  // Fetch initial events on mount
  useEffect(() => {
    fetchRecentEvents(30).then(setEvents).catch(console.error);
  }, []);

  // Prepend WebSocket events as they arrive
  useEffect(() => {
    if (
      latestWsEvent &&
      latestWsEvent.type === 'vehicle_detected' &&
      latestWsEvent !== prevWsEventRef.current
    ) {
      prevWsEventRef.current = latestWsEvent;
      const newEvent = {
        id: crypto.randomUUID(),
        vehicle_class: latestWsEvent.data.vehicle_class,
        confidence: latestWsEvent.data.confidence,
        booth: latestWsEvent.data.booth,
        timestamp: new Date().toISOString(),
      };
      setEvents((prev) => [newEvent, ...prev].slice(0, 100));
    }
  }, [latestWsEvent]);

  return (
    <div className="rounded-xl bg-white shadow border border-gray-200 overflow-hidden">
      <div className="px-5 py-3 border-b border-gray-200 bg-gray-50">
        <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">
          Recent Crossings
        </h3>
      </div>
      <div className="max-h-100 overflow-y-auto divide-y divide-gray-100">
        {events.length === 0 && (
          <p className="p-5 text-sm text-gray-400 text-center">
            No crossings yet today
          </p>
        )}
        {events.map((evt) => (
          <div
            key={evt.id}
            className="flex items-center justify-between px-5 py-3 hover:bg-gray-50 transition-colors"
          >
            <div>
              <span className="font-medium text-gray-800">
                {evt.vehicle_class}
              </span>
              {evt.booth && (
                <span className="ml-2 text-xs text-gray-400">
                  @ {evt.booth}
                </span>
              )}
            </div>
            <div className="text-right">
              <span className="text-xs text-gray-500">
                {(evt.confidence * 100).toFixed(1)}%
              </span>
              <span className="ml-3 text-xs text-gray-400">
                {timeAgo(evt.timestamp)}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
