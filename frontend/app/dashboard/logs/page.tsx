"use client";
import { useEffect, useState, useRef } from "react";
import { apiFetch, formatRelativeTime, severityColor } from "@/lib/utils";
import { FileText, Search, Upload, RefreshCw, Download, Filter } from "lucide-react";

export default function LogsPage() {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [uploading, setUploading] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);
  const perPage = 50;

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (search) params.set("search", search);
      if (categoryFilter) params.set("category", categoryFilter);
      params.set("page", String(page));
      params.set("per_page", String(perPage));
      const data = await apiFetch(`/api/logs?${params.toString()}`);
      setLogs(data.events || []);
      setTotal(data.total || 0);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchLogs(); }, [page, categoryFilter]);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setError("");
    try {
      const token = localStorage.getItem("token");
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch("/api/logs/upload", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });
      if (!res.ok) throw new Error("Upload failed");
      const data = await res.json();
      alert(`Uploaded ${data.events_count || 0} log entries, generated ${data.alerts_generated || 0} alerts`);
      fetchLogs();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setUploading(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  const exportLogs = async () => {
    try {
      const token = localStorage.getItem("token");
      const res = await fetch("/api/logs/export?format=csv", {
        headers: { Authorization: `Bearer ${token}` },
      });
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "logs_export.csv";
      a.click();
      URL.revokeObjectURL(url);
    } catch (e: any) {
      setError(e.message);
    }
  };

  const totalPages = Math.ceil(total / perPage);

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Security Logs</h1>
          <p className="text-sm text-slate-400 mt-1">{total} log entries</p>
        </div>
        <div className="flex gap-2">
          <input ref={fileRef} type="file" accept=".csv,.log,.json,.txt" onChange={handleUpload} className="hidden" />
          <button onClick={() => fileRef.current?.click()} disabled={uploading} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-sm disabled:opacity-50">
            <Upload className="w-4 h-4" />{uploading ? "Uploading..." : "Upload Logs"}
          </button>
          <button onClick={exportLogs} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800/50 border border-slate-700/50 text-slate-300 hover:text-white text-sm">
            <Download className="w-4 h-4" />Export
          </button>
          <button onClick={fetchLogs} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800/50 border border-slate-700/50 text-slate-300 hover:text-white text-sm">
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="flex flex-col md:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && fetchLogs()}
            placeholder="Search logs..."
            className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-800/50 border border-slate-700/50 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-blue-500"
          />
        </div>
        <select value={categoryFilter} onChange={(e) => { setCategoryFilter(e.target.value); setPage(1); }} className="px-4 py-2.5 rounded-xl bg-slate-800/50 border border-slate-700/50 text-slate-300 text-sm focus:outline-none focus:border-blue-500">
          <option value="">All Categories</option>
          <option value="authentication">Authentication</option>
          <option value="network">Network</option>
          <option value="firewall">Firewall</option>
          <option value="application">Application</option>
          <option value="system">System</option>
          <option value="web_server">Web Server</option>
        </select>
      </div>

      {error && <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">{error}</div>}

      <div className="rounded-2xl border border-slate-800/50 bg-slate-900/30 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full data-table">
            <thead>
              <tr>
                <th className="text-left px-4 py-3">Time</th>
                <th className="text-left px-4 py-3">Category</th>
                <th className="text-left px-4 py-3">Source IP</th>
                <th className="text-left px-4 py-3">Event</th>
                <th className="text-left px-4 py-3">Raw</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                [...Array(8)].map((_, i) => (
                  <tr key={i}><td colSpan={5} className="px-4 py-3"><div className="h-4 bg-slate-800/50 rounded animate-pulse" /></td></tr>
                ))
              ) : logs.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-4 py-12 text-center">
                    <FileText className="w-10 h-10 text-slate-600 mx-auto mb-3" />
                    <p className="text-slate-400 text-sm">No logs found.</p>
                    <p className="text-slate-500 text-xs mt-1">Upload a log file or run a simulation to generate data.</p>
                  </td>
                </tr>
              ) : (
                logs.map((log, i) => (
                  <tr key={log.id || i}>
                    <td className="px-4 py-3 text-xs text-slate-400 whitespace-nowrap">
                      {log.timestamp ? new Date(log.timestamp).toLocaleString() : "N/A"}
                    </td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-0.5 rounded text-xs bg-slate-800/50 text-slate-300 capitalize">
                        {log.category || log.event_category || "N/A"}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm font-mono text-slate-300">{log.source_ip || "N/A"}</td>
                    <td className="px-4 py-3 text-sm text-slate-300 max-w-xs truncate">{log.event_type || log.message || "N/A"}</td>
                    <td className="px-4 py-3">
                      {log.raw_log && (
                        <span className="text-xs text-blue-400 hover:text-blue-300 cursor-pointer" title={log.raw_log}>
                          View
                        </span>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <span className="text-sm text-slate-500">Page {page} of {totalPages}</span>
          <div className="flex gap-2">
            <button onClick={() => setPage(Math.max(1, page - 1))} disabled={page === 1} className="px-4 py-2 rounded-xl bg-slate-800/50 border border-slate-700/50 text-slate-300 text-sm disabled:opacity-50">Previous</button>
            <button onClick={() => setPage(Math.min(totalPages, page + 1))} disabled={page === totalPages} className="px-4 py-2 rounded-xl bg-slate-800/50 border border-slate-700/50 text-slate-300 text-sm disabled:opacity-50">Next</button>
          </div>
        </div>
      )}
    </div>
  );
}
