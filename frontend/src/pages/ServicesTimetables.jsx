import React, { useState, useEffect } from 'react';
import api from '../api/client';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import {
  Train,
  Calendar,
  Clock,
  Search,
  Filter,
  CheckCircle,
  AlertCircle,
  Tag,
} from 'lucide-react';

const ServicesTimetables = () => {
  const [activeTab, setActiveTab] = useState('services'); // 'services' | 'trips'
  const [services, setServices] = useState([]);
  const [trips, setTrips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [serviceTypeFilter, setServiceTypeFilter] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [svcRes, tripRes] = await Promise.all([
        api.get('/services?limit=50'),
        api.get('/trips?limit=50'),
      ]);
      setServices(svcRes.data || []);
      setTrips(tripRes.data || []);
    } catch (err) {
      console.error('Error fetching services or timetables:', err);
      setError('Failed to fetch services and schedule data from MySQL.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const filteredServices = services.filter((s) => {
    const matchesSearch =
      s.service_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.service_name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType =
      serviceTypeFilter === 'ALL' || s.service_type === serviceTypeFilter;
    return matchesSearch && matchesType;
  });

  const filteredTrips = trips.filter((t) => {
    const matchesSearch =
      (t.service_name && t.service_name.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (t.route_code && t.route_code.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (t.service_number && t.service_number.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesSearch;
  });

  if (loading) {
    return <LoadingSpinner message="Loading train services catalog and timetable schedule..." />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-2 border-b border-slate-200">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Services & Timetables
          </h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Operational train catalog, rakes, calendar trips, and timetable departures
          </p>
        </div>

        {/* Tab Controls */}
        <div className="bg-slate-200 p-1 rounded-lg flex text-xs font-semibold">
          <button
            onClick={() => setActiveTab('services')}
            className={`px-3 py-1.5 rounded-md transition-all ${
              activeTab === 'services' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Services Catalog ({services.length})
          </button>
          <button
            onClick={() => setActiveTab('trips')}
            className={`px-3 py-1.5 rounded-md transition-all ${
              activeTab === 'trips' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Scheduled Trips ({trips.length})
          </button>
        </div>
      </div>

      {error && <ErrorMessage message={error} onRetry={fetchData} />}

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder={
              activeTab === 'services'
                ? 'Search by train number (e.g. 12952) or service name...'
                : 'Search by service name or route code...'
            }
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-sm bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500 shadow-sm"
          />
        </div>

        {activeTab === 'services' && (
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-slate-400" />
            <select
              value={serviceTypeFilter}
              onChange={(e) => setServiceTypeFilter(e.target.value)}
              className="px-3 py-2 text-sm bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500 shadow-sm"
            >
              <option value="ALL">All Service Types</option>
              <option value="EXPRESS">Express</option>
              <option value="SUPERFAST">Superfast</option>
              <option value="RAJDHANI">Rajdhani Express</option>
              <option value="SHATABDI">Shatabdi Express</option>
              <option value="VANDE_BHARAT">Vande Bharat</option>
            </select>
          </div>
        )}
      </div>

      {/* Services Grid or Trips Table */}
      {activeTab === 'services' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredServices.map((svc) => (
            <div
              key={svc.service_id}
              className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm hover:shadow transition-shadow flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-bold bg-sky-50 text-sky-700 px-2 py-0.5 rounded border border-sky-100">
                    {svc.service_number}
                  </span>
                  <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700">
                    {svc.service_type.replace('_', ' ')}
                  </span>
                </div>
                <h3 className="font-bold text-slate-900 text-base mt-2">
                  {svc.service_name}
                </h3>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                <span className="font-mono">Route ID: #{svc.route_id}</span>
                <span className="inline-flex items-center gap-1 text-emerald-600 font-semibold">
                  <CheckCircle className="w-3.5 h-3.5" /> Operational
                </span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        /* Trips Table */
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-600">
              <thead className="bg-slate-50 text-xs font-semibold text-slate-500 uppercase tracking-wider border-b border-slate-200">
                <tr>
                  <th className="px-5 py-3">Trip ID</th>
                  <th className="px-5 py-3">Train Service</th>
                  <th className="px-5 py-3">Route Corridor</th>
                  <th className="px-5 py-3">Date</th>
                  <th className="px-5 py-3">Departure</th>
                  <th className="px-5 py-3">Arrival</th>
                  <th className="px-5 py-3">Base Fare</th>
                  <th className="px-5 py-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredTrips.map((trip) => (
                  <tr key={trip.trip_id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-5 py-3.5 font-mono text-xs font-semibold text-slate-700">
                      #{trip.trip_id}
                    </td>
                    <td className="px-5 py-3.5">
                      <div className="font-medium text-slate-900">{trip.service_name || `Service #${trip.service_id}`}</div>
                      <div className="text-xs font-mono text-slate-400">{trip.service_number}</div>
                    </td>
                    <td className="px-5 py-3.5">
                      <span className="font-mono text-xs font-semibold text-sky-700">
                        {trip.route_code || `Route #${trip.route_id}`}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 font-mono text-xs text-slate-600">
                      {trip.trip_date}
                    </td>
                    <td className="px-5 py-3.5 font-mono text-xs text-slate-600">
                      {trip.scheduled_departure ? new Date(trip.scheduled_departure).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '-'}
                    </td>
                    <td className="px-5 py-3.5 font-mono text-xs text-slate-600">
                      {trip.scheduled_arrival ? new Date(trip.scheduled_arrival).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '-'}
                    </td>
                    <td className="px-5 py-3.5 font-bold text-slate-900">
                      ₹{parseFloat(trip.base_fare).toFixed(2)}
                    </td>
                    <td className="px-5 py-3.5">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          trip.status === 'SCHEDULED' || trip.status === 'ON_TIME'
                            ? 'bg-emerald-100 text-emerald-800'
                            : trip.status === 'DELAYED'
                            ? 'bg-amber-100 text-amber-800'
                            : trip.status === 'CANCELLED'
                            ? 'bg-rose-100 text-rose-800'
                            : 'bg-slate-100 text-slate-800'
                        }`}
                      >
                        {trip.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default ServicesTimetables;
