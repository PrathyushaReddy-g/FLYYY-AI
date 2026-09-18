import React, { useState, useEffect } from 'react';
import { Search, RefreshCw, AlertCircle, CheckCircle2 } from 'lucide-react';
import { discoveryService } from '../services/api';
import { DiscoveryField } from '../types';

export const Discovery: React.FC = () => {
  const [fields, setFields] = useState<DiscoveryField[]>([]);
  const [loading, setLoading] = useState(false);
  const [discoveredAt, setDiscoveredAt] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const runDiscovery = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await discoveryService.discover();
      setFields(data.fields);
      setDiscoveredAt(data.discovered_at);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to execute dynamic PII discovery.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runDiscovery();
  }, []);

  const classificationBadges: Record<string, string> = {
    PERSON: 'bg-indigo-950 text-indigo-400 border-indigo-800',
    EMAIL: 'bg-blue-950 text-blue-400 border-blue-800',
    PHONE: 'bg-emerald-950 text-emerald-400 border-emerald-800',
    IDENTIFIER: 'bg-purple-950 text-purple-400 border-purple-800',
    LOCATION: 'bg-amber-950 text-amber-400 border-amber-800',
    GENERIC: 'bg-slate-900 text-slate-400 border-slate-700',
  };

  const protectionBadges: Record<string, string> = {
    TOKENIZE: 'bg-blue-600/20 text-blue-400 border-blue-500/40',
    FPE: 'bg-emerald-600/20 text-emerald-400 border-emerald-500/40',
    KEEP: 'bg-slate-800 text-slate-400 border-slate-700',
    ENCRYPT: 'bg-purple-600/20 text-purple-400 border-purple-500/40',
    MASK: 'bg-amber-600/20 text-amber-400 border-amber-500/40',
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">Dynamic PII Discovery & Classification</h1>
          <p className="text-xs text-slate-400 mt-0.5">Automated detection using Microsoft Presidio and semantic analysis</p>
        </div>
        <button
          onClick={runDiscovery}
          disabled={loading}
          className="flex items-center px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold shadow transition disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 mr-2 ${loading ? 'animate-spin' : ''}`} />
          <span>{loading ? 'Analyzing Schema...' : 'Run Dynamic Discovery'}</span>
        </button>
      </div>

      {error && (
        <div className="p-3 bg-red-950/40 border border-red-800 rounded-lg flex items-center text-xs text-red-300">
          <AlertCircle className="w-4 h-4 mr-2 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Discovered Fields Table */}
      <div className="bg-[#0F172A] border border-slate-800 rounded-xl p-5">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Search className="w-4 h-4 text-blue-400" />
            <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wider">Discovered Field Inventory</h3>
          </div>
          {discoveredAt && (
            <span className="text-[10px] font-mono text-slate-500">
              Scanned: {new Date(discoveredAt).toLocaleTimeString()}
            </span>
          )}
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900/80 text-[11px] font-mono text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="p-3">Field Name</th>
                <th className="p-3">Data Type</th>
                <th className="p-3">Classification</th>
                <th className="p-3">Confidence Score</th>
                <th className="p-3">Recommended Policy</th>
                <th className="p-3">Masked Presentation Sample</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono text-[11px]">
              {fields.map((f) => (
                <tr key={f.field_name} className="hover:bg-slate-900/40">
                  <td className="p-3 text-white font-semibold">{f.field_name}</td>
                  <td className="p-3 text-slate-400">{f.data_type}</td>
                  <td className="p-3">
                    <span
                      className={`px-2 py-0.5 rounded border text-[10px] font-semibold ${
                        classificationBadges[f.classification] || classificationBadges.GENERIC
                      }`}
                    >
                      {f.classification}
                    </span>
                  </td>
                  <td className="p-3">
                    <div className="flex items-center space-x-2">
                      <div className="w-16 bg-slate-800 rounded-full h-1.5 overflow-hidden">
                        <div
                          className="bg-blue-500 h-full rounded-full"
                          style={{ width: `${Math.round(f.confidence * 100)}%` }}
                        ></div>
                      </div>
                      <span className="text-slate-300 font-semibold">{f.confidence.toFixed(2)}</span>
                    </div>
                  </td>
                  <td className="p-3">
                    <span
                      className={`px-2 py-0.5 rounded border text-[10px] font-semibold ${
                        protectionBadges[f.recommended_protection] || protectionBadges.KEEP
                      }`}
                    >
                      {f.recommended_protection}
                    </span>
                  </td>
                  <td className="p-3 text-slate-400">
                    {f.sample_masked ? (
                      <span className="bg-slate-900 px-2 py-1 rounded border border-slate-800 text-slate-300">
                        {f.sample_masked}
                      </span>
                    ) : (
                      <span className="text-slate-600">-</span>
                    )}
                  </td>
                </tr>
              ))}
              {fields.length === 0 && !loading && (
                <tr>
                  <td colSpan={6} className="p-6 text-center text-slate-500">
                    Click 'Run Dynamic Discovery' to inspect the source database.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div className="p-4 bg-blue-950/20 border border-blue-800/40 rounded-lg text-xs text-slate-400 flex items-start space-x-3">
        <CheckCircle2 className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
        <p>
          <strong className="text-slate-200">Zero Raw PII Exposure:</strong> The discovery engine analyzes fields dynamically using regular expressions and Presidio Named Entity Recognition. Raw plaintext samples are strictly masked before returning to the UI.
        </p>
      </div>
    </div>
  );
};
