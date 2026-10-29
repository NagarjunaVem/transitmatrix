import React from 'react';
import { AlertCircle } from 'lucide-react';

const ErrorMessage = ({ message, onRetry }) => {
  // Format message if it is an object, array of Pydantic errors, or string
  let displayMessage = message;
  if (Array.isArray(message)) {
    displayMessage = message
      .map((item) => {
        const field = item.loc ? item.loc[item.loc.length - 1] : 'Field';
        return `${field}: ${item.msg || 'Invalid value'}`;
      })
      .join(' | ');
  } else if (typeof message === 'object' && message !== null) {
    displayMessage = message.detail || message.msg || message.message || JSON.stringify(message);
  }

  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3 my-4">
      <AlertCircle className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
      <div className="flex-1">
        <h4 className="text-sm font-semibold text-red-800">Notice</h4>
        <p className="text-sm text-red-700 mt-1 break-words">
          {String(displayMessage || 'Unable to complete request.')}
        </p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="mt-2 text-xs font-semibold text-red-800 underline hover:text-red-900"
          >
            Try Again
          </button>
        )}
      </div>
    </div>
  );
};

export default ErrorMessage;
