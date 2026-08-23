"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { apiFetch, formatRelativeTime, severityColor, statusColor } from "@/lib/utils";
import { FileWarning, Search, Plus, RefreshCw } from "lucide-react";

interface Incident {
  id: number;
  title: string;
  severity: string;
  status: string;
  description: string;
  assigned_to: string;
  created_at: string;
  updated_at: string;
}

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const perPage = 20;

  const fetchIncidents = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (search) params.set("search", search);
      if (statusFilter) params.set("status", statusFilter);
      params.set("page", String(page));
      params.set("per_page", String(perPage));
      const data = await apiFetch(`/api/incidents?${params.toString()}`);
      setIncidents(data.incidents || []);
      setTotal(data.total || 0);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchIncidents(); }, [page, statusFilter]);

  const totalPages = Math.ceil(total / perPage);

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Incidents</h1>
          <p className="text-sm text-slate-400 mt-1">{total} total incidents</p>
        </div>
        <div className="flex gap-2">
          <button onClick={fetchIncidents} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800/50 border border-slate-700/50 text-slate-300 hover:text-white text-sm">
            <RefreshCw className="w-4 h-4" />Refresh
          </button>
        </div>
      </div>

      <div className="flex flex-col md:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input
            type="text"
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            onKeyDown={(e) => e.key === "Enter" && fetchIncidents()}
            placeholder="Search incidents..."
            className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-800/50 border border-slate-700/50 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-blue-500"
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
          className="px-4 py-2.5 rounded-xl bg-slate-800/50 border border-slate-700/50 text-slate-300 text-sm focus:outline-none focus:border-blue-500"
        >
          <option value="">All Statuses</option>
          <option value="new">New</option>
          <option value="triaged">Triaged</option>
          <option value="investigating">Investigating</option>
          <option value="contained">Contained</option>
          <option value="resolved">Resolved</option>
        </select>
      </div>

      {error && <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">{error}</div>}

      <div className="rounded-2xl border border-slate-800/50 bg-slate-900/30 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full data-table">
            <thead>
              <tr>
                <th className="text-left px-4 py-3">Severity</th>
                <th className="text-left px-4 py-3">Incident</th>
                <th className="text-left px-4 py-3">Status</th>
                <th className="text-left px-4 py-3">Assigned To</th>
                <th className="text-left px-4 py-3">Created</th>
                <th className="text-left px-4 py-3">Updated</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                [...Array(5)].map((_, i) => (
                  <tr key={i}><td colSpan={6} className="px-4 py-4"><div className="h-4 bg-slate-800/50 rounded animate-pulse" /></td></tr>
                ))
              ) : incidents.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-12 text-center">
                    <FileWarning className="w-10 h-10 text-slate-600 mx-auto mb-3" />
                    <p className="text-slate-400 text-sm">No incidents found.</p>
                    <p className="text-slate-500 text-xs mt-1">Create incidents from alerts or run a simulation.</p>
                  </td>
                </tr>
              ) : (
                incidents.map((inc) => (
                  <tr key={inc.id}>
                    <td className="px-4 py-3">
                      <span className={`px-2.5 py-1 rounded-lg text-xs font-medium border ${severityColor(inc.severity)}`}>
                        {inc.severity?.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <Link href={`/dashboard/incidents/${inc.id}`} className="text-sm text-white hover:text-blue-400 transition-colors">
                        {inc.title}
                      </Link>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`px-2.5 py-1 rounded-lg text-xs font-medium ${statusColor(inc.status)}`}>
                        {inc.status?.replace("_", " ")}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-sm text-slate-400">{inc.assigned_to || "Unassigned"}</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-xs text-slate-400">{formatRelativeTime(inc.created_at)}</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-xs text-slate-400">{formatRelativeTime(inc.updated_at)}</span>
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
