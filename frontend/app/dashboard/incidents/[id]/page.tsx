"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { apiFetch, formatRelativeTime, severityColor, statusColor } from "@/lib/utils";
import { ArrowLeft, AlertTriangle, Clock, User, FileText, Shield, MessageSquare } from "lucide-react";

export default function IncidentDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [incident, setIncident] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [note, setNote] = useState("");
  const [actionLoading, setActionLoading] = useState("");

  const fetchIncident = async () => {
    try {
      const data = await apiFetch(`/api/incidents/${params.id}`);
      setIncident(data);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchIncident(); }, [params.id]);

  const updateStatus = async (status: string) => {
    setActionLoading(status);
    try {
      await apiFetch(`/api/incidents/${params.id}/status`, {
        method: "PATCH",
        body: JSON.stringify({ status }),
      });
      await fetchIncident();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setActionLoading("");
    }
  };

  const addNote = async () => {
    if (!note.trim()) return;
    setActionLoading("note");
    try {
      await apiFetch(`/api/incidents/${params.id}/notes`, {
        method: "POST",
        body: JSON.stringify({ content: note }),
      });
      setNote("");
      await fetchIncident();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setActionLoading("");
    }
  };

  if (loading) return (
    <div className="space-y-6 animate-pulse">
      <div className="h-8 w-48 bg-slate-800/50 rounded" />
      <div className="h-96 bg-slate-800/50 rounded-2xl" />
    </div>
  );

  if (error && !incident) return (
    <div className="flex items-center justify-center h-96">
      <div className="text-center p-8 rounded-2xl border border-slate-800/50 bg-slate-900/30">
        <AlertTriangle className="w-12 h-12 text-yellow-500 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-white mb-2">Incident not found</h3>
        <Link href="/dashboard/incidents" className="px-4 py-2 rounded-xl bg-blue-600 text-white text-sm">Back to Incidents</Link>
      </div>
    </div>
  );

  if (!incident) return null;

  const statusFlow = ["new", "triaged", "investigating", "contained", "resolved"];
  const currentIdx = statusFlow.indexOf(incident.status);

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/dashboard/incidents" className="p-2 rounded-xl hover:bg-slate-800/50 text-slate-400 hover:text-white">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <span className={`px-3 py-1 rounded-lg text-xs font-medium border ${severityColor(incident.severity)}`}>
              {incident.severity?.toUpperCase()}
            </span>
            <span className={`px-3 py-1 rounded-lg text-xs font-medium ${statusColor(incident.status)}`}>
              {incident.status?.replace("_", " ")}
            </span>
          </div>
          <h1 className="text-2xl font-bold text-white mt-2">{incident.title}</h1>
        </div>
      </div>

      {/* Status Flow */}
      <div className="p-4 rounded-2xl border border-slate-800/50 bg-slate-900/30">
        <div className="flex items-center justify-between">
          {statusFlow.map((s, i) => (
            <div key={s} className="flex items-center">
              <div className="flex flex-col items-center">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-medium border ${
                  i <= currentIdx ? "bg-blue-600 border-blue-500 text-white" : "bg-slate-800 border-slate-700 text-slate-500"
                }`}>
                  {i + 1}
                </div>
                <span className={`text-xs mt-1 capitalize ${i <= currentIdx ? "text-blue-400" : "text-slate-500"}`}>{s}</span>
              </div>
              {i < statusFlow.length - 1 && (
                <div className={`w-12 sm:w-20 h-0.5 mx-1 ${i < currentIdx ? "bg-blue-600" : "bg-slate-700"}`} />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Actions */}
      <div className="flex flex-wrap gap-2">
        {statusFlow.map((s, i) => (
          i > currentIdx && (
            <button
              key={s}
              onClick={() => updateStatus(s)}
              disabled={!!actionLoading}
              className="px-4 py-2 rounded-xl bg-blue-600/10 border border-blue-500/20 text-blue-400 text-sm hover:bg-blue-600/20 transition-colors"
            >
              Move to {s}
            </button>
          )
        ))}
      </div>

      {error && <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">{error}</div>}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="p-6 rounded-2xl border border-slate-800/50 bg-slate-900/30">
            <h3 className="text-sm font-semibold text-white mb-4">Incident Details</h3>
            <p className="text-sm text-slate-400 mb-4">{incident.description || "No description provided."}</p>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-xs text-slate-500 mb-0.5">Assigned To</div>
                <div className="text-sm text-slate-300">{incident.assigned_to || "Unassigned"}</div>
              </div>
              <div>
                <div className="text-xs text-slate-500 mb-0.5">Created</div>
                <div className="text-sm text-slate-300">{new Date(incident.created_at).toLocaleString()}</div>
              </div>
              <div>
                <div className="text-xs text-slate-500 mb-0.5">Updated</div>
                <div className="text-sm text-slate-300">{new Date(incident.updated_at).toLocaleString()}</div>
              </div>
            </div>
          </div>

          {/* Related Alerts */}
          {incident.related_alerts?.length > 0 && (
            <div className="p-6 rounded-2xl border border-slate-800/50 bg-slate-900/30">
              <h3 className="text-sm font-semibold text-white mb-3">Related Alerts</h3>
              <div className="space-y-2">
                {incident.related_alerts.map((a: any) => (
                  <Link key={a.id} href={`/dashboard/alerts/${a.id}`} className="flex items-center justify-between p-3 rounded-xl hover:bg-slate-800/30 transition-colors">
                    <div className="flex items-center gap-3">
                      <span className={`px-2 py-0.5 rounded text-xs font-medium border ${severityColor(a.severity)}`}>
                        {a.severity?.toUpperCase()}
                      </span>
                      <span className="text-sm text-slate-300">{a.title}</span>
                    </div>
                    <span className="text-xs text-slate-500">{formatRelativeTime(a.created_at)}</span>
                  </Link>
                ))}
              </div>
            </div>
          )}

          {/* Notes */}
          <div className="p-6 rounded-2xl border border-slate-800/50 bg-slate-900/30">
            <h3 className="text-sm font-semibold text-white mb-3">Analyst Notes</h3>
            <div className="flex gap-2 mb-4">
              <input
                type="text"
                value={note}
                onChange={(e) => setNote(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && addNote()}
                placeholder="Add a note..."
                className="flex-1 px-4 py-2.5 rounded-xl bg-slate-800/50 border border-slate-700/50 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-blue-500"
              />
              <button
                onClick={addNote}
                disabled={!!actionLoading || !note.trim()}
                className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-sm disabled:opacity-50"
              >
                Add
              </button>
            </div>
            {incident.notes?.length > 0 ? (
              <div className="space-y-3">
                {incident.notes.map((n: any, i: number) => (
                  <div key={i} className="p-3 rounded-xl bg-slate-800/30">
                    <div className="flex items-center gap-2 mb-1">
                      <User className="w-3 h-3 text-slate-500" />
                      <span className="text-xs text-slate-500">{n.author || "Analyst"}</span>
                      <span className="text-xs text-slate-600">·</span>
                      <span className="text-xs text-slate-500">{formatRelativeTime(n.created_at)}</span>
                    </div>
                    <p className="text-sm text-slate-400">{n.content}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-slate-500">No notes yet.</p>
            )}
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          <div className="p-6 rounded-2xl border border-slate-800/50 bg-slate-900/30">
            <h3 className="text-sm font-semibold text-white mb-3">IOC Summary</h3>
            {incident.iocs?.length > 0 ? (
              <div className="space-y-2">
                {incident.iocs.map((ioc: any, i: number) => (
                  <div key={i} className="p-2 rounded-lg bg-slate-800/30 font-mono text-xs text-red-400 truncate">
                    {ioc}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-slate-500">No IOCs identified yet.</p>
            )}
          </div>

          <div className="p-6 rounded-2xl border border-slate-800/50 bg-slate-900/30">
            <h3 className="text-sm font-semibold text-white mb-3">Evidence</h3>
            {incident.evidence?.length > 0 ? (
              <div className="space-y-2">
                {incident.evidence.map((e: any, i: number) => (
                  <div key={i} className="p-2 rounded-lg bg-slate-800/30 text-xs text-slate-400">
                    {typeof e === "string" ? e : JSON.stringify(e)}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-slate-500">No evidence collected.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
