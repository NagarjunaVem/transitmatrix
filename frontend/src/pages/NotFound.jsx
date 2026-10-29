import React from 'react';
import { Link } from 'react-router-dom';
import { Train, Home } from 'lucide-react';

const NotFound = () => {
  return (
    <div className="max-w-md mx-auto my-20 text-center">
      <div className="w-16 h-16 bg-slate-100 text-slate-400 rounded-full flex items-center justify-center mx-auto mb-4">
        <Train className="w-8 h-8" />
      </div>
      <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">404</h1>
      <h2 className="text-lg font-bold text-slate-800 mt-2">Station Not Found</h2>
      <p className="text-xs text-slate-500 mt-1">
        The route or view you requested does not exist on this transit corridor.
      </p>
      <Link
        to="/"
        className="inline-flex items-center gap-1.5 mt-6 px-4 py-2 text-xs font-semibold bg-sky-600 hover:bg-sky-500 text-white rounded-lg shadow-sm transition-colors"
      >
        <Home className="w-4 h-4" />
        <span>Return to Dashboard</span>
      </Link>
    </div>
  );
};

export default NotFound;
