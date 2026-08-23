"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { apiFetch, formatRelativeTime, severityColor, statusColor } from "@/lib/utils";
import { AlertTriangle, Search, Filter, ChevronDown, ArrowUpDown, RefreshCw } from "lucide-react";

interface Alert {
  id: number;
  title: string;
  severity: string;
  status: string;
  source_ip: string;
  destination_ip: string;
  threat_type: string;
  confidence: number;
  risk_score: number;
  created_at: string;
}

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [severityFilter, setSeverityFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [sortBy, setSortBy] = useState("created_at");
  const [sortDir, setSortDir] = useState("desc");
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const perPage = 20;

  const fetchAlerts = async () => {
    setLoading(true);
    setError("");
    try {
      const params = new URLSearchParams();
      if (search) params.set("search", search);
      if (severityFilter) params.set("severity", severityFilter);
      if (statusFilter) params.set("status", statusFilter);
      params.set("sort_by", sortBy);
      params.set("sort_dir", sortDir);
      params.set("page", String(page));
      params.set("per_page", String(perPage));
      
      const data = await apiFetch(`/api/alerts?${params.toString()}`);
      setAlerts(data.alerts || []);
      setTotal(data.total || 0);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAlerts(); }, [page, severityFilter, statusFilter, sortBy, sortDir]);

  const toggleSort = (field: string) => {
    if (sortBy === field) {
      setSortDir(sortDir === "desc" ? "asc" : "desc");
    } else {
      setSortBy(field);
      setSortDir("desc");
    }
  };

  const totalPages = Math.ceil(total / perPage);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Security Alerts</h1>
          <p className="text-sm text-slate-400 mt-1">{total} total alerts detected</p>
        </div>
        <button onClick={fetchAlerts} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800/50 border border-slate-700/50 text-slate-300 hover:text-white text-sm transition-colors">
          <RefreshCw className="w-4 h-4" />Refresh
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-col md:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <input
            type="text"
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            onKeyDown={(e) => e.key === "Enter" && fetchAlerts()}
            placeholder="Search alerts..."
            className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-800/50 border border-slate-700/50 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-blue-500"
          />
        </div>
        <select
          value={severityFilter}
          onChange={(e) => { setSeverityFilter(e.target.value); setPage(1); }}
          className="px-4 py-2.5 rounded-xl bg-slate-800/50 border border-slate-700/50 text-slate-300 text-sm focus:outline-none focus:border-blue-500 appearance-none cursor-pointer"
        >
          <option value="">All Severities</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
        <select
          value={statusFilter}
          onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
          className="px-4 py-2.5 rounded-xl bg-slate-800/50 border border-slate-700/50 text-slate-300 text-sm focus:outline-none focus:border-blue-500 appearance-none cursor-pointer"
        >
          <option value="">All Statuses</option>
          <option value="new">New</option>
          <option value="acknowledged">Acknowledged</option>
          <option value="investigating">Investigating</option>
          <option value="resolved">Resolved</option>
          <option value="false_positive">False Positive</option>
        </select>
      </div>

      {/* Error */}
      {error && (
        <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
          {error}
        </div>
      )}

      {/* Table */}
      <div className="rounded-2xl border border-slate-800/50 bg-slate-900/30 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full data-table">
            <thead>
              <tr>
                <th className="text-left px-4 py-3 cursor-pointer hover:text-slate-300" onClick={() => toggleSort("severity")}>
                  <span className="flex items-center gap-1">Severity <ArrowUpDown className="w-3 h-3" /></span>
                </th>
                <th className="text-left px-4 py-3">Alert</th>
                <th className="text-left px-4 py-3">Source</th>
                <th className="text-left px-4 py-3">Destination</th>
                <th className="text-left px-4 py-3">Confidence</th>
                <th className="text-left px-4 py-3 cursor-pointer hover:text-slate-300" onClick={() => toggleSort("status")}>
                  <span className="flex items-center gap-1">Status <ArrowUpDown className="w-3 h-3" /></span>
                </th>
                <th className="text-left px-4 py-3 cursor-pointer hover:text-slate-300" onClick={() => toggleSort("created_at")}>
                  <span className="flex items-center gap-1">Time <ArrowUpDown className="w-3 h-3" /></span>
                </th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                [...Array(5)].map((_, i) => (
                  <tr key={i}>
                    <td colSpan={7} className="px-4 py-4">
                      <div className="h-4 bg-slate-800/50 rounded animate-pulse" />
                    </td>
                  </tr>
                ))
              ) : alerts.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-12 text-center">
                    <AlertTriangle className="w-10 h-10 text-slate-600 mx-auto mb-3" />
                    <p className="text-slate-400 text-sm">No alerts detected.</p>
                    <p className="text-slate-500 text-xs mt-1">Upload logs or run a simulation to generate alerts.</p>
                  </td>
                </tr>
              ) : (
                alerts.map((alert) => (
                  <tr key={alert.id} className="cursor-pointer">
                    <td className="px-4 py-3">
                      <span className={`px-2.5 py-1 rounded-lg text-xs font-medium border ${severityColor(alert.severity)}`}>
                        {alert.severity?.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <Link href={`/dashboard/alerts/${alert.id}`} className="text-sm text-white hover:text-blue-400 transition-colors">
                        {alert.title}
                      </Link>
                      <div className="text-xs text-slate-500 mt-0.5">{alert.threat_type}</div>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-sm font-mono text-slate-300">{alert.source_ip || "N/A"}</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-sm font-mono text-slate-300">{alert.destination_ip || "N/A"}</span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <div className="w-16 h-1.5 bg-slate-700 rounded-full overflow-hidden">
                          <div className="h-full bg-blue-500 rounded-full" style={{ width: `${alert.confidence || 0}%` }} />
                        </div>
                        <span className="text-xs text-slate-400">{alert.confidence || 0}%</span>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`px-2.5 py-1 rounded-lg text-xs font-medium ${statusColor(alert.status)}`}>
                        {alert.status?.replace("_", " ")}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-xs text-slate-400">{formatRelativeTime(alert.created_at)}</span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <span className="text-sm text-slate-500">Page {page} of {totalPages}</span>
          <div className="flex gap-2">
            <button onClick={() => setPage(Math.max(1, page - 1))} disabled={page === 1} className="px-4 py-2 rounded-xl bg-slate-800/50 border border-slate-700/50 text-slate-300 text-sm disabled:opacity-50 hover:bg-slate-800">
              Previous
            </button>
            <button onClick={() => setPage(Math.min(totalPages, page + 1))} disabled={page === totalPages} className="px-4 py-2 rounded-xl bg-slate-800/50 border border-slate-700/50 text-slate-300 text-sm disabled:opacity-50 hover:bg-slate-800">
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
