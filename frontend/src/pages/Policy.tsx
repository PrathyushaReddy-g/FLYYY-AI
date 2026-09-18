import React, { useState, useEffect } from 'react';
import { Sliders, Save, CheckCircle, AlertCircle, Shield } from 'lucide-react';
import { policyService } from '../services/api';
import { PolicyItem } from '../types';

export const Policy: React.FC = () => {
  const [policies, setPolicies] = useState<PolicyItem[]>([]);
  const [activeVersion, setActiveVersion] = useState(1);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const fetchPolicies = async () => {
    setLoading(true);
    try {
      const data = await policyService.getPolicies();
      setPolicies(data.policies);
      setActiveVersion(data.active_version);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPolicies();
  }, []);

  const handleMethodChange = (fieldName: string, method: any) => {
    setPolicies((prev) =>
      prev.map((p) => (p.field_name === fieldName ? { ...p, protection_method: method } : p))
    );
  };

  const handleToggle = (fieldName: string, prop: 'enabled' | 'deterministic') => {
    setPolicies((prev) =>
      prev.map((p) => (p.field_name === fieldName ? { ...p, [prop]: !p[prop] } : p))
    );
  };

  const handleSave = async () => {
    setSaving(true);
    setMessage(null);
    try {
      const data = await policyService.updatePolicies(policies);
      setPolicies(data.policies);
      setActiveVersion(data.active_version);
      setMessage({
        type: 'success',
        text: `Protection policies successfully persisted! Active Version: v${data.active_version}`,
      });
    } catch (err: any) {
      setMessage({
        type: 'error',
        text: err.response?.data?.detail || 'Failed to update policies. Admin role required.',
      });
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">Protection Policy Management</h1>
          <p className="text-xs text-slate-400 mt-0.5">Define deterministic tokenization, FPE, encryption, or masking per field</p>
        </div>
        <div className="flex items-center space-x-3">
          <span className="px-2.5 py-1 rounded bg-blue-950/80 border border-blue-800 text-[11px] font-mono text-blue-300">
            Active Policy: v{activeVersion}
          </span>
          <button
            onClick={handleSave}
            disabled={saving}
            className="flex items-center px-4 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold shadow transition disabled:opacity-50"
          >
            <Save className="w-3.5 h-3.5 mr-2" />
            <span>{saving ? 'Persisting Rules...' : 'Save & Increment Version'}</span>
          </button>
        </div>
      </div>

      {message && (
        <div
          className={`p-3 rounded-lg border flex items-center text-xs ${
            message.type === 'success'
              ? 'bg-emerald-950/40 border-emerald-800 text-emerald-300'
              : 'bg-red-950/40 border-red-800 text-red-300'
          }`}
        >
          {message.type === 'success' ? (
            <CheckCircle className="w-4 h-4 mr-2 flex-shrink-0" />
          ) : (
            <AlertCircle className="w-4 h-4 mr-2 flex-shrink-0" />
          )}
          <span>{message.text}</span>
        </div>
      )}

      {/* Policies Table */}
      <div className="bg-[#0F172A] border border-slate-800 rounded-xl p-5">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900/80 text-[11px] font-mono text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="p-3">Field Name</th>
                <th className="p-3">Classification</th>
                <th className="p-3">Protection Method</th>
                <th className="p-3 text-center">Enabled</th>
                <th className="p-3 text-center">Deterministic</th>
                <th className="p-3 text-right">Rule Version</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono text-[11px]">
              {policies.map((p) => (
                <tr key={p.field_name} className="hover:bg-slate-900/40">
                  <td className="p-3 text-white font-semibold">{p.field_name}</td>
                  <td className="p-3 text-slate-400">{p.classification}</td>
                  <td className="p-3">
                    <select
                      value={p.protection_method}
                      onChange={(e) => handleMethodChange(p.field_name, e.target.value)}
                      className="bg-slate-900 border border-slate-700 rounded px-2.5 py-1 text-xs text-white focus:outline-none focus:border-blue-500"
                    >
                      <option value="TOKENIZE">TOKENIZE (Deterministic Token)</option>
                      <option value="FPE">FPE (Format-Preserving Encryption)</option>
                      <option value="ENCRYPT">ENCRYPT (AES-256-GCM Vault)</option>
                      <option value="MASK">MASK (Display-Only Masking)</option>
                      <option value="KEEP">KEEP (Plaintext Retention)</option>
                    </select>
                  </td>
                  <td className="p-3 text-center">
                    <input
                      type="checkbox"
                      checked={p.enabled}
                      onChange={() => handleToggle(p.field_name, 'enabled')}
                      className="w-4 h-4 rounded bg-slate-900 border-slate-700 text-blue-600 focus:ring-0 cursor-pointer"
                    />
                  </td>
                  <td className="p-3 text-center">
                    <input
                      type="checkbox"
                      checked={p.deterministic}
                      onChange={() => handleToggle(p.field_name, 'deterministic')}
                      className="w-4 h-4 rounded bg-slate-900 border-slate-700 text-blue-600 focus:ring-0 cursor-pointer"
                    />
                  </td>
                  <td className="p-3 text-right text-slate-400">v{p.version}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-lg text-xs text-slate-400">
        <h4 className="font-semibold text-slate-200 mb-1 flex items-center">
          <Shield className="w-4 h-4 mr-1.5 text-blue-400" />
          Dynamic Policy Engine Rationale
        </h4>
        <p className="leading-relaxed">
          Policies are not hardcoded. When batches run, the batch engine pulls the active policy directly from PostgreSQL. If a policy is updated, subsequent batches will apply the new version while preserving existing vault mappings.
        </p>
      </div>
    </div>
  );
};
