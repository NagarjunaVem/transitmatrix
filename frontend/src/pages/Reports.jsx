import React, { useState, useEffect } from 'react';
import api from '../api/client';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import {
  BarChart3,
  Download,
  Calendar,
  TrendingUp,
  AlertTriangle,
  FileSpreadsheet,
  Layers,
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
} from 'recharts';

const Reports = () => {
  const [activeReport, setActiveReport] = useState('route_performance'); // 'route_performance' | 'monthly_revenue' | 'delay_summary'
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchReport = async (reportType) => {
    setLoading(true);
    setError(null);
    try {
      let endpoint = '/reports/route-performance';
      if (reportType === 'monthly_revenue') endpoint = '/reports/monthly-revenue';
      if (reportType === 'delay_summary') endpoint = '/reports/delay-summary';

      const res = await api.get(endpoint);
      setData(res.data || []);
    } catch (err) {
      console.error('Error fetching report:', err);
      setError('Unable to load analytical report from MySQL.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReport(activeReport);
  }, [activeReport]);

  // Export current table records to CSV
  const exportToCSV = () => {
    if (!data || data.length === 0) return;

    const headers = Object.keys(data[0]);
    const csvRows = [];
    csvRows.push(headers.join(','));

    for (const row of data) {
      const values = headers.map((header) => {
        const val = row[header] !== null && row[header] !== undefined ? row[header] : '';
        const escaped = ('' + val).replace(/"/g, '""');
        return `"${escaped}"`;
      });
      csvRows.push(values.join(','));
    }

    const csvString = csvRows.join('\n');
    const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `transitmatrix_${activeReport}_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-2 border-b border-slate-200">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Analytical Reports & Auditing
          </h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Commercial KPIs, monthly revenue manifests, delay metrics, and CSV exports
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={exportToCSV}
            disabled={loading || data.length === 0}
            className="flex items-center gap-1.5 text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white px-3.5 py-2 rounded-lg shadow-sm transition-colors disabled:opacity-50"
          >
            <Download className="w-4 h-4" />
            <span>Export to CSV</span>
          </button>
        </div>
      </div>

      {/* Report Selector Tabs */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => setActiveReport('route_performance')}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-xs font-semibold transition-all border ${
            activeReport === 'route_performance'
              ? 'bg-sky-600 text-white border-sky-600 shadow-sm'
              : 'bg-white text-slate-600 hover:bg-slate-50 border-slate-200'
          }`}
        >
          <TrendingUp className="w-4 h-4" />
          <span>Route Performance (v_route_performance)</span>
        </button>

        <button
          onClick={() => setActiveReport('monthly_revenue')}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-xs font-semibold transition-all border ${
            activeReport === 'monthly_revenue'
              ? 'bg-sky-600 text-white border-sky-600 shadow-sm'
              : 'bg-white text-slate-600 hover:bg-slate-50 border-slate-200'
          }`}
        >
          <Calendar className="w-4 h-4" />
          <span>Monthly Revenue (v_monthly_revenue)</span>
        </button>

        <button
          onClick={() => setActiveReport('delay_summary')}
          className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-xs font-semibold transition-all border ${
            activeReport === 'delay_summary'
              ? 'bg-sky-600 text-white border-sky-600 shadow-sm'
              : 'bg-white text-slate-600 hover:bg-slate-50 border-slate-200'
          }`}
        >
          <AlertTriangle className="w-4 h-4" />
          <span>Delay Summary (v_delay_summary)</span>
        </button>
      </div>

      {error && <ErrorMessage message={error} onRetry={() => fetchReport(activeReport)} />}

      {/* Visual Chart if Route Performance is active */}
      {activeReport === 'route_performance' && data.length > 0 && !loading && (
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
          <h3 className="text-sm font-bold text-slate-900 mb-2">Net Corridor Earnings Comparison</h3>
          <p className="text-xs text-slate-500 mb-4">Gross revenue minus refunds across top corridors</p>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.slice(0, 8)} margin={{ top: 10, right: 10, left: 0, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="route_code" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip
                  formatter={(val) => [`₹${val.toLocaleString()}`, 'Net Revenue']}
                  contentStyle={{ backgroundColor: '#0f172a', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                />
                <Bar dataKey="net_revenue" name="Net Revenue (₹)" fill="#0284c7" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Dynamic Data Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {loading ? (
          <LoadingSpinner message="Querying MySQL reporting view..." />
        ) : (
          <div className="overflow-x-auto">
            {data.length > 0 ? (
              <table className="w-full text-left text-sm text-slate-600">
                <thead className="bg-slate-50 text-xs font-semibold text-slate-500 uppercase tracking-wider border-b border-slate-200">
                  <tr>
                    {Object.keys(data[0]).map((col) => (
                      <th key={col} className="px-5 py-3 whitespace-nowrap">
                        {col.replace(/_/g, ' ')}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-mono text-xs">
                  {data.map((row, idx) => (
                    <tr key={idx} className="hover:bg-slate-50 transition-colors">
                      {Object.keys(row).map((col) => (
                        <td key={col} className="px-5 py-3 whitespace-nowrap">
                          {typeof row[col] === 'number'
                            ? col.includes('revenue') || col.includes('amount') || col.includes('fare')
                              ? `₹${row[col].toLocaleString('en-IN', { maximumFractionDigits: 2 })}`
                              : row[col]
                            : row[col] !== null
                            ? '' + row[col]
                            : '-'}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="p-8 text-center text-xs text-slate-400">
                No records returned from view.
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Reports;
