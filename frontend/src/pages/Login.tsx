import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Lock, User as UserIcon, AlertCircle } from 'lucide-react';
import { authService } from '../services/api';
import { User } from '../types';

interface LoginProps {
  onLoginSuccess: (user: User) => void;
}

export const Login: React.FC<LoginProps> = ({ onLoginSuccess }) => {
  const navigate = useNavigate();

  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const demoAccounts = [
    { role: 'ADMIN', username: 'admin', label: 'Admin (Full Access)' },
    { role: 'MARKETING', username: 'marketing', label: 'Marketing (Token-Only)' },
    { role: 'CUSTOMER_SUPPORT', username: 'support', label: 'Customer Support (Controlled Reveal)' },
    { role: 'AUDITOR', username: 'auditor', label: 'Auditor (Audit Logs Only)' },
  ];

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const data = await authService.login(username, password);

      localStorage.setItem('token', data.access_token);

      const user: User = {
        id: data.username,
        username: data.username,
        email: `${data.username}@flyyy.ai`,
        role: data.role as any,
      };

      localStorage.setItem('user', JSON.stringify(user));

      onLoginSuccess(user);
      navigate('/');
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
        'Authentication failed. Please verify credentials.'
      );
    } finally {
      setLoading(false);
    }
  };

  const selectDemoRole = (uname: string) => {
    setUsername(uname);
    setPassword('admin');
  };

  return (
    <div className="min-h-screen bg-[#070C18] flex items-center justify-center p-4">
      <div className="max-w-md w-full">

        {/* Logo and Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-blue-600/10 border border-blue-500/30 text-blue-400 mb-4 shadow-lg shadow-blue-900/20">
            <Shield className="w-8 h-8" />
          </div>

          <h1 className="text-2xl font-bold text-white tracking-tight">
            FLYYY.AI Platform
          </h1>

          <p className="text-xs text-slate-400 mt-1">
            Privacy-Preserving Customer Data Platform
          </p>

          <div className="inline-block mt-2 px-2.5 py-0.5 rounded-full text-[10px] font-mono tracking-wide bg-blue-950/60 border border-blue-800/50 text-blue-300">
            PROTECTED BY DEFAULT &bull; REVEAL BY EXCEPTION
          </div>
        </div>

        {/* Login Card */}
        <div className="bg-[#0F172A] border border-slate-800 rounded-xl p-6 shadow-xl">
          <h2 className="text-sm font-semibold text-slate-200 mb-4">
            Authenticate to Gateway
          </h2>

          {error && (
            <div className="mb-4 p-3 bg-red-950/50 border border-red-800/60 rounded-lg flex items-center text-xs text-red-300">
              <AlertCircle className="w-4 h-4 mr-2 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-4">

            {/* Username */}
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Username
              </label>

              <div className="relative">
                <UserIcon className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />

                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg pl-9 pr-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                  placeholder="Enter username"
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1.5">
                Password
              </label>

              <div className="relative">
                <Lock className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />

                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg pl-9 pr-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                  placeholder="Enter password"
                />
              </div>
            </div>

            {/* Login Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-2 px-4 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold shadow-md shadow-blue-900/30 transition disabled:opacity-50"
            >
              {loading ? 'Authenticating...' : 'Sign In'}
            </button>

          </form>

          {/* Quick Demo Role Switcher */}
          <div className="mt-6 pt-5 border-t border-slate-800">
            <p className="text-[11px] font-medium text-slate-400 mb-2">
              Select Demonstration Account:
            </p>

            <div className="grid grid-cols-2 gap-2">
              {demoAccounts.map((acc) => (
                <button
                  key={acc.role}
                  type="button"
                  onClick={() => selectDemoRole(acc.username)}
                  className={`text-left p-2 rounded border text-[11px] transition ${
                    username === acc.username
                      ? 'bg-blue-950/60 border-blue-600/80 text-blue-300 font-semibold'
                      : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:border-slate-700'
                  }`}
                >
                  <div className="font-mono text-[10px] text-slate-200">
                    {acc.role}
                  </div>

                  <div className="text-[9px] text-slate-500 truncate">
                    {acc.username}
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        <p className="text-center text-[10px] text-slate-500 mt-4">
          All operations authenticated with RS256/HS256 JWT tokens.
        </p>

      </div>
    </div>
  );
};