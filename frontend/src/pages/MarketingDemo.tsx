import React, { useState, useEffect } from 'react';
import { Mail, Send, ExternalLink, CheckCircle2, AlertCircle, ShieldAlert } from 'lucide-react';
import { customerService, marketingService } from '../services/api';
import { ProtectedCustomer } from '../types';

export const MarketingDemo: React.FC = () => {
  const [customers, setCustomers] = useState<ProtectedCustomer[]>([]);
  const [selectedRecipient, setSelectedRecipient] = useState('');
  const [campaignId, setCampaignId] = useState('CMP-2026-SUMMER');
  const [templateId, setTemplateId] = useState('WELCOME_OFFER');
  const [sending, setSending] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    customerService.getCustomers(1, 20).then((data) => {
      setCustomers(data.items);
      if (data.items.length > 0 && data.items[0].email) {
        setSelectedRecipient(data.items[0].email);
      }
    });
  }, []);

  const handleSendEmail = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedRecipient) return;

    setSending(true);
    setError(null);
    setResult(null);

    try {
      const data = await marketingService.sendEmail(selectedRecipient, campaignId, templateId);
      setResult(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Email dispatch failed. Verify Mailpit connection.');
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-white tracking-tight">Marketing Campaign Execution Demo</h1>
        <p className="text-xs text-slate-400 mt-0.5">
          Execute downstream marketing actions using exclusively protected recipient tokens
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Campaign Execution Form */}
        <div className="bg-[#0F172A] border border-slate-800 rounded-xl p-5 space-y-4">
          <h2 className="text-sm font-semibold text-slate-200">Dispatch Campaign Message</h2>

          {error && (
            <div className="p-3 bg-red-950/40 border border-red-800 rounded-lg flex items-center text-xs text-red-300">
              <AlertCircle className="w-4 h-4 mr-2 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSendEmail} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Protected Recipient Identifier (Token Only)
              </label>
              <select
                value={selectedRecipient}
                onChange={(e) => setSelectedRecipient(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-cyan-300 font-mono focus:outline-none focus:border-blue-500"
              >
                {customers.map((c) => (
                  <option key={c.customer_id} value={c.email || ''}>
                    {c.customer_id} &bull; {c.email} ({c.city})
                  </option>
                ))}
              </select>
              <p className="text-[10px] text-slate-500 mt-1">
                Notice: The marketing user and application interface NEVER observe the real email address.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">Campaign ID</label>
                <input
                  type="text"
                  value={campaignId}
                  onChange={(e) => setCampaignId(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white font-mono focus:outline-none focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1.5">Template ID</label>
                <select
                  value={templateId}
                  onChange={(e) => setTemplateId(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500"
                >
                  <option value="WELCOME_OFFER">WELCOME_OFFER</option>
                  <option value="LOYALTY_REWARD">LOYALTY_REWARD</option>
                  <option value="RETENTION_PROMO">RETENTION_PROMO</option>
                </select>
              </div>
            </div>

            <button
              type="submit"
              disabled={sending || !selectedRecipient}
              className="w-full flex items-center justify-center py-2 px-4 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold shadow transition disabled:opacity-50"
            >
              <Send className="w-3.5 h-3.5 mr-2" />
              <span>{sending ? 'Gateway Processing...' : 'Dispatch Email via Privacy Gateway'}</span>
            </button>
          </form>

          {result && (
            <div className="p-4 bg-emerald-950/40 border border-emerald-800 rounded-lg space-y-2">
              <div className="flex items-center text-emerald-300 text-xs font-semibold">
                <CheckCircle2 className="w-4 h-4 mr-2 flex-shrink-0" />
                <span>Marketing Action Successfully Executed</span>
              </div>
              <div className="text-[11px] font-mono text-slate-300 bg-slate-950/80 p-2.5 rounded border border-slate-800 space-y-1">
                <div>Recipient Token: <span className="text-cyan-400">{result.recipient}</span></div>
                <div>Status: <span className="text-emerald-400 font-bold">{result.status}</span></div>
                <div>Result: <span className="text-slate-400">{result.message}</span></div>
              </div>
              <p className="text-[10px] text-slate-400">
                Zero plaintext leakage: The Privacy Gateway internally decrypted the real email from the secure vault, connected to Mailpit SMTP, and delivered the message without exposing the recipient address to the client.
              </p>
            </div>
          )}
        </div>

        {/* Mailpit Verification Panel */}
        <div className="bg-[#0F172A] border border-slate-800 rounded-xl p-5 space-y-4">
          <h2 className="text-sm font-semibold text-slate-200">Mailpit Local SMTP Inspection</h2>

          <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-lg space-y-3">
            <p className="text-xs text-slate-300 leading-relaxed">
              In development and evaluation mode, emails delivered through the Privacy Gateway are routed directly to Mailpit.
            </p>

            <div className="text-xs font-mono bg-slate-950 p-3 rounded border border-slate-800 space-y-1 text-slate-400">
              <div>SMTP Host: <span className="text-blue-400">localhost (or mailpit in Docker)</span></div>
              <div>SMTP Port: <span className="text-blue-400">1025</span></div>
              <div>Web UI: <span className="text-emerald-400">http://localhost:8025</span></div>
            </div>

            <a
              href="http://localhost:8025"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded border border-slate-700 text-xs font-medium transition"
            >
              <ExternalLink className="w-3.5 h-3.5 mr-2 text-blue-400" />
              <span>Open Mailpit Inbox (Web UI)</span>
            </a>
          </div>

          <div className="p-4 bg-blue-950/20 border border-blue-800/40 rounded-lg text-xs text-slate-400 flex items-start space-x-3">
            <ShieldAlert className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
            <p>
              <strong className="text-slate-200">Security Boundary:</strong> Downstream marketing systems operate strictly on tokens. If the marketing database were compromised, an attacker would obtain only meaningless hashes, rendering customer PII safe.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
