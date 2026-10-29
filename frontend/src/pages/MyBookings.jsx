import React, { useState, useEffect } from 'react';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import {
  Ticket,
  Calendar,
  XCircle,
  AlertCircle,
  CheckCircle,
  Clock,
  ArrowRight,
  ShieldAlert,
} from 'lucide-react';

const MyBookings = () => {
  const { user } = useAuth();
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Cancellation modal state
  const [cancellingTicket, setCancellingTicket] = useState(null);
  const [cancelReason, setCancelReason] = useState('Change of travel plans');
  const [cancellingInProgress, setCancellingInProgress] = useState(false);
  const [cancelSuccessMsg, setCancelSuccessMsg] = useState(null);
  const [cancelErrorMsg, setCancelErrorMsg] = useState(null);

  const fetchMyBookings = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get('/bookings/my-bookings');
      setBookings(res.data || []);
    } catch (err) {
      console.error('Failed to load my bookings:', err);
      setError('Unable to fetch your reservation history.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMyBookings();
  }, []);

  const handleCancelTicket = async (e) => {
    e.preventDefault();
    if (!cancellingTicket) return;

    setCancellingInProgress(true);
    setCancelErrorMsg(null);
    setCancelSuccessMsg(null);

    try {
      const res = await api.post('/cancellations', {
        ticket_id: cancellingTicket.ticket_id,
        cancellation_reason: cancelReason,
      });

      setCancelSuccessMsg(
        `Ticket #${cancellingTicket.ticket_number} cancelled successfully. Refund amount: ₹${res.data.refund_amount.toFixed(2)} (Cancellation fee: ₹${res.data.cancellation_fee.toFixed(2)}). Seat released back to inventory.`
      );
      setCancellingTicket(null);
      // Refresh bookings
      fetchMyBookings();
    } catch (err) {
      console.error('Cancellation failed:', err);
      setCancelErrorMsg(err.response?.data?.detail || 'Failed to process ticket cancellation.');
    } finally {
      setCancellingInProgress(false);
    }
  };

  if (loading) {
    return <LoadingSpinner message="Retrieving your reservation manifests..." />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-2 border-b border-slate-200">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            My Reservations & Tickets
          </h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Confirmed journey permits, allocated coach seats, and refund cancellations
          </p>
        </div>

        <Link
          to="/booking"
          className="inline-flex items-center gap-1.5 text-xs font-semibold bg-sky-600 hover:bg-sky-500 text-white px-3.5 py-2 rounded-lg shadow-sm transition-colors"
        >
          <Ticket className="w-4 h-4" />
          <span>Book New Journey</span>
        </Link>
      </div>

      {error && <ErrorMessage message={error} onRetry={fetchMyBookings} />}

      {cancelSuccessMsg && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs rounded-lg flex items-center gap-2">
          <CheckCircle className="w-4 h-4 text-emerald-600 flex-shrink-0" />
          <span>{cancelSuccessMsg}</span>
        </div>
      )}

      {/* Bookings List */}
      {bookings.length > 0 ? (
        <div className="space-y-4">
          {bookings.map((booking) => (
            <div
              key={booking.booking_id}
              className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden"
            >
              {/* Booking Header */}
              <div className="p-4 bg-slate-50 border-b border-slate-200 flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  <div className="bg-sky-100 text-sky-800 font-mono text-xs font-bold px-2.5 py-1 rounded">
                    PNR: {booking.booking_reference}
                  </div>
                  <span className="text-xs text-slate-500 flex items-center gap-1">
                    <Calendar className="w-3.5 h-3.5" />
                    {new Date(booking.booking_date).toLocaleDateString()}
                  </span>
                </div>

                <div className="flex items-center gap-4 text-xs">
                  <div>
                    <span className="text-slate-400">Total Fare: </span>
                    <span className="font-bold text-slate-900">
                      ₹{parseFloat(booking.total_fare).toFixed(2)}
                    </span>
                  </div>
                  <span
                    className={`px-2 py-0.5 rounded-full font-semibold ${
                      booking.booking_status === 'CONFIRMED'
                        ? 'bg-emerald-100 text-emerald-800'
                        : 'bg-rose-100 text-rose-800'
                    }`}
                  >
                    {booking.booking_status}
                  </span>
                </div>
              </div>

              {/* Tickets List */}
              <div className="p-4 divide-y divide-slate-100">
                {booking.tickets && booking.tickets.length > 0 ? (
                  booking.tickets.map((t) => (
                    <div
                      key={t.ticket_id}
                      className="py-3 first:pt-0 last:pb-0 flex flex-col sm:flex-row sm:items-center justify-between gap-3"
                    >
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-xs font-bold text-slate-700">
                            Ticket #{t.ticket_number}
                          </span>
                          <span
                            className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                              t.ticket_status === 'CONFIRMED'
                                ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                                : 'bg-rose-50 text-rose-700 border border-rose-200'
                            }`}
                          >
                            {t.ticket_status}
                          </span>
                        </div>
                        <div className="text-sm font-semibold text-slate-900 mt-1">
                          Coach {t.coach_number || 'A1'} - Seat {t.seat_number || '1'} ({t.seat_class || '3A'}, {t.seat_type || 'BERTH'})
                        </div>
                        <div className="text-xs text-slate-500 mt-0.5">
                          Corridor: {t.origin_station_name || `Station #${t.origin_station_id}`} &rarr; {t.destination_station_name || `Station #${t.destination_station_id}`}
                        </div>
                      </div>

                      <div className="flex items-center gap-3">
                        <span className="font-bold text-slate-900 text-sm">
                          ₹{parseFloat(t.fare_amount).toFixed(2)}
                        </span>

                        {t.ticket_status === 'CONFIRMED' && (
                          <button
                            onClick={() => {
                              setCancellingTicket(t);
                              setCancelErrorMsg(null);
                            }}
                            className="px-3 py-1.5 text-xs font-semibold text-rose-600 hover:text-rose-700 bg-rose-50 hover:bg-rose-100 rounded-lg transition-colors border border-rose-200"
                          >
                            Cancel Ticket
                          </button>
                        )}
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="text-xs text-slate-400 py-2">
                    No ticket records attached to this booking.
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-white rounded-xl border border-slate-200 p-12 text-center shadow-sm">
          <Ticket className="w-10 h-10 text-slate-300 mx-auto mb-3" />
          <h3 className="text-base font-bold text-slate-800">No Reservations Found</h3>
          <p className="text-xs text-slate-500 mt-1">
            You have not booked any train journeys yet.
          </p>
          <Link
            to="/booking"
            className="inline-block mt-4 px-4 py-2 text-xs font-semibold bg-sky-600 hover:bg-sky-500 text-white rounded-lg transition-colors"
          >
            Search & Book Seats
          </Link>
        </div>
      )}

      {/* Cancellation Confirmation Modal */}
      {cancellingTicket && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6 border border-slate-200">
            <div className="flex items-center gap-3 text-rose-600 mb-2">
              <ShieldAlert className="w-6 h-6" />
              <h3 className="text-lg font-bold text-slate-900">Confirm Ticket Cancellation</h3>
            </div>

            <p className="text-xs text-slate-600">
              Are you sure you want to cancel Ticket #{cancellingTicket.ticket_number}?
              The seat will be automatically released back to the inventory, and standard refund policies will apply.
            </p>

            {cancelErrorMsg && (
              <div className="mt-3 p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-lg">
                {cancelErrorMsg}
              </div>
            )}

            <form onSubmit={handleCancelTicket} className="mt-4 space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Reason for Cancellation
                </label>
                <select
                  value={cancelReason}
                  onChange={(e) => setCancelReason(e.target.value)}
                  className="w-full px-3 py-2 text-sm bg-white border border-slate-200 rounded-lg focus:ring-2 focus:ring-sky-500"
                >
                  <option value="Change of travel plans">Change of travel plans</option>
                  <option value="Booking error or duplicate">Booking error or duplicate</option>
                  <option value="Medical emergency">Medical emergency</option>
                  <option value="Personal schedule conflict">Personal schedule conflict</option>
                </select>
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t border-slate-200">
                <button
                  type="button"
                  onClick={() => setCancellingTicket(null)}
                  className="px-4 py-2 text-xs font-semibold text-slate-600 hover:text-slate-800 rounded-lg"
                >
                  Keep Reservation
                </button>
                <button
                  type="submit"
                  disabled={cancellingInProgress}
                  className="px-4 py-2 text-xs font-semibold bg-rose-600 hover:bg-rose-500 text-white rounded-lg disabled:opacity-50"
                >
                  {cancellingInProgress ? 'Processing Refund...' : 'Confirm Cancellation'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default MyBookings;
