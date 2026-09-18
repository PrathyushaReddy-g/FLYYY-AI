import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  Shield,
  LayoutDashboard,
  Database,
  Search,
  Sliders,
  Layers,
  Users,
  Mail,
  RefreshCw,
  KeyRound,
  FileText,
  Network,
  LogOut,
  User as UserIcon
} from 'lucide-react';
import { User } from '../types';

interface SidebarProps {
  user: User | null;
  onLogout: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ user, onLogout }) => {
  const navigate = useNavigate();

  const navItems = [
    { to: '/', label: 'Main Dashboard', icon: LayoutDashboard },
    { to: '/sources', label: 'Source & Batch Config', icon: Database },
    { to: '/discovery', label: 'Data Discovery', icon: Search },
    { to: '/policies', label: 'Protection Policies', icon: Sliders },
    { to: '/batches', label: 'Batch Monitor', icon: Layers },
    { to: '/customers', label: 'Protected Customers', icon: Users },
    { to: '/marketing', label: 'Marketing Demo', icon: Mail },
    { to: '/bounce', label: 'Bounce Simulator', icon: RefreshCw },
    { to: '/reveal', label: 'Controlled Reveal', icon: KeyRound },
    { to: '/audit', label: 'Audit Dashboard', icon: FileText },
    { to: '/architecture', label: 'System Architecture', icon: Network },
  ];

  const roleColors: Record<string, string> = {
    ADMIN: 'bg-red-950/80 text-red-400 border-red-800',
    MARKETING: 'bg-blue-950/80 text-blue-400 border-blue-800',
    CUSTOMER_SUPPORT: 'bg-emerald-950/80 text-emerald-400 border-emerald-800',
    AUDITOR: 'bg-purple-950/80 text-purple-400 border-purple-800',
  };

  return (
    <aside className="w-64 bg-[#0F172A] border-r border-slate-800 flex flex-col h-screen select-none sticky top-0">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800 flex items-center space-x-3">
        <div className="w-10 h-10 rounded-lg bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400">
          <Shield className="w-6 h-6" />
        </div>
        <div>
          <div className="font-bold text-base tracking-wide text-white flex items-center space-x-1">
            <span>FLYYY.AI</span>
          </div>
          <p className="text-[10px] text-blue-400 font-semibold tracking-wider uppercase">Privacy CDP</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center px-3 py-2 text-xs font-medium rounded-lg transition-colors ${
                  isActive
                    ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`
              }
            >
              <Icon className="w-4 h-4 mr-3 flex-shrink-0" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* User Badge & Logout */}
      <div className="p-4 border-t border-slate-800 bg-[#0B1120]">
        <div className="flex items-center space-x-3 mb-3">
          <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300">
            <UserIcon className="w-4 h-4" />
          </div>
          <div className="overflow-hidden">
            <div className="text-xs font-semibold text-slate-200 truncate">{user?.username || 'Guest'}</div>
            <span
              className={`text-[9px] px-1.5 py-0.5 rounded border font-mono uppercase tracking-wider inline-block ${
                roleColors[user?.role || 'ADMIN'] || 'bg-slate-800 text-slate-400'
              }`}
            >
              {user?.role || 'ANONYMOUS'}
            </span>
          </div>
        </div>

        <button
          onClick={onLogout}
          className="w-full flex items-center justify-center px-3 py-1.5 text-xs text-slate-400 hover:text-red-400 hover:bg-red-950/30 rounded border border-slate-800 hover:border-red-900/50 transition"
        >
          <LogOut className="w-3.5 h-3.5 mr-2" />
          <span>Sign Out</span>
        </button>
      </div>
    </aside>
  );
};
