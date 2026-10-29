import React from 'react';

const LoadingSpinner = ({ message = 'Loading data...' }) => {
  return (
    <div className="flex flex-col items-center justify-center p-12">
      <div className="w-10 h-10 border-4 border-sky-200 border-t-sky-600 rounded-full animate-spin"></div>
      <p className="mt-3 text-sm text-slate-500 font-medium">{message}</p>
    </div>
  );
};

export default LoadingSpinner;
