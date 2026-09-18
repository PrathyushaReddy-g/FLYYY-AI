import React, { useState, useEffect } from 'react';
import { Database, Upload, Play, CheckCircle, AlertCircle, FileText } from 'lucide-react';
import { sourceService, batchService } from '../services/api';

export const SourceConfig: React.FC = () => {
  const [sourceType, setSourceType] = useState('DATABASE');
  const [batchSize, setBatchSize] = useState(1000);
  const [config, setConfig] = useState<any>(null);
  const [records, setRecords] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const loadSourceData = async () => {
    try {
      const cfg = await sourceService.getConfig();
      setConfig(cfg);
      const recs = await sourceService.getRecords(1, 10);
      setRecords(recs.items || []);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadSourceData();
  }, []);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setMessage(null);
    try {
      const res = await sourceService.uploadCSV(file);
      setMessage({
        type: 'success',
        text: `Uploaded ${file.name} successfully! Imported ${res.records_imported} source records.`,
      });
      loadSourceData();
    } catch (err: any) {
      setMessage({
        type: 'error',
        text: err.response?.data?.detail || 'CSV upload failed. Verify file format.',
      });
    } finally {
      setUploading(false);
    }
  };

  const handleRunBatch = async () => {
    setLoading(true);
    setMessage(null);
    try {
      const res = await batchService.runBatch(sourceType, batchSize);
      setMessage({
        type: 'success',
        text: `Batch ${res.batch_id.slice(0, 8)} completed successfully! Processed: ${res.processed_rows}, Success: ${res.success_count}, Errors: ${res.error_count}`,
      });
    } catch (err: any) {
      setMessage({
        type: 'error',
        text: err.response?.data?.detail || 'Batch execution failed.',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-white tracking-tight">Source & Ingestion Configuration</h1>
        <p className="text-xs text-slate-400 mt-0.5">Configure source dataset, batch sizes, and trigger privacy pipeline ingestion</p>
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

      {/* Ingestion Settings Card */}
      <div className="bg-[#0F172A] border border-slate-800 rounded-xl p-5 space-y-4">
        <h2 className="text-sm font-semibold text-slate-200">Pipeline Ingestion Parameters</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Source Type Selection */}
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">Source Type</label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => setSourceType('DATABASE')}
                className={`flex items-center justify-center p-2.5 rounded-lg border text-xs font-medium transition ${
                  sourceType === 'DATABASE'
                    ? 'bg-blue-600/20 border-blue-500 text-blue-400 font-semibold'
                    : 'bg-slate-900 border-slate-700 text-slate-400 hover:border-slate-600'
                }`}
              >
                <Database className="w-4 h-4 mr-2" />
                <span>PostgreSQL DB</span>
              </button>
              <button
                type="button"
                onClick={() => setSourceType('CSV')}
                className={`flex items-center justify-center p-2.5 rounded-lg border text-xs font-medium transition ${
                  sourceType === 'CSV'
                    ? 'bg-blue-600/20 border-blue-500 text-blue-400 font-semibold'
                    : 'bg-slate-900 border-slate-700 text-slate-400 hover:border-slate-600'
                }`}
              >
                <FileText className="w-4 h-4 mr-2" />
                <span>CSV Upload</span>
              </button>
            </div>
          </div>

          {/* Configurable Batch Size */}
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1.5">Configurable Batch Size</label>
            <select
              value={batchSize}
              onChange={(e) => setBatchSize(Number(e.target.value))}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-blue-500"
            >
              <option value={100}>100 records / chunk</option>
              <option value={500}>500 records / chunk</option>
              <option value={1000}>1,000 records / chunk</option>
              <option value={5000}>5,000 records / chunk</option>
              <option value={10000}>10,000 records / chunk</option>
            </select>
          </div>
        </div>

        {/* CSV File Upload Section */}
        {sourceType === 'CSV' && (
          <div className="p-4 bg-slate-900/60 border border-dashed border-slate-700 rounded-lg text-center">
            <Upload className="w-6 h-6 mx-auto text-slate-400 mb-2" />
            <p className="text-xs text-slate-300 mb-1">Select or drop a CSV file with customer data</p>
            <p className="text-[10px] text-slate-500 mb-3">Columns can include customer_id, name, email, mobile, city, segment</p>
            <label className="inline-block px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-white rounded text-xs font-medium cursor-pointer transition border border-slate-600">
              {uploading ? 'Processing File...' : 'Choose CSV File'}
              <input type="file" accept=".csv" onChange={handleFileUpload} disabled={uploading} className="hidden" />
            </label>
          </div>
        )}

        {/* Action Button */}
        <div className="pt-2 flex justify-end">
          <button
            onClick={handleRunBatch}
            disabled={loading}
            className="flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold shadow-md shadow-blue-900/20 transition disabled:opacity-50"
          >
            <Play className="w-4 h-4 mr-2" />
            <span>{loading ? 'Executing Privacy Ingestion...' : 'Execute Ingestion Batch'}</span>
          </button>
        </div>
      </div>

      {/* Source Database Records Preview (Admin view) */}
      <div className="bg-[#0F172A] border border-slate-800 rounded-xl p-5">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wider">
            Raw Source Records Preview (Admin View)
          </h3>
          <span className="text-[10px] font-mono text-slate-500">
            Total In Source DB: {config?.total_source_records ?? 0}
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-900/80 text-[11px] font-mono text-slate-400 uppercase tracking-wider border-b border-slate-800">
              <tr>
                <th className="p-2.5">ID</th>
                <th className="p-2.5">Name</th>
                <th className="p-2.5">Email</th>
                <th className="p-2.5">Mobile</th>
                <th className="p-2.5">City</th>
                <th className="p-2.5">Segment</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono text-[11px]">
              {records.map((r) => (
                <tr key={r.customer_id} className="hover:bg-slate-900/40">
                  <td className="p-2.5 text-blue-400 font-semibold">{r.customer_id}</td>
                  <td className="p-2.5">{r.name}</td>
                  <td className="p-2.5">{r.email}</td>
                  <td className="p-2.5">{r.mobile}</td>
                  <td className="p-2.5 text-slate-400">{r.city}</td>
                  <td className="p-2.5 text-slate-400">{r.segment}</td>
                </tr>
              ))}
              {records.length === 0 && (
                <tr>
                  <td colSpan={6} className="p-4 text-center text-slate-500">
                    No source records loaded yet.
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
