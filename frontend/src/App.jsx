import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './context/AuthContext';
import ErrorBoundary from './components/ErrorBoundary';

import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import ProtectedRoute from './components/ProtectedRoute';

import Dashboard from './pages/Dashboard';
import StationsRoutes from './pages/StationsRoutes';
import ServicesTimetables from './pages/ServicesTimetables';
import Booking from './pages/Booking';
import MyBookings from './pages/MyBookings';
import Reports from './pages/Reports';
import DatabaseLab from './pages/DatabaseLab';
import MLForecast from './pages/MLForecast';
import Login from './pages/Login';
import Register from './pages/Register';
import NotFound from './pages/NotFound';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <Router>
            <div className="min-h-screen bg-slate-50 flex flex-col">
              <Navbar />
              <div className="flex-1 flex">
                <Sidebar />
                <main className="flex-1 p-6 max-w-7xl w-full mx-auto overflow-y-auto">
                  <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/stations-routes" element={<StationsRoutes />} />
                    <Route path="/services-timetables" element={<ServicesTimetables />} />
                    <Route path="/booking" element={<Booking />} />
                    <Route
                      path="/my-bookings"
                      element={
                        <ProtectedRoute>
                          <MyBookings />
                        </ProtectedRoute>
                      }
                    />
                    <Route
                      path="/reports"
                      element={
                        <ProtectedRoute allowedRoles={['ADMIN', 'STAFF']}>
                          <Reports />
                        </ProtectedRoute>
                      }
                    />
                    <Route
                      path="/database-lab"
                      element={
                        <ProtectedRoute allowedRoles={['ADMIN', 'STAFF']}>
                          <DatabaseLab />
                        </ProtectedRoute>
                      }
                    />
                    <Route path="/ml-forecast" element={<MLForecast />} />
                    <Route path="/login" element={<Login />} />
                    <Route path="/register" element={<Register />} />
                    <Route path="*" element={<NotFound />} />
                  </Routes>
                </main>
              </div>
            </div>
          </Router>
        </AuthProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;
