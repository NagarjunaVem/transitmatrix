import React, { useState, useEffect } from 'react';
import api from '../api/client';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import { formatErrorMessage } from '../utils/formatError';
import {
  Search,
  Train,
  Calendar,
  MapPin,
  CheckCircle,
  CreditCard,
  User,
  ArrowRight,
  ShieldCheck,
  Armchair,
  Clock,
  Sparkles,
} from 'lucide-react';

const Booking = () => {
  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  // Search parameters
  const [stations, setStations] = useState([]);
  const [origin, setOrigin] = useState('NDLS');
  const [destination, setDestination] = useState('BCT');
  const [travelDate, setTravelDate] = useState(() => {
    // Default to an upcoming travel date
    const d = new Date();
    return d.toISOString().split('T')[0];
  });

  // Search results & upcoming fallback
  const [searchResults, setSearchResults] = useState([]);
  const [upcomingTrips, setUpcomingTrips] = useState([]);
  const [searching, setSearching] = useState(false);
  const [searchError, setSearchError] = useState(null);

  // Selected Trip & Seat Map
  const [selectedTrip, setSelectedTrip] = useState(null);
  const [seatMap, setSeatMap] = useState([]);
  const [loadingSeats, setLoadingSeats] = useState(false);
  const [selectedSeats, setSelectedSeats] = useState([]);

  // Passenger details
  const [passengerDetails, setPassengerDetails] = useState({
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    age: 28,
    gender: 'MALE',
    id_card_type: 'AADHAAR',
    id_card_number: '123456789012',
    email: user?.email || '',
    phone_number: user?.phone_number || '9876543210',
  });

  const [paymentMethod, setPaymentMethod] = useState('UPI');
  const [bookingInProgress, setBookingInProgress] = useState(false);
  const [bookingSuccess, setBookingSuccess] = useState(null);
  const [bookingError, setBookingError] = useState(null);

  // Load stations and upcoming trips on mount
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        const [stRes, trRes] = await Promise.allSettled([
          api.get('/stations?limit=50'),
          api.get('/trips?limit=10&status=SCHEDULED'),
        ]);

        if (stRes.status === 'fulfilled') {
          const stList = stRes.value.data || [];
          setStations(stList);
          if (stList.length >= 2) {
            setOrigin(stList[0].station_code);
            setDestination(stList[1].station_code);
          }
        }

        if (trRes.status === 'fulfilled') {
          setUpcomingTrips(trRes.value.data || []);
        }
      } catch (err) {
        console.error('Failed to load initial booking data:', err);
      }
    };

    loadInitialData();
  }, []);

  // Update passenger details when user logs in or profile changes
  useEffect(() => {
    if (user) {
      setPassengerDetails((prev) => ({
        ...prev,
        first_name: user.first_name || prev.first_name,
        last_name: user.last_name || prev.last_name,
        email: user.email || prev.email,
        phone_number: user.phone_number || prev.phone_number,
      }));
    }
  }, [user]);

  // Execute trip search
  const handleSearch = async (e) => {
    if (e) e.preventDefault();
    setSearching(true);
    setSearchError(null);
    setSelectedTrip(null);
    setSelectedSeats([]);
    setBookingSuccess(null);
    setBookingError(null);

    try {
      // Backend expects origin_code, destination_code, and travel_date
      const res = await api.get('/trips/search', {
        params: {
          origin_code: origin,
          destination_code: destination,
          travel_date: travelDate,
        },
      });

      setSearchResults(res.data || []);
      if (!res.data || res.data.length === 0) {
        setSearchError(
          'No scheduled trains found between these stations on this date. You can select an upcoming scheduled journey below or adjust your search date.'
        );
      }
    } catch (err) {
      console.error('Trip search failed:', err);
      setSearchError(formatErrorMessage(err, 'Failed to search trains for this route corridor.'));
    } finally {
      setSearching(false);
    }
  };

  // Select trip and fetch seat map
  const handleSelectTrip = async (trip) => {
    setSelectedTrip(trip);
    setSelectedSeats([]);
    setLoadingSeats(true);
    setBookingError(null);

    try {
      const res = await api.get(`/bookings/trip/${trip.trip_id}/seats`);
      setSeatMap(res.data || []);
    } catch (err) {
      console.error('Failed to load seat availability:', err);
      setBookingError(formatErrorMessage(err, 'Unable to load real-time seat layout.'));
    } finally {
      setLoadingSeats(false);
    }
  };

  // Toggle seat selection
  const toggleSeat = (seat) => {
    if (!seat.is_available) return;

    if (selectedSeats.some((s) => s.seat_id === seat.seat_id)) {
      setSelectedSeats(selectedSeats.filter((s) => s.seat_id !== seat.seat_id));
    } else {
      if (selectedSeats.length >= 4) {
        alert('You can select a maximum of 4 seats per reservation.');
        return;
      }
      setSelectedSeats([...selectedSeats, seat]);
    }
  };

  // Calculate total fare
  const totalFare = selectedSeats.reduce((acc, seat) => {
    const base = parseFloat(selectedTrip?.base_fare || 0);
    const multiplier = parseFloat(seat.fare_multiplier || 1.0);
    return acc + base * multiplier;
  }, 0);

  // Submit atomic booking reservation
  const handleCompleteBooking = async (e) => {
    e.preventDefault();
    if (!isAuthenticated) {
      alert('Please login to complete your train reservation.');
      navigate('/login');
      return;
    }

    if (selectedSeats.length === 0) {
      alert('Please select at least one available seat from the seat map.');
      return;
    }

    setBookingInProgress(true);
    setBookingError(null);

    try {
      // Step 1: Create or fetch passenger profile
      let passengerId = null;
      try {
        const passRes = await api.post('/passengers', {
          first_name: passengerDetails.first_name,
          last_name: passengerDetails.last_name,
          gender: passengerDetails.gender,
          age: parseInt(passengerDetails.age, 10),
          id_card_type: passengerDetails.id_card_type,
          id_card_number: passengerDetails.id_card_number,
          email: passengerDetails.email,
          phone_number: passengerDetails.phone_number,
        });
        passengerId = passRes.data.passenger_id;
      } catch (passErr) {
        // Fallback: list existing passengers
        const existingPass = await api.get('/passengers?limit=1');
        if (existingPass.data && existingPass.data.length > 0) {
          passengerId = existingPass.data[0].passenger_id;
        } else {
          throw new Error('Could not resolve passenger record.');
        }
      }

      // Step 2: Resolve Station IDs
      const originStation = stations.find((s) => s.station_code === origin) || stations[0];
      const destStation = stations.find((s) => s.station_code === destination) || stations[1];

      // Step 3: Call transactional atomic booking endpoint
      const bookingPayload = {
        trip_id: selectedTrip.trip_id,
        payment_method: paymentMethod,
        passengers: selectedSeats.map((seat) => ({
          passenger_id: passengerId,
          seat_id: seat.seat_id,
          origin_station_id: originStation ? originStation.station_id : 1,
          destination_station_id: destStation ? destStation.station_id : 2,
        })),
      };

      const res = await api.post('/bookings', bookingPayload);
      setBookingSuccess(res.data);
      setSelectedSeats([]);

      // Refresh seat map to show updated inventory state
      const updatedSeats = await api.get(`/bookings/trip/${selectedTrip.trip_id}/seats`);
      setSeatMap(updatedSeats.data || []);
    } catch (err) {
      console.error('Booking failed:', err);
      setBookingError(
        formatErrorMessage(
          err,
          'Booking transaction failed. The selected seat may have just been reserved by another user (Pessimistic Lock Conflict).'
        )
      );
    } finally {
      setBookingInProgress(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="pb-2 border-b border-slate-200">
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
          Passenger Train Booking
        </h1>
        <p className="text-sm text-slate-500 mt-0.5">
          Search corridors, select live coach seats, and execute atomic reservations with ACID concurrency
        </p>
      </div>

      {/* Corridor Search Bar */}
      <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
        <form onSubmit={handleSearch} className="grid grid-cols-1 sm:grid-cols-4 gap-4 items-end">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Origin Station
            </label>
            <select
              value={origin}
              onChange={(e) => setOrigin(e.target.value)}
              className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-lg focus:ring-2 focus:ring-sky-500 font-medium"
            >
              {stations.map((st) => (
                <option key={st.station_id} value={st.station_code}>
                  {st.station_name} ({st.station_code})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Destination Station
            </label>
            <select
              value={destination}
              onChange={(e) => setDestination(e.target.value)}
              className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-lg focus:ring-2 focus:ring-sky-500 font-medium"
            >
              {stations.map((st) => (
                <option key={st.station_id} value={st.station_code}>
                  {st.station_name} ({st.station_code})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Travel Date
            </label>
            <input
              type="date"
              value={travelDate}
              onChange={(e) => setTravelDate(e.target.value)}
              className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-lg focus:ring-2 focus:ring-sky-500 font-medium"
            />
          </div>

          <div>
            <button
              type="submit"
              disabled={searching}
              className="w-full flex items-center justify-center gap-2 bg-sky-600 hover:bg-sky-500 text-white font-semibold text-sm px-4 py-2.5 rounded-lg shadow-sm transition-colors disabled:opacity-50"
            >
              <Search className="w-4 h-4" />
              <span>{searching ? 'Searching...' : 'Find Trains'}</span>
            </button>
          </div>
        </form>
      </div>

      {searchError && <ErrorMessage message={searchError} />}

      {/* Booking Success Receipt */}
      {bookingSuccess && (
        <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-6 shadow-sm">
          <div className="flex items-center gap-3">
            <CheckCircle className="w-7 h-7 text-emerald-600 flex-shrink-0" />
            <div>
              <h3 className="text-lg font-bold text-emerald-900">
                Reservation Confirmed!
              </h3>
              <p className="text-xs text-emerald-700">
                ACID transaction committed successfully. PNR Reference:{' '}
                <span className="font-mono font-bold text-emerald-950 bg-emerald-100 px-2 py-0.5 rounded">
                  {bookingSuccess.booking_reference}
                </span>
              </p>
            </div>
          </div>

          <div className="mt-4 pt-4 border-t border-emerald-200 grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
            <div>
              <span className="text-slate-500">Total Passengers:</span>
              <p className="font-bold text-slate-800">{bookingSuccess.total_passengers}</p>
            </div>
            <div>
              <span className="text-slate-500">Amount Paid:</span>
              <p className="font-bold text-emerald-700">₹{bookingSuccess.total_fare.toFixed(2)}</p>
            </div>
            <div>
              <span className="text-slate-500">Booking Status:</span>
              <p className="font-bold text-emerald-800">{bookingSuccess.booking_status}</p>
            </div>
            <div>
              <span className="text-slate-500">Date:</span>
              <p className="font-mono text-slate-700">
                {new Date(bookingSuccess.booking_date).toLocaleDateString()}
              </p>
            </div>
          </div>

          {bookingSuccess.tickets && bookingSuccess.tickets.length > 0 && (
            <div className="mt-4">
              <h4 className="text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">
                Allocated Ticket Permits:
              </h4>
              <div className="space-y-1">
                {bookingSuccess.tickets.map((t) => (
                  <div
                    key={t.ticket_id}
                    className="bg-white p-2.5 rounded border border-emerald-100 flex items-center justify-between text-xs"
                  >
                    <span className="font-mono font-bold text-slate-800">
                      Ticket #{t.ticket_number}
                    </span>
                    <span className="font-semibold text-sky-700">
                      Coach {t.coach_number || 'A1'} - Seat {t.seat_number || '1'} ({t.seat_class || '3A'})
                    </span>
                    <span className="font-bold text-emerald-700">₹{t.fare_amount.toFixed(2)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Search Results List */}
      {searchResults.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-sm font-bold uppercase tracking-wider text-slate-500">
            Available Train Services ({searchResults.length})
          </h2>

          <div className="grid grid-cols-1 gap-3">
            {searchResults.map((train) => (
              <div
                key={train.trip_id}
                className={`bg-white rounded-xl border p-5 transition-all shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4 ${
                  selectedTrip?.trip_id === train.trip_id
                    ? 'border-sky-500 ring-2 ring-sky-100'
                    : 'border-slate-200 hover:border-slate-300'
                }`}
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold bg-sky-50 text-sky-700 px-2 py-0.5 rounded border border-sky-100">
                      {train.service_number}
                    </span>
                    <h3 className="font-bold text-slate-900 text-base">{train.service_name}</h3>
                    <span className="text-xs px-2 py-0.5 bg-slate-100 text-slate-700 rounded-full font-medium">
                      {train.service_type}
                    </span>
                  </div>

                  <div className="flex items-center gap-4 mt-2 text-xs text-slate-500">
                    <div>
                      <span className="text-slate-400">Departure: </span>
                      <span className="font-mono font-semibold text-slate-700">
                        {new Date(train.scheduled_departure).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-400">Arrival: </span>
                      <span className="font-mono font-semibold text-slate-700">
                        {new Date(train.scheduled_arrival).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-400">Vacant Seats: </span>
                      <span className="font-bold text-emerald-600">
                        {train.available_seats} / {train.total_seats}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <span className="text-xs text-slate-400 block">Base Fare</span>
                    <span className="text-xl font-bold text-slate-900">
                      ₹{parseFloat(train.base_fare).toFixed(2)}
                    </span>
                  </div>

                  <button
                    onClick={() => handleSelectTrip(train)}
                    className={`px-4 py-2 text-xs font-semibold rounded-lg transition-colors ${
                      selectedTrip?.trip_id === train.trip_id
                        ? 'bg-sky-700 text-white'
                        : 'bg-sky-600 hover:bg-sky-500 text-white'
                    }`}
                  >
                    {selectedTrip?.trip_id === train.trip_id ? 'Viewing Seat Map' : 'Select & View Seats'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Fallback / Quick Selection: Upcoming Scheduled Journeys */}
      {searchResults.length === 0 && upcomingTrips.length > 0 && !selectedTrip && (
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div>
              <h3 className="text-sm font-bold text-slate-900">
                Upcoming Scheduled Journeys
              </h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Active calendar trips available in the database. Click any trip to view its live seat map.
              </p>
            </div>
            <Sparkles className="w-4 h-4 text-sky-500" />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {upcomingTrips.map((trip) => (
              <div
                key={trip.trip_id}
                className="p-3.5 rounded-lg border border-slate-200 hover:border-sky-400 hover:bg-sky-50/40 transition-all flex items-center justify-between gap-3"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-sky-700 bg-sky-50 px-2 py-0.5 rounded">
                      #{trip.trip_id}
                    </span>
                    <span className="font-semibold text-slate-900 text-sm">
                      {trip.service_name || `Service #${trip.service_id}`}
                    </span>
                  </div>
                  <div className="flex items-center gap-3 mt-1 text-xs text-slate-500 font-mono">
                    <span>{trip.route_code || `Route #${trip.route_id}`}</span>
                    <span>{trip.trip_date}</span>
                    <span className="font-bold text-slate-800">₹{parseFloat(trip.base_fare).toFixed(2)}</span>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => handleSelectTrip(trip)}
                  className="px-3 py-1.5 text-xs font-semibold bg-sky-600 hover:bg-sky-500 text-white rounded-lg transition-colors flex-shrink-0"
                >
                  Select Trip
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Interactive Seat Layout Map & Passenger Reservation */}
      {selectedTrip && (
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 pb-4 border-b border-slate-200">
            <div>
              <span className="font-mono text-xs font-bold text-sky-700 bg-sky-50 px-2 py-0.5 rounded">
                Trip #{selectedTrip.trip_id}
              </span>
              <h2 className="text-lg font-bold text-slate-900 mt-1">
                Seat Availability Map: {selectedTrip.service_name || `Service #${selectedTrip.service_id}`}
              </h2>
              <p className="text-xs text-slate-500">
                Pessimistic concurrency locking via SELECT ... FOR UPDATE on trip_seat_inventory
              </p>
            </div>

            {/* Seat Map Legend */}
            <div className="flex items-center gap-4 text-xs font-medium">
              <div className="flex items-center gap-1.5">
                <div className="w-3.5 h-3.5 rounded bg-emerald-50 border border-emerald-400"></div>
                <span className="text-slate-600">Available</span>
              </div>
              <div className="flex items-center gap-1.5">
                <div className="w-3.5 h-3.5 rounded bg-sky-600 text-white"></div>
                <span className="text-slate-600">Selected</span>
              </div>
              <div className="flex items-center gap-1.5">
                <div className="w-3.5 h-3.5 rounded bg-slate-200 border border-slate-300"></div>
                <span className="text-slate-400">Reserved</span>
              </div>
            </div>
          </div>

          {loadingSeats ? (
            <LoadingSpinner message="Querying real-time inventory from MySQL..." />
          ) : (
            <div>
              {seatMap.length > 0 ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 lg:grid-cols-10 gap-2.5">
                    {seatMap.map((seat) => {
                      const isSelected = selectedSeats.some((s) => s.seat_id === seat.seat_id);
                      return (
                        <button
                          key={seat.seat_id}
                          type="button"
                          disabled={!seat.is_available}
                          onClick={() => toggleSeat(seat)}
                          className={`p-2.5 rounded-lg border text-center transition-all flex flex-col items-center justify-center ${
                            isSelected
                              ? 'bg-sky-600 text-white border-sky-600 shadow-sm scale-105'
                              : seat.is_available
                              ? 'bg-emerald-50 hover:bg-emerald-100 border-emerald-300 text-emerald-950 cursor-pointer'
                              : 'bg-slate-100 border-slate-200 text-slate-400 cursor-not-allowed opacity-60'
                          }`}
                        >
                          <Armchair className="w-4 h-4 mb-1" />
                          <span className="font-mono text-xs font-bold">
                            {seat.coach_number}-{seat.seat_number}
                          </span>
                          <span className="text-[10px] opacity-75">{seat.seat_class}</span>
                        </button>
                      );
                    })}
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-xs text-slate-400">
                  No seat inventory initialized for this trip yet.
                </div>
              )}
            </div>
          )}

          {/* Passenger Information and Payment Checkout */}
          {selectedSeats.length > 0 && (
            <div className="mt-6 pt-6 border-t border-slate-200 bg-slate-50/70 p-5 rounded-xl border">
              <h3 className="text-base font-bold text-slate-900 mb-4 flex items-center gap-2">
                <User className="w-4 h-4 text-sky-600" />
                Passenger Details & Reservation Checkout
              </h3>

              {bookingError && <ErrorMessage message={bookingError} />}

              <form onSubmit={handleCompleteBooking} className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      First Name *
                    </label>
                    <input
                      type="text"
                      required
                      value={passengerDetails.first_name}
                      onChange={(e) =>
                        setPassengerDetails({ ...passengerDetails, first_name: e.target.value })
                      }
                      className="w-full px-3 py-1.5 text-sm bg-white border border-slate-200 rounded-lg focus:ring-2 focus:ring-sky-500"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      Last Name *
                    </label>
                    <input
                      type="text"
                      required
                      value={passengerDetails.last_name}
                      onChange={(e) =>
                        setPassengerDetails({ ...passengerDetails, last_name: e.target.value })
                      }
                      className="w-full px-3 py-1.5 text-sm bg-white border border-slate-200 rounded-lg focus:ring-2 focus:ring-sky-500"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      Age *
                    </label>
                    <input
                      type="number"
                      min="1"
                      max="120"
                      required
                      value={passengerDetails.age}
                      onChange={(e) =>
                        setPassengerDetails({ ...passengerDetails, age: e.target.value })
                      }
                      className="w-full px-3 py-1.5 text-sm bg-white border border-slate-200 rounded-lg focus:ring-2 focus:ring-sky-500"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      Gender *
                    </label>
                    <select
                      value={passengerDetails.gender}
                      onChange={(e) =>
                        setPassengerDetails({ ...passengerDetails, gender: e.target.value })
                      }
                      className="w-full px-3 py-1.5 text-sm bg-white border border-slate-200 rounded-lg focus:ring-2 focus:ring-sky-500"
                    >
                      <option value="MALE">Male</option>
                      <option value="FEMALE">Female</option>
                      <option value="OTHER">Other</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      ID Card Type *
                    </label>
                    <select
                      value={passengerDetails.id_card_type}
                      onChange={(e) =>
                        setPassengerDetails({ ...passengerDetails, id_card_type: e.target.value })
                      }
                      className="w-full px-3 py-1.5 text-sm bg-white border border-slate-200 rounded-lg focus:ring-2 focus:ring-sky-500"
                    >
                      <option value="AADHAAR">Aadhaar Card</option>
                      <option value="PASSPORT">Passport</option>
                      <option value="PAN">PAN Card</option>
                      <option value="VOTER_ID">Voter ID</option>
                      <option value="DRIVING_LICENSE">Driving License</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1">
                      ID Card Number *
                    </label>
                    <input
                      type="text"
                      required
                      value={passengerDetails.id_card_number}
                      onChange={(e) =>
                        setPassengerDetails({ ...passengerDetails, id_card_number: e.target.value })
                      }
                      className="w-full px-3 py-1.5 text-sm bg-white border border-slate-200 rounded-lg focus:ring-2 focus:ring-sky-500"
                    />
                  </div>
                </div>

                {/* Payment Option & Confirmation */}
                <div className="pt-4 border-t border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div className="flex items-center gap-3">
                    <span className="text-xs font-semibold text-slate-700">Payment Method:</span>
                    <select
                      value={paymentMethod}
                      onChange={(e) => setPaymentMethod(e.target.value)}
                      className="px-3 py-1.5 text-xs bg-white border border-slate-200 rounded-lg focus:ring-2 focus:ring-sky-500 font-medium"
                    >
                      <option value="UPI">UPI Instant (GPay / PhonePe)</option>
                      <option value="CREDIT_CARD">Credit Card</option>
                      <option value="DEBIT_CARD">Debit Card</option>
                      <option value="NET_BANKING">Net Banking</option>
                    </select>
                  </div>

                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <span className="text-xs text-slate-400 block">Total Fare</span>
                      <span className="text-xl font-bold text-slate-900">
                        ₹{totalFare.toFixed(2)}
                      </span>
                    </div>

                    <button
                      type="submit"
                      disabled={bookingInProgress}
                      className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-sm px-5 py-2.5 rounded-lg shadow-sm transition-colors disabled:opacity-50"
                    >
                      <ShieldCheck className="w-4 h-4" />
                      <span>{bookingInProgress ? 'Processing Transaction...' : 'Pay & Confirm Reservation'}</span>
                    </button>
                  </div>
                </div>
              </form>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Booking;
