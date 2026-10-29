import React, { useState, useEffect } from 'react';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import {
  MapPin,
  Route as RouteIcon,
  Plus,
  Search,
  ChevronRight,
  Clock,
  Layers,
  ArrowRight,
} from 'lucide-react';

const StationsRoutes = () => {
  const { isStaff } = useAuth();
  const [activeTab, setActiveTab] = useState('stations'); // 'stations' | 'routes'
  const [stations, setStations] = useState([]);
  const [routes, setRoutes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  // Selected route for stop sequence visualization
  const [selectedRoute, setSelectedRoute] = useState(null);
  const [routeStops, setRouteStops] = useState([]);
  const [loadingStops, setLoadingStops] = useState(false);

  // Station creation modal state
  const [showStationModal, setShowStationModal] = useState(false);
  const [stationForm, setStationForm] = useState({
    station_code: '',
    station_name: '',
    city: '',
    state: '',
    zone: 'Northern',
    total_platforms: 4,
    latitude: 28.6139,
    longitude: 77.2090,
  });
  const [modalSubmitting, setModalSubmitting] = useState(false);
  const [modalMessage, setModalMessage] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [stRes, rtRes] = await Promise.all([
        api.get('/stations?limit=50'),
        api.get('/routes?limit=50'),
      ]);
      setStations(stRes.data || []);
      setRoutes(rtRes.data || []);
      if (rtRes.data && rtRes.data.length > 0) {
        loadRouteDetails(rtRes.data[0]);
      }
    } catch (err) {
      console.error('Error fetching stations or routes:', err);
      setError('Failed to fetch station and route records from MySQL.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const loadRouteDetails = async (route) => {
    setSelectedRoute(route);
    setLoadingStops(true);
    try {
      const res = await api.get(`/routes/${route.route_id}`);
      setRouteStops(res.data.stops || []);
    } catch (err) {
      console.error('Error fetching route stop sequence:', err);
      setRouteStops([]);
    } finally {
      setLoadingStops(false);
    }
  };

  const handleCreateStation = async (e) => {
    e.preventDefault();
    setModalSubmitting(true);
    setModalMessage(null);
    try {
      await api.post('/stations', stationForm);
      setShowStationModal(false);
      setStationForm({
        station_code: '',
        station_name: '',
        city: '',
        state: '',
        zone: 'Northern',
        total_platforms: 4,
        latitude: 28.6139,
        longitude: 77.2090,
      });
      fetchData();
    } catch (err) {
      console.error('Error creating station:', err);
      setModalMessage(err.response?.data?.detail || 'Failed to create station. Verify unique constraints.');
    } finally {
      setModalSubmitting(false);
    }
  };

  const filteredStations = stations.filter(
    (s) =>
      s.station_code.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.station_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.city.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredRoutes = routes.filter(
    (r) =>
      r.route_code.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.route_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (loading) {
    return <LoadingSpinner message="Loading stations and corridor routes..." />;
  }

  return (
    <div className="space-y-6">
      {/* Header and Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-2 border-b border-slate-200">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Stations & Corridor Routes
          </h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Physical station terminal master records and topological route halts
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Tab Selector */}
          <div className="bg-slate-200 p-1 rounded-lg flex text-xs font-semibold">
            <button
              onClick={() => setActiveTab('stations')}
              className={`px-3 py-1.5 rounded-md transition-all ${
                activeTab === 'stations' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Stations ({stations.length})
            </button>
            <button
              onClick={() => setActiveTab('routes')}
              className={`px-3 py-1.5 rounded-md transition-all ${
                activeTab === 'routes' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Routes ({routes.length})
            </button>
          </div>

          {/* Add Station Button (Staff/Admin) */}
          {isStaff && (
            <button
              onClick={() => setShowStationModal(true)}
              className="flex items-center gap-1.5 text-xs font-semibold bg-sky-600 hover:bg-sky-500 text-white px-3.5 py-2 rounded-lg shadow-sm transition-colors"
            >
              <Plus className="w-4 h-4" />
              <span>Add Station</span>
            </button>
          )}
        </div>
      </div>

      {error && <ErrorMessage message={error} onRetry={fetchData} />}

      {/* Search Input Bar */}
      <div className="relative max-w-md">
        <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
        <input
          type="text"
          placeholder={`Search ${activeTab === 'stations' ? 'by station code, name, or city...' : 'by route code or name...'}`}
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full pl-9 pr-4 py-2 text-sm bg-white border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500 shadow-sm"
        />
      </div>

      {/* Main Tab Content */}
      {activeTab === 'stations' ? (
        /* Stations Table */
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-600">
              <thead className="bg-slate-50 text-xs font-semibold text-slate-500 uppercase tracking-wider border-b border-slate-200">
                <tr>
                  <th className="px-5 py-3">Code</th>
                  <th className="px-5 py-3">Station Name</th>
                  <th className="px-5 py-3">City & State</th>
                  <th className="px-5 py-3">Railway Zone</th>
                  <th className="px-5 py-3">Platforms</th>
                  <th className="px-5 py-3">Coordinates</th>
                  <th className="px-5 py-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredStations.map((station) => (
                  <tr key={station.station_id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-5 py-3.5 font-mono font-bold text-sky-700">
                      {station.station_code}
                    </td>
                    <td className="px-5 py-3.5 font-medium text-slate-900">
                      {station.station_name}
                    </td>
                    <td className="px-5 py-3.5">
                      {station.city}, <span className="text-slate-400">{station.state}</span>
                    </td>
                    <td className="px-5 py-3.5">
                      <span className="bg-slate-100 text-slate-700 text-xs px-2 py-0.5 rounded font-mono">
                        {station.zone}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 font-semibold text-slate-700">
                      {station.total_platforms}
                    </td>
                    <td className="px-5 py-3.5 text-xs font-mono text-slate-400">
                      {Number(station.latitude).toFixed(3)}, {Number(station.longitude).toFixed(3)}
                    </td>
                    <td className="px-5 py-3.5">
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                          station.is_active ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'
                        }`}
                      >
                        {station.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        /* Routes and Stop Sequence Visualizer */
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Corridor Routes List */}
          <div className="lg:col-span-1 bg-white rounded-xl border border-slate-200 p-4 shadow-sm space-y-2 max-h-[600px] overflow-y-auto">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 px-2 mb-2">
              Select Corridor Route
            </h3>
            {filteredRoutes.map((route) => (
              <div
                key={route.route_id}
                onClick={() => loadRouteDetails(route)}
                className={`p-3 rounded-lg border cursor-pointer transition-all ${
                  selectedRoute?.route_id === route.route_id
                    ? 'border-sky-500 bg-sky-50/60 shadow-sm'
                    : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-bold text-sky-700">
                    {route.route_code}
                  </span>
                  <span className="text-xs text-slate-500">
                    {route.total_distance_km} km
                  </span>
                </div>
                <div className="font-medium text-slate-900 text-sm mt-1">
                  {route.route_name}
                </div>
                <div className="flex items-center gap-2 mt-2 text-xs text-slate-500">
                  <Clock className="w-3.5 h-3.5" />
                  <span>~{Math.round(route.duration_est_minutes / 60)} hrs {route.duration_est_minutes % 60} min</span>
                </div>
              </div>
            ))}
          </div>

          {/* Route Halts & Topo Sequence Visualizer */}
          <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
            {selectedRoute ? (
              <div>
                <div className="flex items-center justify-between pb-4 border-b border-slate-200">
                  <div>
                    <span className="font-mono text-xs font-bold text-sky-600 bg-sky-50 px-2 py-0.5 rounded">
                      {selectedRoute.route_code}
                    </span>
                    <h2 className="text-lg font-bold text-slate-900 mt-1">
                      {selectedRoute.route_name}
                    </h2>
                    <p className="text-xs text-slate-500 mt-0.5">
                      Corridor distance: {selectedRoute.total_distance_km} km | Total travel time: ~{Math.round(selectedRoute.duration_est_minutes / 60)} hours
                    </p>
                  </div>
                  <RouteIcon className="w-6 h-6 text-slate-400" />
                </div>

                {loadingStops ? (
                  <LoadingSpinner message="Loading route stops sequence..." />
                ) : (
                  <div className="mt-6">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-4">
                      Intermediate Stops & Platform Halts Sequence
                    </h4>

                    {routeStops.length > 0 ? (
                      <div className="relative border-l-2 border-sky-400 ml-4 space-y-6 py-2">
                        {routeStops.map((stop, idx) => (
                          <div key={stop.stop_id} className="relative pl-6 group">
                            {/* Sequence number dot */}
                            <div className="absolute -left-[11px] top-1 w-5 h-5 rounded-full bg-white border-2 border-sky-500 flex items-center justify-center text-[10px] font-bold text-sky-700 shadow-sm">
                              {stop.stop_sequence}
                            </div>

                            <div className="bg-slate-50 group-hover:bg-sky-50/50 transition-colors border border-slate-200 rounded-lg p-3">
                              <div className="flex items-center justify-between">
                                <span className="font-bold text-slate-900 text-sm">
                                  {stop.station_name || `Station ID ${stop.station_id}`}
                                </span>
                                <span className="font-mono text-xs font-semibold text-sky-700 bg-white px-2 py-0.5 rounded border border-slate-200">
                                  Platform {stop.platform_number || '1'}
                                </span>
                              </div>

                              <div className="flex flex-wrap items-center gap-4 mt-2 text-xs text-slate-500">
                                <div>
                                  <span className="text-slate-400">Distance: </span>
                                  <span className="font-medium text-slate-700">{stop.distance_from_origin_km} km</span>
                                </div>
                                {stop.halt_duration_minutes > 0 && (
                                  <div>
                                    <span className="text-slate-400">Halt: </span>
                                    <span className="font-medium text-amber-700">{stop.halt_duration_minutes} mins</span>
                                  </div>
                                )}
                                <div>
                                  <span className="text-slate-400">Dep. Offset: </span>
                                  <span className="font-medium text-slate-700">+{stop.departure_offset_minutes} min</span>
                                </div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-10 text-xs text-slate-400">
                        No intermediate halts mapped for this corridor yet.
                      </div>
                    )}
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-16 text-slate-400">
                Select a route from the left corridor catalog to view its stop sequence.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Modal: Create Station */}
      {showStationModal && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6 border border-slate-200">
            <h3 className="text-lg font-bold text-slate-900">Add New Railway Station</h3>
            <p className="text-xs text-slate-500 mt-1">Insert record directly into stations table (Raw SQL)</p>

            {modalMessage && (
              <div className="mt-3 p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-lg">
                {modalMessage}
              </div>
            )}

            <form onSubmit={handleCreateStation} className="mt-4 space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Station Code *</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. NDLS"
                    value={stationForm.station_code}
                    onChange={(e) => setStationForm({ ...stationForm, station_code: e.target.value.toUpperCase() })}
                    className="w-full px-3 py-1.5 text-sm border border-slate-200 rounded-lg focus:ring-2 focus:ring-sky-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">Platforms *</label>
                  <input
                    type="number"
                    min="1"
                    max="30"
                    required
                    value={stationForm.total_platforms}
                    onChange={(e) => setStationForm({ ...stationForm, total_platforms: parseInt(e.target.value, 10) })}
                    className="w-full px-3 py-1.5 text-sm border border-slate-200 rounded-lg focus:ring-2 focus:ring-sky-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Station Name *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. New Delhi Railway Station"
                  value={stationForm.station_name}
                  onChange={(e) => setStationForm({ ...stationForm, station_name: e.target.value })}
                  className="w-full px-3 py-1.5 text-sm border border-slate-200 rounded-lg focus:ring-2 focus:ring-sky-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">City *</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. New Delhi"
                    value={stationForm.city}
                    onChange={(e) => setStationForm({ ...stationForm, city: e.target.value })}
                    className="w-full px-3 py-1.5 text-sm border border-slate-200 rounded-lg focus:ring-2 focus:ring-sky-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">State *</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Delhi"
                    value={stationForm.state}
                    onChange={(e) => setStationForm({ ...stationForm, state: e.target.value })}
                    className="w-full px-3 py-1.5 text-sm border border-slate-200 rounded-lg focus:ring-2 focus:ring-sky-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Railway Zone *</label>
                <select
                  value={stationForm.zone}
                  onChange={(e) => setStationForm({ ...stationForm, zone: e.target.value })}
                  className="w-full px-3 py-1.5 text-sm border border-slate-200 rounded-lg focus:ring-2 focus:ring-sky-500"
                >
                  <option value="Northern">Northern Railway (NR)</option>
                  <option value="Western">Western Railway (WR)</option>
                  <option value="Central">Central Railway (CR)</option>
                  <option value="Eastern">Eastern Railway (ER)</option>
                  <option value="Southern">Southern Railway (SR)</option>
                  <option value="South Western">South Western Railway (SWR)</option>
                </select>
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t border-slate-200">
                <button
                  type="button"
                  onClick={() => setShowStationModal(false)}
                  className="px-4 py-2 text-xs font-semibold text-slate-600 hover:text-slate-800 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={modalSubmitting}
                  className="px-4 py-2 text-xs font-semibold bg-sky-600 hover:bg-sky-500 text-white rounded-lg disabled:opacity-50"
                >
                  {modalSubmitting ? 'Inserting...' : 'Insert Station'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default StationsRoutes;
