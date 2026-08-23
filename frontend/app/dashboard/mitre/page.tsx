"use client";
import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/utils";
import { Globe, ExternalLink, AlertTriangle } from "lucide-react";
import Link from "next/link";

const TACTICS = [
  { id: "TA0001", name: "Initial Access", color: "from-blue-500 to-cyan-400" },
  { id: "TA0002", name: "Execution", color: "from-purple-500 to-blue-400" },
  { id: "TA0003", name: "Persistence", color: "from-orange-500 to-red-400" },
  { id: "TA0004", name: "Privilege Escalation", color: "from-red-500 to-pink-400" },
  { id: "TA0005", name: "Defense Evasion", color: "from-yellow-500 to-orange-400" },
  { id: "TA0006", name: "Credential Access", color: "from-cyan-500 to-blue-400" },
  { id: "TA0007", name: "Discovery", color: "from-green-500 to-emerald-400" },
  { id: "TA0008", name: "Lateral Movement", color: "from-pink-500 to-purple-400" },
  { id: "TA0009", name: "Collection", color: "from-indigo-500 to-blue-400" },
  { id: "TA0011", name: "Command and Control", color: "from-violet-500 to-purple-400" },
  { id: "TA0010", name: "Exfiltration", color: "from-rose-500 to-red-400" },
  { id: "TA0040", name: "Impact", color: "from-red-600 to-red-400" },
];

export default function MitrePage() {
  const [mapping, setMapping] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedTactic, setSelectedTactic] = useState<string | null>(null);

  useEffect(() => {
    apiFetch("/api/mitre/mapping")
      .then(setMapping)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="space-y-6 animate-pulse">
      <div className="h-8 w-48 bg-slate-800/50 rounded" />
      <div className="grid grid-cols-4 gap-4">
        {[...Array(12)].map((_, i) => <div key={i} className="h-24 rounded-2xl bg-slate-800/30" />)}
      </div>
    </div>
  );

  const techniques = mapping?.techniques || [];
  const stats = mapping?.stats || {};

  const getTechniquesForTactic = (tacticId: string) =>
    techniques.filter((t: any) => t.tactic_id === tacticId || t.tactic?.includes(tacticId));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">MITRE ATT&CK</h1>
        <p className="text-sm text-slate-400 mt-1">Map detections to attack techniques</p>
      </div>

      {error && <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">{error}</div>}

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-2xl border border-slate-800/50 bg-slate-900/30">
          <div className="text-2xl font-bold text-white">{stats.total_techniques || techniques.length}</div>
          <div className="text-xs text-slate-400">Mapped Techniques</div>
        </div>
        <div className="p-4 rounded-2xl border border-slate-800/50 bg-slate-900/30">
          <div className="text-2xl font-bold text-blue-400">{stats.total_alerts || 0}</div>
          <div className="text-xs text-slate-400">Related Alerts</div>
        </div>
        <div className="p-4 rounded-2xl border border-slate-800/50 bg-slate-900/30">
          <div className="text-2xl font-bold text-orange-400">{stats.total_incidents || 0}</div>
          <div className="text-xs text-slate-400">Related Incidents</div>
        </div>
        <div className="p-4 rounded-2xl border border-slate-800/50 bg-slate-900/30">
          <div className="text-2xl font-bold text-red-400">{stats.total_detections || 0}</div>
          <div className="text-xs text-slate-400">Total Detections</div>
        </div>
      </div>

      {/* Attack Matrix */}
      <div className="p-6 rounded-2xl border border-slate-800/50 bg-slate-900/30">
        <h3 className="text-sm font-semibold text-white mb-4">Attack Technique Matrix</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
          {TACTICS.map((tactic) => {
            const tacticTechniques = getTechniquesForTactic(tactic.id);
            const isSelected = selectedTactic === tactic.id;
            return (
              <div key={tactic.id} onClick={() => setSelectedTactic(isSelected ? null : tactic.id)} className={`rounded-xl border p-4 cursor-pointer transition-all ${isSelected ? "border-blue-500/30 bg-blue-500/5" : "border-slate-800/50 bg-slate-800/20 hover:bg-slate-800/30"}`}>
                <div className={`text-xs font-bold text-transparent bg-clip-text bg-gradient-to-r ${tactic.color} mb-2`}>{tactic.id}</div>
                <div className="text-sm font-medium text-white mb-1">{tactic.name}</div>
                <div className="text-xs text-slate-500">{tacticTechniques.length} techniques</div>
                {tacticTechniques.length > 0 && (
                  <div className="w-full h-1 bg-slate-700 rounded-full mt-2 overflow-hidden">
                    <div className={`h-full rounded-full bg-gradient-to-r ${tactic.color}`} style={{ width: `${Math.min(100, tacticTechniques.length * 20)}%` }} />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Techniques List */}
      <div className="space-y-3">
        {(selectedTactic ? techniques.filter((t: any) => t.tactic_id === selectedTactic || t.tactic?.includes(selectedTactic)) : techniques).map((technique: any, i: number) => (
          <div key={technique.id || i} className="p-5 rounded-2xl border border-slate-800/50 bg-slate-900/30">
            <div className="flex items-start justify-between">
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <span className="text-sm font-mono font-bold text-blue-400">{technique.technique_id || technique.id}</span>
                  <span className="text-sm font-semibold text-white">{technique.name}</span>
                </div>
                <div className="flex items-center gap-3 mb-2">
                  <span className="text-xs text-slate-500">{technique.tactic}</span>
                  {technique.detection_count > 0 && (
                    <span className="px-2 py-0.5 rounded text-xs bg-blue-500/10 text-blue-400 border border-blue-500/20">
                      {technique.detection_count} detections
                    </span>
                  )}
                </div>
                {technique.description && (
                  <p className="text-xs text-slate-400 max-w-2xl">{technique.description}</p>
                )}
              </div>
            </div>
          </div>
        ))}
        {techniques.length === 0 && (
          <div className="text-center py-16 rounded-2xl border border-slate-800/50 bg-slate-900/30">
            <Globe className="w-12 h-12 text-slate-600 mx-auto mb-3" />
            <p className="text-slate-400">No MITRE techniques mapped yet.</p>
            <p className="text-slate-500 text-sm mt-1">Detection rules will automatically map to ATT&CK techniques.</p>
          </div>
        )}
      </div>
    </div>
  );
}
