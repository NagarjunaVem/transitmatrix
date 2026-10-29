// Utility helper to safely format FastAPI and Axios error responses
// Prevents React from crashing when FastAPI returns an array of Pydantic validation errors

export const formatErrorMessage = (err, fallback = 'An unexpected error occurred.') => {
  if (!err) return fallback;

  const detail = err.response?.data?.detail;
  if (!detail) {
    return err.message || fallback;
  }

  if (typeof detail === 'string') {
    return detail;
  }

  // Handle FastAPI Pydantic validation error lists: [{loc: [...], msg: "..."}]
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        const field = item.loc ? item.loc[item.loc.length - 1] : 'Field';
        return `${field}: ${item.msg || 'Invalid value'}`;
      })
      .join(' | ');
  }

  if (typeof detail === 'object' && detail !== null) {
    return JSON.stringify(detail);
  }

  return String(detail);
};
