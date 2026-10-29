import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Train, Lock, User, AlertCircle } from 'lucide-react';
import { formatErrorMessage } from '../utils/formatError';

const Login = () => {
  const [username, setUsername] = useState('admin_sys');
  const [password, setPassword] = useState('SuperSecretPassword123!');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await login(username, password);
      navigate('/');
    } catch (err) {
      console.error('Login failed:', err);
      const parsedError = formatErrorMessage(
        err,
        'Login failed. Please verify credentials or register a new account.'
      );
      setError(parsedError);
    } finally {
      setLoading(false);
    }
  };

  // Quick fill helper for testing/presentation
  const fillRole = (u, p) => {
    setUsername(u);
    setPassword(p);
  };

  return (
    <div className="max-w-md mx-auto my-12">
      <div className="bg-white rounded-2xl border border-slate-200 p-8 shadow-sm">
        <div className="text-center mb-6">
          <div className="w-12 h-12 bg-sky-500 text-slate-950 rounded-xl flex items-center justify-center mx-auto mb-3 shadow-sm">
            <Train className="w-7 h-7" />
          </div>
          <h2 className="text-2xl font-bold text-slate-900 tracking-tight">System Login</h2>
          <p className="text-xs text-slate-500 mt-1">
            Access TransitMatrix via JWT Bearer Authentication
          </p>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-xs text-red-700 flex items-start gap-2">
            <AlertCircle className="w-4 h-4 text-red-600 mt-0.5 flex-shrink-0" />
            <span className="break-words">{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Username
            </label>
            <div className="relative">
              <User className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full pl-9 pr-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500 font-medium"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Password
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-9 pr-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500 font-medium"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 bg-sky-600 hover:bg-sky-500 text-white font-semibold text-sm rounded-lg shadow-sm transition-colors disabled:opacity-50"
          >
            {loading ? 'Authenticating...' : 'Sign In'}
          </button>
        </form>

        {/* Quick Demo Credentials Preset */}
        <div className="mt-6 pt-5 border-t border-slate-200 text-xs">
          <p className="font-semibold text-slate-500 uppercase tracking-wider text-[10px] mb-2">
            Demonstration Roles:
          </p>
          <div className="grid grid-cols-3 gap-2">
            <button
              type="button"
              onClick={() => fillRole('admin_sys', 'SuperSecretPassword123!')}
              className="px-2 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded font-medium text-center"
            >
              Admin
            </button>
            <button
              type="button"
              onClick={() => fillRole('staff_ndls', 'SuperSecretPassword123!')}
              className="px-2 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded font-medium text-center"
            >
              Staff
            </button>
            <button
              type="button"
              onClick={() => fillRole('user_8', 'SuperSecretPassword123!')}
              className="px-2 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded font-medium text-center"
            >
              Passenger
            </button>
          </div>
        </div>

        <div className="mt-4 text-center text-xs text-slate-500">
          Don't have an account?{' '}
          <Link to="/register" className="font-semibold text-sky-600 hover:underline">
            Register Profile
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Login;
