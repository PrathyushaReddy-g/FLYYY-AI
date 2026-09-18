import React, { useState, useEffect } from 'react';
import { FileText, Filter, CheckCircle2, XCircle, AlertTriangle, ChevronLeft, ChevronRight, RefreshCw } from 'lucide-react';
import { auditService } from '../services/api';
import { AuditEvent } from '../types';

export const AuditDashboard: React.FC = () => {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [actor, setActor] = useState('');
  const [action, setAction] = useState('');
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchEvents = async () => {
    setLoading(true);
    try {
      const data = await auditService.getEvents(page, 20, actor, action, '', result);
      setEvents(data.items);
      setTotal(data.total);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, [page, actor, action, result]);

  const getResultBadge = (res: string) => {
    switch (res) {
      case 'ALLOWED':
      case 'SUCCESS':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-emerald-950 text-emerald-400 border border-emerald-800">
            <CheckCircle2 className="w-3 h-3 mr-1" /> {res}
          </span>
        );
      case 'DENIED':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-red-950 text-red-400 border border-red-800">
            <XCircle className="w-3 h-3 mr-1" /> DENIED
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-amber-950 text-amber-400 border border-amber-800">
            <AlertTriangle className="w-3 h-3 mr-1" /> {res}
          </span>
        );
    }
  };

  const totalPages = Math.ceil(total / 20) || 1;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">Security & Governance Audit Log</h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Append-only, immutable record of all data operations, access requests, and cryptographic executions
          </p>
        </div>
        <button
          onClick={fetchEvents}
          disabled={loading}
          className="flex items-center px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-medium border border-slate-700 transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 mr-2 ${loading ? 'animate-spin text-blue-400' : ''}`} />
          <span>Refresh Audit Feed</span>
        </button>
      </div>

      {/* Filter Toolbar */}
      <div className="bg-[#0F172A] border border-slate-800 rounded-xl p-4 grid grid-cols-1 md:grid-cols-4 gap-3">
        <div>
          <label className="block text-[11px] font-medium text-slate-400 mb-1">Filter Actor</label>
          <input
            type="text"
            value={actor}
            onChange={(e) => {
              setActor(e.target.value);
              setPage(1);
            }}
            placeholder="e.g. admin, support"
            className="w-full bg-slate-900 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-blue-500"
          />
        </div>

        <div>
          <label className="block text-[11px] font-medium text-slate-400 mb-1">Filter Action</label>
          <select
            value={action}
            onChange={(e) => {
              setAction(e.target.value);
              setPage(1);
            }}
            className="w-full bg-slate-900 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-blue-500"
          >
            <option value="">All Actions</option>
            <option value="REVEAL">REVEAL</option>
            <option value="SEND_EMAIL">SEND_EMAIL</option>
            <option value="BOUNCE_PROCESSED">BOUNCE_PROCESSED</option>
            <option value="BATCH_RUN">BATCH_RUN</option>
            <option value="LOGIN">LOGIN</option>
            <option value="DISCOVERY">DISCOVERY</option>
            <option value="POLICY_UPDATE">POLICY_UPDATE</option>
            <option value="EXPORT_PROTECTED_DATA">EXPORT_PROTECTED_DATA</option>
          </select>
        </div>

        <div>
          <label className="block text-[11px] font-medium text-slate-400 mb-1">Filter Result</label>
          <select
            value={result}
            onChange={(e) => {
              setResult(e.target.value);
              setPage(1);
            }}
            className="w-full bg-slate-900 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-blue-500"
          >
            <option value="">All Results</option>
            <option value="ALLOWED">ALLOWED</option>
            <option value="DENIED">DENIED</option>
            <option value="SUCCESS">SUCCESS</option>
            <option value="FAILURE">FAILURE</option>
          </select>
        </div>

        <div className="flex items-end justify-end">
          <span className="text-[11px] font-mono text-slate-400">Matching Events: {total}</span>
        </div>
      </div>

      {/* Events Table */}
      <div className="bg-[#0F172A] border border-slate-800 rounded-xl p-5">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900/80 text-[11px] font-mono text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="p-3">Timestamp</th>
                <th className="p-3">Actor</th>
                <th className="p-3">Action</th>
                <th className="p-3">Subject</th>
                <th className="p-3">Field</th>
                <th className="p-3">Purpose / Reference</th>
                <th className="p-3">Result</th>
                <th className="p-3">Error Code</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono text-[11px]">
              {events.map((e) => (
                <tr key={e.id} className="hover:bg-slate-900/40">
                  <td className="p-3 text-slate-400 whitespace-nowrap">
                    {e.timestamp ? new Date(e.timestamp).toLocaleString() : '-'}
                  </td>
                  <td className="p-3 text-blue-400 font-semibold">{e.actor}</td>
                  <td className="p-3 text-slate-200">{e.action}</td>
                  <td className="p-3 text-cyan-300">{e.protected_subject}</td>
                  <td className="p-3 text-slate-400">{e.field || '-'}</td>
                  <td className="p-3 text-slate-300">
                    <div>{e.purpose || '-'}</div>
                    <div className="text-[10px] text-slate-500">{e.reference || ''}</div>
                  </td>
                  <td className="p-3">{getResultBadge(e.result)}</td>
                  <td className="p-3 text-rose-400 font-mono text-[10px]">{e.error_code || '-'}</td>
                </tr>
              ))}
              {events.length === 0 && (
                <tr>
                  <td colSpan={8} className="p-6 text-center text-slate-500">
                    No audit records matching criteria.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-between pt-4 border-t border-slate-800 mt-4 text-xs text-slate-400">
          <span>
            Page {page} of {totalPages}
          </span>
          <div className="flex space-x-1">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="p-1 rounded bg-slate-900 border border-slate-800 hover:bg-slate-800 disabled:opacity-40"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="p-1 rounded bg-slate-900 border border-slate-800 hover:bg-slate-800 disabled:opacity-40"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
