import React, { useEffect, useState } from 'react';
import {
  Database,
  ShieldCheck,
  Search,
  Layers,
  FileText,
  Mail,
  RefreshCw,
  Lock,
  Unlock,
  Activity,
  CheckCircle2,
  AlertTriangle
} from 'lucide-react';
import { dashboardService } from '../services/api';
import { DashboardStats } from '../types';

export const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [health, setHealth] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const [statsData, healthData] = await Promise.all([
        dashboardService.getStats(),
        dashboardService.getHealth()
      ]);
      setStats(statsData);
      setHealth(healthData);
    } catch (err) {
      console.error('Failed to load dashboard metrics', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 8000);
    return () => clearInterval(interval);
  }, []);

  if (loading && !stats) {
    return (
      <div className="p-8 flex items-center justify-center text-slate-400 text-xs">
        <Activity className="w-5 h-5 mr-2 animate-spin text-blue-500" />
        Loading real-time platform telemetry...
      </div>
    );
  }

  const kpis = [
    { label: 'Source Records', value: stats?.total_source_records ?? 0, icon: Database, color: 'text-cyan-400', border: 'border-cyan-800/40' },
    { label: 'Protected Records', value: stats?.protected_records ?? 0, icon: ShieldCheck, color: 'text-blue-400', border: 'border-blue-800/40' },
    { label: 'Discovered PII Fields', value: stats?.discovered_pii_fields ?? 0, icon: Search, color: 'text-amber-400', border: 'border-amber-800/40' },
    { label: 'Processed Rows', value: stats?.processed_rows ?? 0, icon: Layers, color: 'text-indigo-400', border: 'border-indigo-800/40' },
    { label: 'Total Audit Events', value: stats?.audit_events ?? 0, icon: FileText, color: 'text-purple-400', border: 'border-purple-800/40' },
    { label: 'Email Dispatches', value: stats?.email_operations ?? 0, icon: Mail, color: 'text-emerald-400', border: 'border-emerald-800/40' },
    { label: 'Bounce Callbacks', value: stats?.bounce_events ?? 0, icon: RefreshCw, color: 'text-teal-400', border: 'border-teal-800/40' },
    { label: 'Denied Reveals', value: stats?.denied_reveals ?? 0, icon: Lock, color: 'text-rose-400', border: 'border-rose-800/40' },
    { label: 'Allowed Reveals', value: stats?.allowed_reveals ?? 0, icon: Unlock, color: 'text-green-400', border: 'border-green-800/40' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">Security & Privacy Operations Center</h1>
          <p className="text-xs text-slate-400 mt-0.5">Real-time telemetry across multi-database privacy pipeline</p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="flex h-2 w-2 relative">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span className="text-[11px] font-mono text-emerald-400 uppercase tracking-wider">LIVE TELEMETRY</span>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-3 gap-4">
        {kpis.map((kpi) => {
          const Icon = kpi.icon;
          return (
            <div
              key={kpi.label}
              className={`bg-[#0F172A] border ${kpi.border} rounded-xl p-4 shadow-sm hover:border-slate-700 transition`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-medium text-slate-400">{kpi.label}</span>
                <Icon className={`w-4 h-4 ${kpi.color}`} />
              </div>
              <div className="text-2xl font-bold text-white font-mono tracking-tight">
                {kpi.value.toLocaleString()}
              </div>
            </div>
          );
        })}
      </div>

      {/* Status & Latest Batch Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Latest Batch Run */}
        <div className="bg-[#0F172A] border border-slate-800 rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wider">Latest Ingestion Batch</h3>
            <span className="text-[10px] font-mono text-slate-500">
              {stats?.latest_batch?.batch_id ? `ID: ${stats.latest_batch.batch_id.slice(0, 8)}` : 'No batches yet'}
            </span>
          </div>

          {stats?.latest_batch ? (
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-slate-900/60 rounded-lg border border-slate-800">
                <span className="text-xs text-slate-400">Status</span>
                <span className="px-2 py-0.5 text-[10px] font-mono font-semibold rounded bg-emerald-950 text-emerald-400 border border-emerald-800">
                  {stats.latest_batch.status}
                </span>
              </div>
              <div className="grid grid-cols-3 gap-2 text-center">
                <div className="p-2 bg-slate-900/40 rounded border border-slate-800/80">
                  <div className="text-[10px] text-slate-400">Processed</div>
                  <div className="text-sm font-bold text-white font-mono">{stats.latest_batch.processed_rows}</div>
                </div>
                <div className="p-2 bg-slate-900/40 rounded border border-slate-800/80">
                  <div className="text-[10px] text-slate-400">Success</div>
                  <div className="text-sm font-bold text-emerald-400 font-mono">{stats.latest_batch.success_count}</div>
                </div>
                <div className="p-2 bg-slate-900/40 rounded border border-slate-800/80">
                  <div className="text-[10px] text-slate-400">Errors</div>
                  <div className="text-sm font-bold text-rose-400 font-mono">{stats.latest_batch.error_count}</div>
                </div>
              </div>
              <div className="text-[10px] text-slate-500 flex justify-between">
                <span>Source: {stats.latest_batch.source}</span>
                <span>Batch Size: {stats.latest_batch.batch_size}</span>
              </div>
            </div>
          ) : (
            <div className="p-6 text-center text-xs text-slate-500 bg-slate-900/40 rounded-lg border border-slate-800/60">
              No batch runs recorded. Run an ingestion batch to view telemetry.
            </div>
          )}
        </div>

        {/* System & Architecture Health */}
        <div className="bg-[#0F172A] border border-slate-800 rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wider">Multi-Database Separation Health</h3>
            <span className="px-2 py-0.5 text-[10px] font-mono font-semibold rounded bg-blue-950 text-blue-400 border border-blue-800">
              {health?.status || 'CHECKING'}
            </span>
          </div>

          <div className="grid grid-cols-2 gap-2">
            {[
              { name: 'Source DB (Raw Customers)', key: 'source_db' },
              { name: 'Protected DB (Tokens/FPE)', key: 'protected_db' },
              { name: 'Secure Vault DB (AES-GCM)', key: 'vault_db' },
              { name: 'Policy DB (Dynamic Rules)', key: 'policy_db' },
              { name: 'Audit DB (Append-Only Log)', key: 'audit_db' },
              { name: 'Mailpit (Local SMTP 1025)', key: 'mailpit_smtp' },
            ].map((item) => {
              const dep = health?.dependencies?.[item.key];
              const isUp = dep?.status === 'UP';
              return (
                <div key={item.key} className="p-2.5 bg-slate-900/50 border border-slate-800 rounded-lg flex items-center justify-between">
                  <div className="text-[11px] text-slate-300 font-medium truncate pr-2">{item.name}</div>
                  {isUp ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                  ) : (
                    <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0" />
                  )}
                </div>
              );
            })}
          </div>

          <p className="text-[10px] text-slate-500 mt-4 leading-relaxed">
            All database operations are logically or physically isolated. Direct access to the Secure Vault is blocked for all normal downstream applications.
          </p>
        </div>
      </div>
    </div>
  );
};
