import React, { useState, useEffect } from 'react';
import { Layers, RefreshCw, CheckCircle2, AlertTriangle, XCircle, Clock } from 'lucide-react';
import { batchService } from '../services/api';
import { BatchRun } from '../types';

export const BatchMonitor: React.FC = () => {
  const [batches, setBatches] = useState<BatchRun[]>([]);
  const [loading, setLoading] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const fetchBatches = async () => {
    setLoading(true);
    try {
      const data = await batchService.getBatches();
      setBatches(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBatches();
    let interval: any;
    if (autoRefresh) {
      interval = setInterval(fetchBatches, 5000);
    }
    return () => clearInterval(interval);
  }, [autoRefresh]);

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-emerald-950 text-emerald-400 border border-emerald-800">
            <CheckCircle2 className="w-3 h-3 mr-1" /> COMPLETED
          </span>
        );
      case 'RUNNING':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-blue-950 text-blue-400 border border-blue-800">
            <RefreshCw className="w-3 h-3 mr-1 animate-spin" /> RUNNING
          </span>
        );
      case 'PARTIAL_SUCCESS':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-amber-950 text-amber-400 border border-amber-800">
            <AlertTriangle className="w-3 h-3 mr-1" /> PARTIAL
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-mono font-semibold bg-red-950 text-red-400 border border-red-800">
            <XCircle className="w-3 h-3 mr-1" /> FAILED
          </span>
        );
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">Batch Processing Monitor</h1>
          <p className="text-xs text-slate-400 mt-0.5">Real-time status, throughput, and error auditing for chunked ETL runs</p>
        </div>
        <div className="flex items-center space-x-3">
          <label className="flex items-center space-x-2 text-xs text-slate-400 cursor-pointer">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="w-3.5 h-3.5 rounded bg-slate-900 border-slate-700 text-blue-600 focus:ring-0"
            />
            <span>Auto-refresh (5s)</span>
          </label>
          <button
            onClick={fetchBatches}
            disabled={loading}
            className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg border border-slate-700 transition"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin text-blue-400' : ''}`} />
          </button>
        </div>
      </div>

      {/* Batches Table */}
      <div className="bg-[#0F172A] border border-slate-800 rounded-xl p-5">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900/80 text-[11px] font-mono text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="p-3">Batch ID</th>
                <th className="p-3">Source</th>
                <th className="p-3">Status</th>
                <th className="p-3">Start Time</th>
                <th className="p-3">Chunk Size</th>
                <th className="p-3 text-right">Processed</th>
                <th className="p-3 text-right">Success</th>
                <th className="p-3 text-right">Errors</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono text-[11px]">
              {batches.map((b) => (
                <tr key={b.batch_id} className="hover:bg-slate-900/40">
                  <td className="p-3 text-blue-400 font-semibold">{b.batch_id.slice(0, 13)}...</td>
                  <td className="p-3 text-slate-300">{b.source}</td>
                  <td className="p-3">{getStatusBadge(b.status)}</td>
                  <td className="p-3 text-slate-400">
                    {b.start_time ? new Date(b.start_time).toLocaleTimeString() : '-'}
                  </td>
                  <td className="p-3 text-slate-400">{b.batch_size}</td>
                  <td className="p-3 text-right text-white font-semibold">{b.processed_rows}</td>
                  <td className="p-3 text-right text-emerald-400 font-semibold">{b.success_count}</td>
                  <td className="p-3 text-right text-rose-400 font-semibold">{b.error_count}</td>
                </tr>
              ))}
              {batches.length === 0 && (
                <tr>
                  <td colSpan={8} className="p-6 text-center text-slate-500">
                    No batch executions found. Execute an ingestion batch from the Source Configuration page.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
