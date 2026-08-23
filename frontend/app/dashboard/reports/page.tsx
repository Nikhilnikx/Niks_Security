"use client";
import { useEffect, useState } from "react";
import { apiFetch, formatRelativeTime } from "@/lib/utils";
import { BarChart3, Plus, Download, FileText, Trash2, X } from "lucide-react";

export default function ReportsPage() {
  const [reports, setReports] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showGen, setShowGen] = useState(false);
  const [form, setForm] = useState({ title: "", report_type: "security_summary", date_from: "", date_to: "" });
  const [generating, setGenerating] = useState(false);

  const fetchReports = async () => {
    try {
      const data = await apiFetch("/api/reports");
      setReports(data.reports || data || []);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchReports(); }, []);

  const generate = async () => {
    setGenerating(true);
    try {
      await apiFetch("/api/reports", { method: "POST", body: JSON.stringify(form) });
      setShowGen(false);
      fetchReports();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setGenerating(false);
    }
  };

  const exportReport = async (id: number, format: string) => {
    try {
      const token = localStorage.getItem("token");
      const res = await fetch(`/api/reports/${id}/export?format=${format}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `report_${id}.${format}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e: any) {
      setError(e.message);
    }
  };

  const deleteReport = async (id: number) => {
    if (!confirm("Delete this report?")) return;
    try {
      await apiFetch(`/api/reports/${id}`, { method: "DELETE" });
      fetchReports();
    } catch (e: any) {
      setError(e.message);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Reports</h1>
          <p className="text-sm text-slate-400 mt-1">{reports.length} reports</p>
        </div>
        <button onClick={() => setShowGen(true)} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-sm">
          <Plus className="w-4 h-4" />Generate Report
        </button>
      </div>

      {error && <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">{error}</div>}

      {/* Generate Modal */}
      {showGen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
          <div className="w-full max-w-md p-6 rounded-2xl border border-slate-800/50 bg-[#0b1120]">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">Generate Report</h3>
              <button onClick={() => setShowGen(false)} className="text-slate-400 hover:text-white"><X className="w-5 h-5" /></button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-slate-300 mb-1">Title</label>
                <input value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} className="w-full px-4 py-2.5 rounded-xl bg-slate-800/50 border border-slate-700/50 text-white text-sm focus:outline-none focus:border-blue-500" placeholder="Security Summary Report" />
              </div>
              <div>
                <label className="block text-sm text-slate-300 mb-1">Type</label>
                <select value={form.report_type} onChange={(e) => setForm({ ...form, report_type: e.target.value })} className="w-full px-4 py-2.5 rounded-xl bg-slate-800/50 border border-slate-700/50 text-white text-sm focus:outline-none focus:border-blue-500">
                  <option value="security_summary">Security Summary</option>
                  <option value="incident_report">Incident Report</option>
                  <option value="threat_report">Threat Report</option>
                  <option value="executive_summary">Executive Summary</option>
                  <option value="detection_report">Detection Report</option>
                </select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-slate-300 mb-1">Date From</label>
                  <input type="date" value={form.date_from} onChange={(e) => setForm({ ...form, date_from: e.target.value })} className="w-full px-4 py-2.5 rounded-xl bg-slate-800/50 border border-slate-700/50 text-white text-sm focus:outline-none focus:border-blue-500" />
                </div>
                <div>
                  <label className="block text-sm text-slate-300 mb-1">Date To</label>
                  <input type="date" value={form.date_to} onChange={(e) => setForm({ ...form, date_to: e.target.value })} className="w-full px-4 py-2.5 rounded-xl bg-slate-800/50 border border-slate-700/50 text-white text-sm focus:outline-none focus:border-blue-500" />
                </div>
              </div>
              <button onClick={generate} disabled={generating} className="w-full py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium disabled:opacity-50">
                {generating ? "Generating..." : "Generate Report"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Reports List */}
      {loading ? (
        <div className="space-y-3">
          {[...Array(3)].map((_, i) => <div key={i} className="h-24 rounded-2xl bg-slate-800/30 animate-pulse" />)}
        </div>
      ) : reports.length === 0 ? (
        <div className="text-center py-16 rounded-2xl border border-slate-800/50 bg-slate-900/30">
          <BarChart3 className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <p className="text-slate-400">No reports generated yet.</p>
          <p className="text-slate-500 text-sm mt-1">Generate your first report to analyze security data.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {reports.map((report) => (
            <div key={report.id} className="p-5 rounded-2xl border border-slate-800/50 bg-slate-900/30 flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center">
                  <FileText className="w-5 h-5 text-purple-400" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-white">{report.title}</h3>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xs text-slate-500 capitalize">{report.report_type?.replace("_", " ")}</span>
                    <span className="text-xs text-slate-600">·</span>
                    <span className="text-xs text-slate-500">{formatRelativeTime(report.created_at)}</span>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button onClick={() => exportReport(report.id, "json")} className="px-3 py-1.5 rounded-lg text-xs text-slate-400 hover:text-white hover:bg-slate-800/50 transition-colors">JSON</button>
                <button onClick={() => exportReport(report.id, "csv")} className="px-3 py-1.5 rounded-lg text-xs text-slate-400 hover:text-white hover:bg-slate-800/50 transition-colors">CSV</button>
                <button onClick={() => deleteReport(report.id)} className="p-2 rounded-lg text-slate-500 hover:text-red-400 hover:bg-red-500/10">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
