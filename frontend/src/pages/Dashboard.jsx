import React, { useState, useEffect } from 'react';
import api from '../api/client';
import StatCard from '../components/StatCard';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import {
  Ticket,
  DollarSign,
  AlertTriangle,
  Train,
  CheckCircle2,
  TrendingUp,
  MapPin,
  Calendar,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
} from 'recharts';

const COLORS = ['#0284c7', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [routePerformance, setRoutePerformance] = useState([]);
  const [monthlyRevenue, setMonthlyRevenue] = useState([]);
  const [delaySummary, setDelaySummary] = useState([]);
  const [activeTrips, setActiveTrips] = useState([]);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      // Fetch analytical reports and trips
      const [perfRes, revRes, delayRes, tripsRes] = await Promise.allSettled([
        api.get('/reports/route-performance'),
        api.get('/reports/monthly-revenue'),
        api.get('/reports/delay-summary'),
        api.get('/trips?limit=8'),
      ]);

      if (perfRes.status === 'fulfilled') setRoutePerformance(perfRes.value.data || []);
      if (revRes.status === 'fulfilled') setMonthlyRevenue(revRes.value.data || []);
      if (delayRes.status === 'fulfilled') setDelaySummary(delayRes.value.data || []);
      if (tripsRes.status === 'fulfilled') setActiveTrips(tripsRes.value.data || []);
    } catch (err) {
      console.error('Error loading dashboard data:', err);
      setError('Unable to load full dashboard analytics. Please ensure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  if (loading) {
    return <LoadingSpinner message="Querying MySQL analytical views..." />;
  }

  // Calculate high-level summary KPIs
  const totalRevenue = routePerformance.reduce((acc, r) => acc + (parseFloat(r.net_revenue) || 0), 0);
  const totalPassengers = routePerformance.reduce((acc, r) => acc + (parseInt(r.total_passengers_booked, 10) || 0), 0);
  const totalDelayedTrips = routePerformance.reduce((acc, r) => acc + (parseInt(r.delayed_trips_count, 10) || 0), 0);
  const totalTripsScheduled = routePerformance.reduce((acc, r) => acc + (parseInt(r.total_trips_scheduled, 10) || 0), 0);

  // Prepare chart data for top 5 routes by revenue
  const topRoutesRevenueData = routePerformance.slice(0, 5).map((r) => ({
    name: r.route_code,
    gross: parseFloat(r.gross_revenue) || 0,
    refunds: parseFloat(r.total_refunds) || 0,
    net: parseFloat(r.net_revenue) || 0,
  }));

  // Prepare delay incidents breakdown by root cause
  const delayCauseMap = delaySummary.reduce((acc, item) => {
    const reason = item.primary_delay_reason || 'Other';
    acc[reason] = (acc[reason] || 0) + (item.total_delay_incidents || 1);
    return acc;
  }, {});

  const delayPieData = Object.entries(delayCauseMap).map(([name, value]) => ({
    name,
    value,
  }));

  return (
    <div className="space-y-6">
      {/* Page Title & System Status Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-2 border-b border-slate-200">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">System Dashboard</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Real-time transit operations, commercial metrics, and capacity tracking
          </p>
        </div>
        <div className="flex items-center gap-2 text-xs font-mono bg-sky-50 text-sky-800 border border-sky-200 px-3 py-1.5 rounded-lg">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span>MySQL 8.0 Views Active</span>
        </div>
      </div>

      {error && <ErrorMessage message={error} onRetry={fetchDashboardData} />}

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Net Revenue"
          value={`₹${totalRevenue.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`}
          icon={DollarSign}
          color="emerald"
          change="+14.2%"
          trend="up"
          subtitle="Across network routes"
        />
        <StatCard
          title="Total Passengers"
          value={totalPassengers.toLocaleString('en-IN')}
          icon={Ticket}
          color="blue"
          change="+8.6%"
          trend="up"
          subtitle="Confirmed bookings"
        />
        <StatCard
          title="Trips Scheduled"
          value={totalTripsScheduled || activeTrips.length}
          icon={Train}
          color="purple"
          subtitle="Active corridor services"
        />
        <StatCard
          title="Delay Incidents"
          value={totalDelayedTrips}
          icon={AlertTriangle}
          color={totalDelayedTrips > 0 ? 'amber' : 'emerald'}
          subtitle="Exceeding 15 min threshold"
        />
      </div>

      {/* Visual Analytics Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Top Routes Revenue Comparison */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-slate-900">Corridor Revenue Performance</h3>
              <p className="text-xs text-slate-500">Gross revenue vs refunds (v_route_performance)</p>
            </div>
            <TrendingUp className="w-5 h-5 text-slate-400" />
          </div>

          <div className="h-72 w-full">
            {topRoutesRevenueData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={topRoutesRevenueData} margin={{ top: 10, right: 10, left: 0, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip
                    formatter={(value) => [`₹${value.toLocaleString()}`, 'Amount']}
                    contentStyle={{ backgroundColor: '#0f172a', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                  />
                  <Legend wrapperStyle={{ fontSize: '12px' }} />
                  <Bar dataKey="gross" name="Gross Revenue" fill="#0284c7" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="refunds" name="Refunds" fill="#ef4444" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-400">
                No revenue records available in database.
              </div>
            )}
          </div>
        </div>

        {/* Delay Incident Causes Pie Chart */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-slate-900">Delay Root Causes</h3>
              <p className="text-xs text-slate-500">Operational incident distribution</p>
            </div>
            <AlertTriangle className="w-5 h-5 text-amber-500" />
          </div>

          <div className="h-72 w-full flex items-center justify-center">
            {delayPieData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={delayPieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={85}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {delayPieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                  />
                  <Legend wrapperStyle={{ fontSize: '11px' }} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-xs text-slate-400 text-center">
                <CheckCircle2 className="w-8 h-8 text-emerald-500 mx-auto mb-2" />
                No major delay incidents recorded.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Active Scheduled Trips Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-5 border-b border-slate-200 flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-slate-900">Current & Upcoming Journey Trips</h3>
            <p className="text-xs text-slate-500">Live operational status and base fares</p>
          </div>
          <Calendar className="w-5 h-5 text-slate-400" />
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-600">
            <thead className="bg-slate-50 text-xs font-semibold text-slate-500 uppercase tracking-wider border-b border-slate-200">
              <tr>
                <th className="px-5 py-3">Trip ID</th>
                <th className="px-5 py-3">Service</th>
                <th className="px-5 py-3">Route</th>
                <th className="px-5 py-3">Date</th>
                <th className="px-5 py-3">Departure</th>
                <th className="px-5 py-3">Base Fare</th>
                <th className="px-5 py-3">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {activeTrips.length > 0 ? (
                activeTrips.map((trip) => (
                  <tr key={trip.trip_id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-5 py-3.5 font-mono text-xs font-semibold text-slate-700">
                      #{trip.trip_id}
                    </td>
                    <td className="px-5 py-3.5 font-medium text-slate-900">
                      {trip.service_name || `Service #${trip.service_id}`}
                      <span className="block text-xs text-slate-400 font-mono">
                        {trip.service_number || ''}
                      </span>
                    </td>
                    <td className="px-5 py-3.5">
                      <span className="inline-flex items-center gap-1 text-slate-700">
                        <MapPin className="w-3.5 h-3.5 text-slate-400" />
                        {trip.route_code || `Route #${trip.route_id}`}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 font-mono text-xs text-slate-600">
                      {trip.trip_date}
                    </td>
                    <td className="px-5 py-3.5 font-mono text-xs text-slate-600">
                      {trip.scheduled_departure ? new Date(trip.scheduled_departure).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '-'}
                    </td>
                    <td className="px-5 py-3.5 font-semibold text-slate-900">
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
                ))
              ) : (
                <tr>
                  <td colSpan="7" className="px-5 py-8 text-center text-xs text-slate-400">
                    No active trips found. Initialize database seeds to populate calendar trips.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
