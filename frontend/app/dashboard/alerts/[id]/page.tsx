"use client";
import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { apiFetch, formatRelativeTime, severityColor, statusColor } from "@/lib/utils";
import { AlertTriangle, ArrowLeft, Clock, Globe, Shield, Target, FileText, User, ExternalLink, CheckCircle, XCircle, Ban, Bot } from "lucide-react";
import Link from "next/link";

export default function AlertDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [alert, setAlert] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [actionLoading, setActionLoading] = useState("");

  const fetchAlert = async () => {
    try {
      const data = await apiFetch(`/api/alerts/${params.id}`);
      setAlert(data);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAlert(); }, [params.id]);

  const updateStatus = async (status: string) => {
    setActionLoading(status);
    try {
      await apiFetch(`/api/alerts/${params.id}/status`, {
        method: "PATCH",
        body: JSON.stringify({ status }),
      });
      await fetchAlert();
    } catch (e: any) {
      setError(e.message);
    } finally {
      setActionLoading("");
    }
  };

  const createIncident = async () => {
    setActionLoading("incident");
    try {
      const data = await apiFetch(`/api/alerts/${params.id}/create-incident`, { method: "POST" });
      router.push(`/dashboard/incidents/${data.id}`);
    } catch (e: any) {
      setError(e.message);
      setActionLoading("");
    }
  };

  if (loading) return (
    <div className="space-y-6 animate-pulse">
      <div className="h-8 w-48 bg-slate-800/50 rounded" />
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 h-96 bg-slate-800/50 rounded-2xl" />
        <div className="h-96 bg-slate-800/50 rounded-2xl" />
      </div>
    </div>
  );

  if (error && !alert) return (
    <div className="flex items-center justify-center h-96">
      <div className="text-center p-8 rounded-2xl border border-slate-800/50 bg-slate-900/30">
        <AlertTriangle className="w-12 h-12 text-yellow-500 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-white mb-2">Alert not found</h3>
        <p className="text-slate-400 text-sm mb-4">{error}</p>
        <Link href="/dashboard/alerts" className="px-4 py-2 rounded-xl bg-blue-600 text-white text-sm">Back to Alerts</Link>
      </div>
    </div>
  );

  if (!alert) return null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link href="/dashboard/alerts" className="p-2 rounded-xl hover:bg-slate-800/50 text-slate-400 hover:text-white transition-colors">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <span className={`px-3 py-1 rounded-lg text-xs font-medium border ${severityColor(alert.severity)}`}>
              {alert.severity?.toUpperCase()}
            </span>
            <span className={`px-3 py-1 rounded-lg text-xs font-medium ${statusColor(alert.status)}`}>
              {alert.status?.replace("_", " ")}
            </span>
          </div>
          <h1 className="text-2xl font-bold text-white mt-2">{alert.title}</h1>
        </div>
        <div className="flex gap-2">
          {alert.status !== "false_positive" && (
            <button
              onClick={() => updateStatus("false_positive")}
              disabled={!!actionLoading}
              className="px-4 py-2 rounded-xl bg-slate-800/50 border border-slate-700/50 text-slate-300 text-sm hover:bg-slate-800 transition-colors"
            >
              Mark False Positive
            </button>
          )}
          {alert.status === "new" && (
            <button
              onClick={() => updateStatus("acknowledged")}
              disabled={!!actionLoading}
              className="px-4 py-2 rounded-xl bg-yellow-600/10 border border-yellow-500/20 text-yellow-400 text-sm hover:bg-yellow-600/20 transition-colors"
            >
              Acknowledge
            </button>
          )}
          <button
            onClick={createIncident}
            disabled={!!actionLoading}
            className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-sm transition-colors"
          >
            {actionLoading === "incident" ? "Creating..." : "Create Incident"}
          </button>
          <button
            onClick={() => window.dispatchEvent(new CustomEvent("copilot-investigate-alert", { detail: { alertId: Number(params.id) } }))}
            className="px-4 py-2 rounded-xl bg-gradient-to-r from-purple-600 to-violet-600 hover:from-purple-500 hover:to-violet-500 text-white text-sm font-medium transition-all shadow-lg shadow-purple-500/20 flex items-center gap-2"
          >
            <Bot className="w-4 h-4" />
            Investigate with AI
          </button>
        </div>
      </div>

      {error && (
        <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">{error}</div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Details */}
          <div className="p-6 rounded-2xl border border-slate-800/50 bg-slate-900/30">
            <h3 className="text-sm font-semibold text-white mb-4">Alert Details</h3>
            <div className="grid grid-cols-2 gap-4">
              <DetailItem label="Threat Type" value={alert.threat_type} />
              <DetailItem label="Detection Rule" value={alert.detection_rule_name || "N/A"} />
              <DetailItem label="Source IP" value={alert.source_ip || "N/A"} mono />
              <DetailItem label="Destination IP" value={alert.destination_ip || "N/A"} mono />
              <DetailItem label="Source Port" value={alert.source_port?.toString() || "N/A"} />
              <DetailItem label="Destination Port" value={alert.destination_port?.toString() || "N/A"} />
              <DetailItem label="Username" value={alert.username || "N/A"} />
              <DetailItem label="Hostname" value={alert.hostname || "N/A"} mono />
              <DetailItem label="MITRE Technique" value={alert.mitre_technique || "N/A"} />
              <DetailItem label="MITRE Tactic" value={alert.mitre_tactic || "N/A"} />
              <DetailItem label="Risk Score" value={`${alert.risk_score || 0}/100`} />
              <DetailItem label="Confidence" value={`${alert.confidence || 0}%`} />
              <DetailItem label="Created" value={new Date(alert.created_at).toLocaleString()} />
              <DetailItem label="Updated" value={new Date(alert.updated_at).toLocaleString()} />
            </div>
          </div>

          {/* Description */}
          {alert.description && (
            <div className="p-6 rounded-2xl border border-slate-800/50 bg-slate-900/30">
              <h3 className="text-sm font-semibold text-white mb-3">Description</h3>
              <p className="text-sm text-slate-400 leading-relaxed">{alert.description}</p>
            </div>
          )}

          {/* Raw Log */}
          {alert.raw_log && (
            <div className="p-6 rounded-2xl border border-slate-800/50 bg-slate-900/30">
              <h3 className="text-sm font-semibold text-white mb-3">Raw Log</h3>
              <pre className="text-xs text-slate-400 bg-slate-800/50 rounded-xl p-4 overflow-x-auto font-mono whitespace-pre-wrap">
                {typeof alert.raw_log === "string" ? alert.raw_log : JSON.stringify(alert.raw_log, null, 2)}
              </pre>
            </div>
          )}

          {/* Evidence */}
          {alert.evidence && (
            <div className="p-6 rounded-2xl border border-slate-800/50 bg-slate-900/30">
              <h3 className="text-sm font-semibold text-white mb-3">Evidence</h3>
              <pre className="text-xs text-slate-400 bg-slate-800/50 rounded-xl p-4 overflow-x-auto font-mono whitespace-pre-wrap">
                {typeof alert.evidence === "string" ? alert.evidence : JSON.stringify(alert.evidence, null, 2)}
              </pre>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Severity & Score */}
          <div className="p-6 rounded-2xl border border-slate-800/50 bg-slate-900/30">
            <h3 className="text-sm font-semibold text-white mb-4">Risk Assessment</h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-xs text-slate-400 mb-1">
                  <span>Risk Score</span>
                  <span>{alert.risk_score || 0}/100</span>
                </div>
                <div className="w-full h-2 bg-slate-700 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all ${(alert.risk_score || 0) >= 80 ? "bg-red-500" : (alert.risk_score || 0) >= 60 ? "bg-orange-500" : (alert.risk_score || 0) >= 40 ? "bg-yellow-500" : "bg-green-500"}`}
                    style={{ width: `${alert.risk_score || 0}%` }}
                  />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-xs text-slate-400 mb-1">
                  <span>Confidence</span>
                  <span>{alert.confidence || 0}%</span>
                </div>
                <div className="w-full h-2 bg-slate-700 rounded-full overflow-hidden">
                  <div className="h-full bg-blue-500 rounded-full" style={{ width: `${alert.confidence || 0}%` }} />
                </div>
              </div>
            </div>
          </div>

          {/* Recommended Actions */}
          <div className="p-6 rounded-2xl border border-slate-800/50 bg-slate-900/30">
            <h3 className="text-sm font-semibold text-white mb-3">Recommended Actions</h3>
            <div className="space-y-2">
              {alert.severity === "critical" && (
                <>
                  <ActionItem icon={Ban} text="Block source IP at firewall" />
                  <ActionItem icon={User} text="Check for compromised accounts" />
                  <ActionItem icon={Shield} text="Isolate affected systems" />
                </>
              )}
              {alert.severity === "high" && (
                <>
                  <ActionItem icon={AlertTriangle} text="Review related alerts" />
                  <ActionItem icon={User} text="Verify user activity" />
                </>
              )}
              <ActionItem icon={FileText} text="Document investigation findings" />
              <ActionItem icon={Target} text="Map to MITRE ATT&CK technique" />
            </div>
          </div>

          {/* IOC Info */}
          {(alert.source_ip || alert.destination_ip) && (
            <div className="p-6 rounded-2xl border border-slate-800/50 bg-slate-900/30">
              <h3 className="text-sm font-semibold text-white mb-3">Indicators of Compromise</h3>
              <div className="space-y-2">
                {alert.source_ip && (
                  <div className="flex items-center justify-between p-2 rounded-lg bg-slate-800/30">
                    <span className="text-xs text-slate-400">Source IP</span>
                    <span className="text-xs font-mono text-red-400">{alert.source_ip}</span>
                  </div>
                )}
                {alert.destination_ip && (
                  <div className="flex items-center justify-between p-2 rounded-lg bg-slate-800/30">
                    <span className="text-xs text-slate-400">Dest IP</span>
                    <span className="text-xs font-mono text-orange-400">{alert.destination_ip}</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function DetailItem({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div>
      <div className="text-xs text-slate-500 mb-0.5">{label}</div>
      <div className={`text-sm text-slate-300 ${mono ? "font-mono" : ""}`}>{value}</div>
    </div>
  );
}

function ActionItem({ icon: Icon, text }: { icon: any; text: string }) {
  return (
    <div className="flex items-center gap-2 p-2 rounded-lg hover:bg-slate-800/30 transition-colors cursor-pointer">
      <Icon className="w-3.5 h-3.5 text-blue-400" />
      <span className="text-xs text-slate-400">{text}</span>
    </div>
  );
}
