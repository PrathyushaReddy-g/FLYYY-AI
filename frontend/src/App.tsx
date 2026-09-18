import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Sidebar } from './components/Sidebar';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { SourceConfig } from './pages/SourceConfig';
import { Discovery } from './pages/Discovery';
import { Policy } from './pages/Policy';
import { BatchMonitor } from './pages/BatchMonitor';
import { ProtectedCustomers } from './pages/ProtectedCustomers';
import { MarketingDemo } from './pages/MarketingDemo';
import { BounceSimulator } from './pages/BounceSimulator';
import { ControlledReveal } from './pages/ControlledReveal';
import { AuditDashboard } from './pages/AuditDashboard';
import { Architecture } from './pages/Architecture';
import { User } from './types';

export const App: React.FC = () => {
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem('user');
    return saved ? JSON.parse(saved) : null;
  });

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  };

  return (
    <BrowserRouter>
      <div className="flex min-h-screen bg-[#070C18] text-slate-100 font-sans">
        {user ? (
          <>
            <Sidebar user={user} onLogout={handleLogout} />
            <main className="flex-1 p-8 overflow-y-auto max-w-7xl">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/sources" element={<SourceConfig />} />
                <Route path="/discovery" element={<Discovery />} />
                <Route path="/policies" element={<Policy />} />
                <Route path="/batches" element={<BatchMonitor />} />
                <Route path="/customers" element={<ProtectedCustomers />} />
                <Route path="/marketing" element={<MarketingDemo />} />
                <Route path="/bounce" element={<BounceSimulator />} />
                <Route path="/reveal" element={<ControlledReveal />} />
                <Route path="/audit" element={<AuditDashboard />} />
                <Route path="/architecture" element={<Architecture />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </main>
          </>
        ) : (
          <Routes>
            <Route path="/login" element={<Login onLoginSuccess={(u) => setUser(u)} />} />
            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        )}
      </div>
    </BrowserRouter>
  );
};
