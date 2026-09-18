import React, { useState } from 'react';
import { KeyRound, ShieldAlert, CheckCircle2, AlertTriangle, Lock } from 'lucide-react';
import { revealService } from '../services/api';

export const ControlledReveal: React.FC = () => {
  const [subjectId, setSubjectId] = useState('C001');
  const [field, setField] = useState('EMAIL');
  const [purpose, setPurpose] = useState('CUSTOMER_SUPPORT');
  const [reference, setReference] = useState('TICKET-1091');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleReveal = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await revealService.reveal(subjectId, field, purpose, reference);
      setResult(data);
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 'ACCESS_DENIED: You are not authorized to perform controlled reveal.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-white tracking-tight">Controlled Plaintext Reveal Gateway</h1>
        <p className="text-xs text-slate-400 mt-0.5">
          Audited exception workflow requiring role authorization, explicit purpose validation, and ticket reference
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Reveal Request Form */}
        <div className="bg-[#0F172A] border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center space-x-2">
            <Lock className="w-4 h-4 text-amber-400" />
            <h2 className="text-sm font-semibold text-slate-200">Request Controlled PII Reveal</h2>
          </div>

          <form onSubmit={handleReveal} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">Subject Customer ID</label>
              <input
                type="text"
                value={subjectId}
                onChange={(e) => setSubjectId(e.target.value)}
                required
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white font-mono focus:outline-none focus:border-blue-500"
                placeholder="e.g. C001"
              />
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">Requested Field</label>
                <select
                  value={field}
                  onChange={(e) => setField(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="EMAIL">EMAIL</option>
                  <option value="MOBILE">MOBILE (Phone)</option>
                  <option value="NAME">NAME</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">Justified Purpose</label>
                <select
                  value={purpose}
                  onChange={(e) => setPurpose(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="CUSTOMER_SUPPORT">CUSTOMER_SUPPORT</option>
                  <option value="FRAUD_INVESTIGATION">FRAUD_INVESTIGATION</option>
                  <option value="UNAUTHORIZED_BROWSING">UNAUTHORIZED_BROWSING (Test Deny)</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Ticket / Audit Reference ID
              </label>
              <input
                type="text"
                value={reference}
                onChange={(e) => setReference(e.target.value)}
                required
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white font-mono focus:outline-none focus:border-blue-500"
                placeholder="e.g. TICKET-1091"
              />
              <p className="text-[10px] text-slate-500 mt-1">
                A valid ticket reference is required. Missing or blank references will be rejected.
              </p>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center py-2 px-4 bg-amber-600 hover:bg-amber-500 text-white rounded-lg text-xs font-semibold shadow transition disabled:opacity-50"
            >
              <KeyRound className="w-3.5 h-3.5 mr-2" />
              <span>{loading ? 'Validating Authorization...' : 'Submit Reveal Request'}</span>
            </button>
          </form>

          {/* Denied Result */}
          {error && (
            <div className="p-4 bg-red-950/40 border border-red-800 rounded-lg space-y-2">
              <div className="flex items-center text-red-400 text-xs font-bold">
                <AlertTriangle className="w-4 h-4 mr-2 flex-shrink-0" />
                <span>ACCESS_DENIED</span>
              </div>
              <p className="text-[11px] text-red-300">
                The Privacy Gateway rejected this request. Your role, requested field, or declared purpose is unauthorized.
              </p>
              <p className="text-[10px] font-mono text-red-400 bg-red-950/80 p-2 rounded border border-red-900">
                SECURITY LOG: This unauthorized attempt has been permanently recorded in the immutable audit log.
              </p>
            </div>
          )}

          {/* Authorized Success Result */}
          {result && (
            <div className="p-4 bg-emerald-950/40 border border-emerald-800 rounded-lg space-y-3">
              <div className="flex items-center text-emerald-300 text-xs font-bold">
                <CheckCircle2 className="w-4 h-4 mr-2 flex-shrink-0" />
                <span>Controlled Reveal Successful</span>
              </div>

              <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg font-mono text-xs">
                <div className="text-[10px] text-slate-400">Decrypted Plaintext Value:</div>
                <div className="text-base text-emerald-400 font-bold tracking-wide mt-1 select-all">
                  {result.plaintext_value}
                </div>
              </div>

              <div className="flex items-center text-[11px] text-amber-300 bg-amber-950/40 p-2.5 rounded border border-amber-800/60">
                <ShieldAlert className="w-4 h-4 mr-2 flex-shrink-0 text-amber-400" />
                <span>WARNING: {result.warning}</span>
              </div>
            </div>
          )}
        </div>

        {/* Security Rules & Explanation */}
        <div className="bg-[#0F172A] border border-slate-800 rounded-xl p-5 space-y-4">
          <h2 className="text-sm font-semibold text-slate-200">Access Control Matrix</h2>

          <div className="space-y-3 text-xs text-slate-400">
            <p className="leading-relaxed">
              In accordance with the zero-trust architecture, sensitive customer PII is never accessible by default. Controlled reveal requires 4-tier validation:
            </p>

            <div className="space-y-2 font-mono text-[11px]">
              <div className="p-2.5 bg-slate-900/60 border border-slate-800 rounded flex justify-between">
                <span>1. Role Authorization</span>
                <span className="text-blue-400 font-bold">CUSTOMER_SUPPORT or ADMIN</span>
              </div>
              <div className="p-2.5 bg-slate-900/60 border border-slate-800 rounded flex justify-between">
                <span>2. Purpose Validation</span>
                <span className="text-indigo-400 font-bold">CUSTOMER_SUPPORT / FRAUD</span>
              </div>
              <div className="p-2.5 bg-slate-900/60 border border-slate-800 rounded flex justify-between">
                <span>3. Mandatory Reference</span>
                <span className="text-amber-400 font-bold">Minimum 3 characters (e.g. TICKET)</span>
              </div>
              <div className="p-2.5 bg-slate-900/60 border border-slate-800 rounded flex justify-between">
                <span>4. Immutable Audit</span>
                <span className="text-emerald-400 font-bold">Appended to audit_events</span>
              </div>
            </div>

            <div className="p-3 bg-blue-950/20 border border-blue-800/40 rounded-lg text-[11px] text-slate-400">
              Try switching users to <strong className="text-blue-300">MARKETING</strong> or <strong className="text-blue-300">AUDITOR</strong> and submitting a reveal to witness real-time cryptographic denial and security event recording.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
