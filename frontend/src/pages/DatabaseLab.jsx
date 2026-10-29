import React, { useState, useEffect } from 'react';
import api from '../api/client';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import {
  Database,
  Play,
  Clock,
  Layers,
  FileCode,
  CheckCircle,
  HelpCircle,
  ShieldAlert,
  ArrowRight,
  GitBranch,
  Key,
  Terminal,
} from 'lucide-react';

const DatabaseLab = () => {
  const [activeTab, setActiveTab] = useState('queries'); // 'queries' | 'er_diagram' | 'normalization'
  const [catalog, setCatalog] = useState([]);
  const [loadingCatalog, setLoadingCatalog] = useState(true);
  const [catalogError, setCatalogError] = useState(null);

  // Query Execution State
  const [selectedQueryId, setSelectedQueryId] = useState('Q01');
  const [executing, setExecuting] = useState(false);
  const [executionResult, setExecutionResult] = useState(null);
  const [executionError, setExecutionError] = useState(null);

  useEffect(() => {
    const fetchCatalog = async () => {
      setLoadingCatalog(true);
      setCatalogError(null);
      try {
        const res = await api.get('/database-lab/catalog');
        setCatalog(res.data || []);
        if (res.data && res.data.length > 0) {
          setSelectedQueryId(res.data[0].query_id);
          // Query selected without auto-running so the user can click Run Query manually
          setExecutionResult(null);
        }
      } catch (err) {
        console.error('Failed to load database lab catalog:', err);
        setCatalogError('Could not fetch the 21 SQL demonstration queries from backend.');
      } finally {
        setLoadingCatalog(false);
      }
    };
    fetchCatalog();
  }, []);

  const handleSelectQuery = (queryId) => {
    setSelectedQueryId(queryId);
    setExecutionResult(null);
    setExecutionError(null);
  };

  const runQuery = async (queryId) => {
    setSelectedQueryId(queryId);
    setExecuting(true);
    setExecutionError(null);
    try {
      const res = await api.get(`/database-lab/execute/${queryId}`);
      setExecutionResult(res.data);
    } catch (err) {
      console.error(`Failed to execute query ${queryId}:`, err);
      setExecutionError(err.response?.data?.detail || `Execution failed for query ${queryId}`);
      setExecutionResult(null);
    } finally {
      setExecuting(false);
    }
  };

  const selectedItem = catalog.find((q) => q.query_id === selectedQueryId);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-2 border-b border-slate-200">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Database Lab & SQL Workbench
          </h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Live execution of 21 relational SQL demonstrations, EXPLAIN plans, normalization theory, and ER model
          </p>
        </div>

        {/* Tab Controls */}
        <div className="bg-slate-200 p-1 rounded-lg flex text-xs font-semibold">
          <button
            onClick={() => setActiveTab('queries')}
            className={`px-3 py-1.5 rounded-md transition-all ${
              activeTab === 'queries' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            21 SQL Demonstrations
          </button>
          <button
            onClick={() => setActiveTab('er_diagram')}
            className={`px-3 py-1.5 rounded-md transition-all ${
              activeTab === 'er_diagram' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            ER Model & Schema (18 Tables)
          </button>
          <button
            onClick={() => setActiveTab('normalization')}
            className={`px-3 py-1.5 rounded-md transition-all ${
              activeTab === 'normalization' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Normalization & FDs
          </button>
        </div>
      </div>

      {catalogError && <ErrorMessage message={catalogError} />}

      {/* Main Tab 1: 21 SQL Demonstrations */}
      {activeTab === 'queries' && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Query Selector Sidebar */}
          <div className="lg:col-span-4 bg-white rounded-xl border border-slate-200 p-4 shadow-sm max-h-[750px] overflow-y-auto space-y-1.5">
            <div className="px-2 pb-2 mb-1 border-b border-slate-100 flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                SQL Query Catalog
              </span>
              <span className="text-xs font-mono bg-sky-50 text-sky-700 px-2 py-0.5 rounded font-bold">
                {catalog.length} Queries
              </span>
            </div>

            {loadingCatalog ? (
              <LoadingSpinner message="Loading catalog..." />
            ) : (
              catalog.map((q) => (
                <button
                  key={q.query_id}
                  onClick={() => handleSelectQuery(q.query_id)}
                  className={`w-full text-left p-3 rounded-lg border text-xs transition-all ${
                    selectedQueryId === q.query_id
                      ? 'border-sky-500 bg-sky-50/70 text-slate-900 shadow-sm'
                      : 'border-slate-100 hover:border-slate-200 hover:bg-slate-50 text-slate-600'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-mono font-bold text-sky-700">{q.query_id}</span>
                    <span className="text-[10px] uppercase font-semibold bg-slate-100 px-1.5 py-0.5 rounded text-slate-500">
                      {q.category}
                    </span>
                  </div>
                  <div className="font-semibold text-slate-800 line-clamp-1">{q.title}</div>
                  <div className="text-[11px] text-slate-400 line-clamp-1 mt-0.5">
                    {q.description}
                  </div>
                </button>
              ))
            )}
          </div>

          {/* Query Execution Workspace */}
          <div className="lg:col-span-8 space-y-5">
            {selectedItem && (
              <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-200">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs font-bold bg-sky-100 text-sky-800 px-2 py-0.5 rounded">
                        {selectedItem.query_id}
                      </span>
                      <h2 className="text-base font-bold text-slate-900">{selectedItem.title}</h2>
                    </div>
                    <p className="text-xs text-slate-500 mt-1">{selectedItem.description}</p>
                  </div>

                  <button
                    onClick={() => runQuery(selectedItem.query_id)}
                    disabled={executing}
                    className="flex items-center gap-1.5 bg-sky-600 hover:bg-sky-500 text-white font-semibold text-xs px-4 py-2 rounded-lg shadow-sm transition-colors disabled:opacity-50 flex-shrink-0"
                  >
                    <Play className="w-3.5 h-3.5 fill-current" />
                    <span>{executing ? 'Executing SQL...' : 'Run Query'}</span>
                  </button>
                </div>

                {/* Raw SQL Statement Preview */}
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                      Actual Raw SQL Statement
                    </span>
                    <span className="text-[11px] font-mono text-slate-400">MySQL 8.0 Syntax</span>
                  </div>
                  <pre className="bg-slate-950 text-sky-300 p-4 rounded-xl font-mono text-xs overflow-x-auto leading-relaxed border border-slate-800">
                    <code>{selectedItem.sql_statement}</code>
                  </pre>
                </div>
              </div>
            )}

            {/* If not yet executed, show invitation banner */}
            {!executionResult && !executionError && !executing && (
              <div className="bg-white rounded-xl border border-dashed border-slate-300 p-8 text-center">
                <Terminal className="w-8 h-8 text-slate-400 mx-auto mb-2" />
                <h4 className="text-sm font-bold text-slate-800">Ready to Execute</h4>
                <p className="text-xs text-slate-500 mt-1">
                  Click the blue <strong>"Run Query"</strong> button above to execute this query live against MySQL and display its measured runtime and query plan.
                </p>
              </div>
            )}

            {/* Results Output Section */}
            {executionError && <ErrorMessage message={executionError} />}

            {executionResult && (
              <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                {/* Result Statistics Bar */}
                <div className="bg-slate-50 px-5 py-3 border-b border-slate-200 flex items-center justify-between text-xs">
                  <div className="flex items-center gap-4">
                    <span className="flex items-center gap-1.5 font-semibold text-slate-700">
                      <CheckCircle className="w-4 h-4 text-emerald-600" />
                      Status: Executed Successfully
                    </span>
                    <span className="text-slate-400">|</span>
                    <span className="flex items-center gap-1 text-slate-600 font-mono">
                      <Clock className="w-3.5 h-3.5 text-slate-400" />
                      Runtime: {executionResult.execution_time_ms.toFixed(2)} ms
                    </span>
                    <span className="text-slate-400">|</span>
                    <span className="font-semibold text-slate-700">
                      Rows Returned: {executionResult.row_count}
                    </span>
                  </div>
                </div>

                {/* Result Table */}
                <div className="overflow-x-auto max-h-96">
                  {executionResult.rows && executionResult.rows.length > 0 ? (
                    <table className="w-full text-left text-xs text-slate-600 font-mono">
                      <thead className="bg-slate-100 text-slate-700 uppercase tracking-wider border-b border-slate-200 sticky top-0">
                        <tr>
                          {executionResult.columns.map((col) => (
                            <th key={col} className="px-4 py-2.5 whitespace-nowrap">
                              {col}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {executionResult.rows.map((row, rIdx) => (
                          <tr key={rIdx} className="hover:bg-slate-50">
                            {executionResult.columns.map((col) => (
                              <td key={col} className="px-4 py-2 whitespace-nowrap">
                                {row[col] !== null && row[col] !== undefined ? '' + row[col] : 'NULL'}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : (
                    <div className="p-8 text-center text-xs text-slate-400">
                      Query executed cleanly with zero rows returned or performed a DDL/DML mutation.
                    </div>
                  )}
                </div>

                {/* EXPLAIN Execution Plan Dropdown */}
                {executionResult.explain_plan && executionResult.explain_plan.length > 0 && (
                  <div className="p-4 border-t border-slate-200 bg-slate-50/50">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-600 mb-2">
                      MySQL EXPLAIN Query Optimization Plan:
                    </h4>
                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-[11px] text-slate-600 font-mono">
                        <thead className="bg-slate-200/70 text-slate-700 uppercase">
                          <tr>
                            <th className="px-3 py-1.5">ID</th>
                            <th className="px-3 py-1.5">Select Type</th>
                            <th className="px-3 py-1.5">Table</th>
                            <th className="px-3 py-1.5">Type</th>
                            <th className="px-3 py-1.5">Possible Keys</th>
                            <th className="px-3 py-1.5">Key Used</th>
                            <th className="px-3 py-1.5">Rows</th>
                            <th className="px-3 py-1.5">Extra</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-200 bg-white">
                          {executionResult.explain_plan.map((plan, pIdx) => (
                            <tr key={pIdx}>
                              <td className="px-3 py-1.5">{plan.id}</td>
                              <td className="px-3 py-1.5">{plan.select_type}</td>
                              <td className="px-3 py-1.5 font-bold text-sky-700">{plan.table}</td>
                              <td className="px-3 py-1.5">{plan.type}</td>
                              <td className="px-3 py-1.5">{plan.possible_keys || '-'}</td>
                              <td className="px-3 py-1.5 font-bold text-emerald-700">{plan.key || '-'}</td>
                              <td className="px-3 py-1.5">{plan.rows}</td>
                              <td className="px-3 py-1.5 text-slate-400">{plan.Extra || '-'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Main Tab 2: ER Model & Relational Schema (18 Tables) */}
      {activeTab === 'er_diagram' && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
            <h3 className="text-base font-bold text-slate-900 mb-1">
              TransitMatrix Relational Architecture (18 Tables)
            </h3>
            <p className="text-xs text-slate-500 mb-6">
              Normalized schema enforcing referential integrity with foreign key constraints on MySQL InnoDB
            </p>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[
                { name: 'users', pk: 'user_id', count: '10+', role: 'Authentication & RBAC credentials' },
                { name: 'passengers', pk: 'passenger_id', count: '200+', role: 'Traveler demographic profiles' },
                { name: 'stations', pk: 'station_id', count: '30+', role: 'Station terminals & coordinates' },
                { name: 'routes', pk: 'route_id', count: '18+', role: 'Transit corridors & distances' },
                { name: 'route_stops', pk: 'stop_id', count: '80+', role: 'Ordered intermediate halts & sequences' },
                { name: 'services', pk: 'service_id', count: '20+', role: 'Train service catalog (Express, Rajdhani)' },
                { name: 'vehicles', pk: 'vehicle_id', count: '15+', role: 'Rolling stock rakes & locomotives' },
                { name: 'seats', pk: 'seat_id', count: '120+', role: 'Physical coach seats & fare multipliers' },
                { name: 'trips', pk: 'trip_id', count: '100+', role: 'Calendar scheduled journey instances' },
                { name: 'trip_seat_inventory', pk: 'inventory_id', count: '5,000+', role: 'Row-level concurrency inventory locking' },
                { name: 'bookings', pk: 'booking_id', count: '500+', role: 'Reservation headers with PNR references' },
                { name: 'tickets', pk: 'ticket_id', count: '800+', role: 'Individual passenger seat travel permits' },
                { name: 'payments', pk: 'payment_id', count: '500+', role: 'Settlement receipts & gateway traces' },
                { name: 'cancellations', pk: 'cancellation_id', count: '50+', role: 'Refund calculations & audit deductions' },
                { name: 'waitlists', pk: 'waitlist_id', count: '30+', role: 'FIFO queue for waitlisted passengers' },
                { name: 'delays', pk: 'delay_id', count: '40+', role: 'Operational station delay incident logs' },
                { name: 'audit_logs', pk: 'log_id', count: '200+', role: 'Immutable DML mutation audit trail' },
                { name: 'demand_predictions', pk: 'prediction_id', count: '100+', role: 'AI/ML corridor passenger forecasts' },
              ].map((table) => (
                <div key={table.name} className="border border-slate-200 rounded-lg p-4 bg-slate-50/50">
                  <div className="flex items-center justify-between">
                    <span className="font-mono font-bold text-sky-800 text-sm">{table.name}</span>
                    <span className="text-[10px] bg-slate-200 text-slate-700 px-2 py-0.5 rounded font-mono">
                      PK: {table.pk}
                    </span>
                  </div>
                  <p className="text-xs text-slate-600 mt-2">{table.role}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Main Tab 3: Normalization & Functional Dependencies */}
      {activeTab === 'normalization' && (
        <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm space-y-6">
          <div>
            <h3 className="text-base font-bold text-slate-900">
              Database Normalization & Functional Dependencies Proof
            </h3>
            <p className="text-xs text-slate-500 mt-1">
              Rigorous relational decomposition preventing insertion, update, and deletion anomalies
            </p>
          </div>

          <div className="space-y-4 text-xs text-slate-700">
            <div className="border border-slate-200 rounded-lg p-4 bg-slate-50">
              <h4 className="font-bold text-slate-900 mb-1">1. First Normal Form (1NF)</h4>
              <p>
                All table attributes are strictly atomic. No repeating groups or multi-valued attributes exist.
                For example, intermediate route halts are not stored as comma-separated values inside the `routes` table;
                they are decomposed into independent 1NF tuple rows in `route_stops`.
              </p>
            </div>

            <div className="border border-slate-200 rounded-lg p-4 bg-slate-50">
              <h4 className="font-bold text-slate-900 mb-1">2. Second Normal Form (2NF)</h4>
              <p>
                The schema is in 1NF and contains no partial functional dependencies on composite candidate keys.
                In composite entities such as `route_stops(route_id, station_id)` or `trip_seat_inventory(trip_id, seat_id)`,
                attributes such as `distance_from_origin_km` depend on the full composite key, while non-key attributes
                like `station_name` are extracted to `stations` table.
              </p>
            </div>

            <div className="border border-slate-200 rounded-lg p-4 bg-slate-50">
              <h4 className="font-bold text-slate-900 mb-1">3. Third Normal Form (3NF) & BCNF</h4>
              <p>
                Every non-prime attribute is non-transitively dependent on the primary key ($X \to Y \implies X$ is a superkey).
                In `bookings`, user attributes (first name, email, phone) are referenced via foreign key `user_id`,
                avoiding transitive dependencies ($booking\_id \to user\_id \to email$).
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DatabaseLab;
