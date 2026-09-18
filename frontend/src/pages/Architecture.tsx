import React from 'react';
import {
  ShieldCheck,
  Database,
  Search,
  Sliders,
  Layers,
  Key,
  Lock,
  Mail,
  FileText,
  ArrowRight,
  ShieldAlert
} from 'lucide-react';

export const Architecture: React.FC = () => {
  const pipelineSteps = [
    { step: '1', title: 'Source DB / Ingestion', icon: Database, desc: 'Original customer records extracted read-only' },
    { step: '2', title: 'Dynamic PII Discovery', icon: Search, desc: 'Presidio & regex analyze schema without leaking data' },
    { step: '3', title: 'Dynamic Policy Engine', icon: Sliders, desc: 'Configurable rules (TOKENIZE, FPE, ENCRYPT, KEEP, MASK)' },
    { step: '4', title: 'Chunked Batch Execution', icon: Layers, desc: 'High-throughput idempotent ETL with upserts' },
    { step: '5', title: 'Cryptographic Protection', icon: Key, desc: 'pyffx FPE (10 digits) & HMAC deterministic tokens' },
    { step: '6', title: 'Protected Database', icon: ShieldCheck, desc: 'Only tokens & FPE values stored for downstream apps' },
    { step: '7', title: 'Privacy Gateway', icon: Lock, desc: 'Single point of mediation: Auth, RBAC, Purpose validation' },
    { step: '8', title: 'AES-GCM Secure Vault', icon: Lock, desc: 'Originals encrypted with 96-bit nonces, keys outside DB' },
    { step: '9', title: 'Downstream Operations', icon: Mail, desc: 'Token-based email delivery (Mailpit) & controlled reveal' },
    { step: '10', title: 'Immutable Audit Trail', icon: FileText, desc: 'Zero-PII append-only log of every access & rejection' },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-xl font-bold text-white tracking-tight">System Architecture & Core Principles</h1>
        <p className="text-xs text-slate-400 mt-0.5">
          End-to-end cryptographic and organizational privacy enforcement pipeline
        </p>
      </div>

      {/* Core Principles Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-[#0F172A] border border-blue-800/40 rounded-xl p-5 space-y-2">
          <div className="w-8 h-8 rounded-lg bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-blue-400 mb-2">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <h3 className="text-sm font-semibold text-white">1. Protected by Default</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Downstream applications, analytics pipelines, and marketing platforms interact solely with protected tokens and format-preserving ciphertexts. No plaintext PII exists in downstream datastores.
          </p>
        </div>

        <div className="bg-[#0F172A] border border-amber-800/40 rounded-xl p-5 space-y-2">
          <div className="w-8 h-8 rounded-lg bg-amber-600/20 border border-amber-500/30 flex items-center justify-center text-amber-400 mb-2">
            <Key className="w-5 h-5" />
          </div>
          <h3 className="text-sm font-semibold text-white">2. Reveal Only by Exception</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Plaintext access is restricted to exceptional, authenticated workflows (e.g. authorized customer support or fraud investigation). Requests require role clearance, declared purpose, and ticket reference.
          </p>
        </div>

        <div className="bg-[#0F172A] border border-purple-800/40 rounded-xl p-5 space-y-2">
          <div className="w-8 h-8 rounded-lg bg-purple-600/20 border border-purple-500/30 flex items-center justify-center text-purple-400 mb-2">
            <FileText className="w-5 h-5" />
          </div>
          <h3 className="text-sm font-semibold text-white">3. Audited & Traceable</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Every access request, whether allowed or denied, is written to an immutable audit store. Audit records contain protected identifiers and reason codes, ensuring zero recursive PII leakage into log files.
          </p>
        </div>
      </div>

      {/* Visual Pipeline */}
      <div className="bg-[#0F172A] border border-slate-800 rounded-xl p-6 space-y-6">
        <h2 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">
          Complete End-to-End Privacy Architecture Flow
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3">
          {pipelineSteps.map((step, idx) => {
            const Icon = step.icon;
            return (
              <div
                key={step.step}
                className="bg-slate-900/80 border border-slate-800 rounded-xl p-3.5 space-y-2 relative group hover:border-blue-500/40 transition"
              >
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono font-bold text-blue-400 bg-blue-950/80 px-2 py-0.5 rounded border border-blue-800">
                    STAGE {step.step}
                  </span>
                  <Icon className="w-4 h-4 text-slate-400 group-hover:text-blue-400 transition" />
                </div>
                <div className="font-semibold text-xs text-white">{step.title}</div>
                <div className="text-[10px] text-slate-400 leading-snug">{step.desc}</div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Cryptographic Standards */}
      <div className="bg-[#0F172A] border border-slate-800 rounded-xl p-6 space-y-4">
        <h2 className="text-sm font-semibold text-slate-200">Cryptographic Implementations</h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-lg space-y-2">
            <span className="font-mono text-[11px] text-emerald-400 font-bold">Format-Preserving Encryption (FPE)</span>
            <p className="text-slate-400 text-[11px] leading-relaxed">
              Implemented using NIST-recognized Feistel FFX algorithm (<code className="text-slate-300 font-mono">pyffx</code>). Encrypts 10-digit phone numbers into exactly 10-digit valid numbers without changing data types or requiring schema changes.
            </p>
          </div>

          <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-lg space-y-2">
            <span className="font-mono text-[11px] text-blue-400 font-bold">Secure Vault Encryption</span>
            <p className="text-slate-400 text-[11px] leading-relaxed">
              Original sensitive customer values are encrypted using AES-256-GCM authenticated cipher with unique 96-bit cryptographically random nonces. Vault keys are isolated outside database storage.
            </p>
          </div>

          <div className="p-4 bg-slate-900/60 border border-slate-800 rounded-lg space-y-2">
            <span className="font-mono text-[11px] text-purple-400 font-bold">Deterministic Tokenization</span>
            <p className="text-slate-400 text-[11px] leading-relaxed">
              Constructed via keyed HMAC-SHA256 digests formatted with domain prefixes (<code className="text-slate-300 font-mono">NAME_</code>, <code className="text-slate-300 font-mono">EMAIL_</code>). Guarantees referential integrity across batch runs while remaining irreversible.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
