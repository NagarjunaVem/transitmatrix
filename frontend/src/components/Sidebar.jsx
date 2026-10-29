import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  LayoutDashboard,
  Ticket,
  CalendarCheck,
  MapPin,
  Clock,
  BarChart3,
  Database,
  Cpu,
  Bookmark,
} from 'lucide-react';

const Sidebar = () => {
  const { user, isStaff, isAuthenticated } = useAuth();

  const navLinks = [
    { to: '/', label: 'Dashboard', icon: LayoutDashboard, public: true },
    { to: '/booking', label: 'Book Ticket', icon: Ticket, public: true },
    { to: '/my-bookings', label: 'My Bookings', icon: Bookmark, authOnly: true },
    { to: '/stations-routes', label: 'Stations & Routes', icon: MapPin, public: true },
    { to: '/services-timetables', label: 'Services & Schedule', icon: Clock, public: true },
    { to: '/reports', label: 'Reports & Analytics', icon: BarChart3, staffOnly: true },
    { to: '/database-lab', label: 'Database Lab (21 SQL)', icon: Database, staffOnly: true },
    { to: '/ml-forecast', label: 'AI Demand Forecast', icon: Cpu, public: true },
  ];

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 text-slate-300 flex-shrink-0 min-h-[calc(100vh-4rem)] p-4 flex flex-col justify-between">
      <div>
        <div className="px-3 pb-3 mb-2 border-b border-slate-800">
          <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
            System Modules
          </p>
        </div>

        <nav className="space-y-1">
          {navLinks.map((item) => {
            // Filter by authentication or staff role
            if (item.authOnly && !isAuthenticated) return null;
            if (item.staffOnly && !isStaff) return null;

            const Icon = item.icon;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/'}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-sky-600 text-white font-semibold shadow-sm'
                      : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                  }`
                }
              >
                <Icon className="w-4 h-4 flex-shrink-0" />
                <span>{item.label}</span>
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Database status footer info */}
      <div className="mt-8 pt-4 border-t border-slate-800 px-3 text-xs text-slate-400">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
          <span className="font-medium text-slate-300">MySQL 8.0+ Raw SQL</span>
        </div>
        <p className="mt-1 text-[11px] text-slate-400">InnoDB Concurrency & Zero-ORM</p>
      </div>
    </aside>
  );
};

export default Sidebar;
