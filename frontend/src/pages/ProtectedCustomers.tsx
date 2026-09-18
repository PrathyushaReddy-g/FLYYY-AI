import React, { useState, useEffect } from 'react';
import { Users, Download, Search, ShieldCheck, ChevronLeft, ChevronRight, AlertCircle } from 'lucide-react';
import { customerService } from '../services/api';
import { ProtectedCustomer } from '../types';

export const ProtectedCustomers: React.FC = () => {
  const [customers, setCustomers] = useState<ProtectedCustomer[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [exportStatus, setExportStatus] = useState<string | null>(null);

  const fetchCustomers = async () => {
    setLoading(true);
    try {
      const data = await customerService.getCustomers(page, 15, search);
      setCustomers(data.items);
      setTotal(data.total);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCustomers();
  }, [page, search]);

  const handleExport = async () => {
    setExporting(true);
    setExportStatus('Scanning export stream for plaintext leakage...');
    try {
      await customerService.exportCSV();
      setExportStatus('Export security scan PASSED. Protected CSV downloaded.');
    } catch (err: any) {
      setExportStatus('EXPORT REJECTED: Security check detected potential plaintext leakage.');
    } finally {
      setExporting(false);
      setTimeout(() => setExportStatus(null), 5000);
    }
  };

  const totalPages = Math.ceil(total / 15) || 1;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">Protected Customer Database</h1>
          <p className="text-xs text-slate-400 mt-0.5">Isolated downstream datastore containing only tokens and FPE values</p>
        </div>
        <button
          onClick={handleExport}
          disabled={exporting}
          className="flex items-center px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold shadow transition disabled:opacity-50"
        >
          <Download className="w-3.5 h-3.5 mr-2" />
          <span>{exporting ? 'Verifying Clean Export...' : 'Export Protected CSV'}</span>
        </button>
      </div>

      {exportStatus && (
        <div className="p-3 bg-blue-950/40 border border-blue-800 rounded-lg text-xs text-blue-300 flex items-center">
          <ShieldCheck className="w-4 h-4 mr-2 flex-shrink-0" />
          <span>{exportStatus}</span>
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="flex items-center justify-between bg-[#0F172A] border border-slate-800 rounded-xl p-3">
        <div className="relative w-72">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
          <input
            type="text"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            placeholder="Search by ID, Token, City..."
            className="w-full bg-slate-900 border border-slate-700 rounded-lg pl-9 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
        </div>
        <span className="text-[11px] font-mono text-slate-400">Total Records: {total}</span>
      </div>

      {/* Protected Records Table */}
      <div className="bg-[#0F172A] border border-slate-800 rounded-xl p-5">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900/80 text-[11px] font-mono text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="p-3">Customer ID</th>
                <th className="p-3">Name (Deterministic Token)</th>
                <th className="p-3">Email (Deterministic Token)</th>
                <th className="p-3">Mobile (Format-Preserving FPE)</th>
                <th className="p-3">City</th>
                <th className="p-3">Segment</th>
                <th className="p-3 text-right">Policy Ver</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono text-[11px]">
              {customers.map((c) => (
                <tr key={c.customer_id} className="hover:bg-slate-900/40">
                  <td className="p-3 text-blue-400 font-semibold">{c.customer_id}</td>
                  <td className="p-3 text-indigo-300">{c.name || '-'}</td>
                  <td className="p-3 text-cyan-300">{c.email || '-'}</td>
                  <td className="p-3 text-emerald-400 font-bold">{c.mobile || '-'}</td>
                  <td className="p-3 text-slate-400">{c.city || '-'}</td>
                  <td className="p-3 text-slate-400">{c.segment || '-'}</td>
                  <td className="p-3 text-right text-slate-500">v{c.protection_version}</td>
                </tr>
              ))}
              {customers.length === 0 && (
                <tr>
                  <td colSpan={7} className="p-6 text-center text-slate-500">
                    No protected records found. Run an ingestion batch to generate protected customer records.
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
