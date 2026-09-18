import React, { useState } from 'react';
import { RefreshCw, Send, CheckCircle2, AlertCircle, ShieldCheck } from 'lucide-react';
import { bounceService } from '../services/api';

export const BounceSimulator: React.FC = () => {
  const [email, setEmail] = useState('john.doe@example.com');
  const [event, setEvent] = useState('BOUNCE');
  const [reason, setReason] = useState('MAILBOX_NOT_FOUND');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSimulate = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await bounceService.simulateBounce(email, event, reason);
      setResult(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Bounce callback processing failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-white tracking-tight">Trusted Email Provider Bounce Simulator</h1>
        <p className="text-xs text-slate-400 mt-0.5">
          Simulate inbound webhook notifications from trusted email delivery providers with automatic token remapping
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Simulation Form */}
        <div className="bg-[#0F172A] border border-slate-800 rounded-xl p-5 space-y-4">
          <h2 className="text-sm font-semibold text-slate-200">Incoming Webhook Payload Simulation</h2>

          {error && (
            <div className="p-3 bg-red-950/40 border border-red-800 rounded-lg flex items-center text-xs text-red-300">
              <AlertCircle className="w-4 h-4 mr-2 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSimulate} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Provider Plaintext Recipient (Trusted Callback Input)
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white font-mono focus:outline-none focus:border-blue-500"
                placeholder="e.g. john.doe@example.com"
              />
              <p className="text-[10px] text-slate-500 mt-1">
                Represents external provider data delivered to webhook endpoint.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">Event Type</label>
                <select
                  value={event}
                  onChange={(e) => setEvent(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="BOUNCE">BOUNCE</option>
                  <option value="COMPLAINT">COMPLAINT</option>
                  <option value="UNSUBSCRIBE">UNSUBSCRIBE</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">Reason Code</label>
                <select
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="MAILBOX_NOT_FOUND">MAILBOX_NOT_FOUND</option>
                  <option value="DOMAIN_DOES_NOT_EXIST">DOMAIN_DOES_NOT_EXIST</option>
                  <option value="SPAM_REJECTED">SPAM_REJECTED</option>
                  <option value="MAILBOX_FULL">MAILBOX_FULL</option>
                </select>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center py-2 px-4 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold shadow transition disabled:opacity-50"
            >
              <Send className="w-3.5 h-3.5 mr-2" />
              <span>{loading ? 'Processing Webhook...' : 'Transmit Provider Callback'}</span>
            </button>
          </form>

          {result && (
            <div className="p-4 bg-emerald-950/40 border border-emerald-800 rounded-lg space-y-2">
              <div className="flex items-center text-emerald-300 text-xs font-semibold">
                <CheckCircle2 className="w-4 h-4 mr-2 flex-shrink-0" />
                <span>Reverse Resolution & Ingestion Succeeded</span>
              </div>
              <div className="text-[11px] font-mono text-slate-300 bg-slate-950/80 p-2.5 rounded border border-slate-800 space-y-1">
                <div>Remapped Recipient Token: <span className="text-cyan-400 font-bold">{result.recipient}</span></div>
                <div>Event: <span className="text-amber-400 font-semibold">{result.event}</span></div>
                <div>Reason: <span className="text-slate-400">{result.reason}</span></div>
                <div>Status: <span className="text-emerald-400">{result.status}</span></div>
              </div>
              <p className="text-[10px] text-slate-400">
                Notice: Downstream applications query the bounce log strictly using the protected identifier. The real email is not stored in downstream operational logs.
              </p>
            </div>
          )}
        </div>

        {/* Workflow Explanation */}
        <div className="bg-[#0F172A] border border-slate-800 rounded-xl p-5 space-y-4">
          <h2 className="text-sm font-semibold text-slate-200">Reverse-Resolution Architecture</h2>

          <div className="space-y-3 text-xs text-slate-400 leading-relaxed">
            <p>
              When a third-party email provider (e.g. SendGrid, Mailgun, Amazon SES) issues a bounce or complaint webhook, it identifies the recipient by real plaintext email.
            </p>
            <div className="p-3 bg-slate-900 border border-slate-800 rounded-lg font-mono text-[11px] text-slate-300 space-y-1">
              <div className="text-slate-500">// Reverse Resolution Flow:</div>
              <div>1. Inbound Webhook: provider real email</div>
              <div>2. Privacy Gateway queries Vault with deterministic HMAC</div>
              <div>3. Matching protected token identified: <span className="text-cyan-400">EMAIL_xxxxx</span></div>
              <div>4. Downstream record saved with <span className="text-emerald-400">token only</span></div>
              <div>5. Audit event logged without plaintext</div>
            </div>
            <p className="text-[11px] text-slate-500">
              Downstream suppress lists and marketing dashboards remain 100% free of plaintext customer email addresses.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
