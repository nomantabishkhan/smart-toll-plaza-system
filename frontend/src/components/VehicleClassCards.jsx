const VEHICLE_ICONS = {
  Auto: '🛺',
  Bus: '🚌',
  Car: '🚗',
  LCV: '🚐',
  Motorcycle: '🏍️',
  Multiaxle: '🚛',
  Tractor: '🚜',
  Truck: '🚚',
};

const VEHICLE_COLORS = {
  Auto: 'bg-yellow-100 text-yellow-800 border-yellow-300',
  Bus: 'bg-blue-100 text-blue-800 border-blue-300',
  Car: 'bg-green-100 text-green-800 border-green-300',
  LCV: 'bg-purple-100 text-purple-800 border-purple-300',
  Motorcycle: 'bg-red-100 text-red-800 border-red-300',
  Multiaxle: 'bg-indigo-100 text-indigo-800 border-indigo-300',
  Tractor: 'bg-orange-100 text-orange-800 border-orange-300',
  Truck: 'bg-teal-100 text-teal-800 border-teal-300',
};

export default function VehicleClassCards({ byClass }) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
      {byClass.map((item) => {
        const name = item.vehicle_class__class_name;
        const icon = VEHICLE_ICONS[name] || '🚙';
        const colorClasses =
          VEHICLE_COLORS[name] || 'bg-gray-100 text-gray-800 border-gray-300';
        return (
          <div
            key={item.vehicle_class__id}
            className={`rounded-xl border p-4 flex flex-col items-center shadow-sm transition-transform hover:scale-105 ${colorClasses}`}
          >
            <span className="text-3xl mb-1">{icon}</span>
            <span className="font-semibold text-sm">{name}</span>
            <span className="text-2xl font-bold mt-1">{item.count}</span>
          </div>
        );
      })}
    </div>
  );
}
