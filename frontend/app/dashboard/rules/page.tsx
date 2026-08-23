"use client";
import { useEffect, useState } from "react";
import { apiFetch, severityColor } from "@/lib/utils";
import { Target, Plus, Power, PowerOff, Edit3, Trash2, X, Eye } from "lucide-react";

export default function RulesPage() {
  const [rules, setRules] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showAdd, setShowAdd] = useState(false);
  const [editing, setEditing] = useState<any>(null);
  const [form, setForm] = useState({
    name: "", description: "", severity: "medium", threat_type: "",
    condition_text: "", time_window_seconds: 300, threshold: 10,
    mitre_technique: "", mitre_tactic: "", enabled: true
  });

  const fetchRules = async () => {
    try {
      const data = await apiFetch("/api/rules");
      setRules(data.rules || data || []);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchRules(); }, []);

  const openAdd = () => {
    setForm({ name: "", description: "", severity: "medium", threat_type: "", condition_text: "", time_window_seconds: 300, threshold: 10, mitre_technique: "", mitre_tactic: "", enabled: true });
    setEditing(null);
    setShowAdd(true);
  };

  const openEdit = (rule: any) => {
    setForm({
      name: rule.name || "", description: rule.description || "", severity: rule.severity || "medium",
      threat_type: rule.threat_type || "", condition_text: rule.conditions || rule.condition_text || "",
      time_window_seconds: rule.time_window_seconds || 300, threshold: rule.threshold || 10,
      mitre_technique: rule.mitre_technique || "", mitre_tactic: rule.mitre_tactic || "", enabled: rule.enabled !== false
    });
    setEditing(rule);
    setShowAdd(true);
  };

  const saveRule = async () => {
    try {
      if (editing) {
        await apiFetch(`/api/rules/${editing.id}`, { method: "PUT", body: JSON.stringify(form) });
      } else {
        await apiFetch("/api/rules", { method: "POST", body: JSON.stringify(form) });
      }
      setShowAdd(false);
      fetchRules();
    } catch (e: any) {
      setError(e.message);
    }
  };

  const toggleRule = async (id: number, enabled: boolean) => {
    try {
      await apiFetch(`/api/rules/${id}/toggle`, { method: "PATCH", body: JSON.stringify({ enabled: !enabled }) });
      fetchRules();
    } catch (e: any) {
      setError(e.message);
    }
  };

  const deleteRule = async (id: number) => {
    if (!confirm("Delete this detection rule?")) return;
    try {
      await apiFetch(`/api/rules/${id}`, { method: "DELETE" });
      fetchRules();
    } catch (e: any) {
      setError(e.message);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Detection Rules</h1>
          <p className="text-sm text-slate-400 mt-1">{rules.length} rules configured</p>
        </div>
        <button onClick={openAdd} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-sm">
          <Plus className="w-4 h-4" />New Rule
        </button>
      </div>

      {error && <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm">{error}</div>}

      {/* Add/Edit Modal */}
      {showAdd && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 overflow-y-auto">
          <div className="w-full max-w-lg p-6 rounded-2xl border border-slate-800/50 bg-[#0b1120] my-8">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">{editing ? "Edit Rule" : "New Rule"}</h3>
              <button onClick={() => setShowAdd(false)} className="text-slate-400 hover:text-white"><X className="w-5 h-5" /></button>
            </div>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-slate-300 mb-1">Name</label>
                <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="w-full px-4 py-2.5 rounded-xl bg-slate-800/50 border border-slate-700/50 text-white text-sm focus:outline-none focus:border-blue-500" placeholder="SSH Brute Force" />
              </div>
              <div>
                <label className="block text-sm text-slate-300 mb-1">Description</label>
                <input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} className="w-full px-4 py-2.5 rounded-xl bg-slate-800/50 border border-slate-700/50 text-white text-sm focus:outline-none focus:border-blue-500" placeholder="Detects SSH brute force attempts" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-slate-300 mb-1">Severity</label>
                  <select value={form.severity} onChange={(e) => setForm({ ...form, severity: e.target.value })} className="w-full px-4 py-2.5 rounded-xl bg-slate-800/50 border border-slate-700/50 text-white text-sm focus:outline-none focus:border-blue-500">
                    <option value="critical">Critical</option>
                    <option value="high">High</option>
                    <option value="medium">Medium</option>
                    <option value="low">Low</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm text-slate-300 mb-1">Threat Type</label>
                  <input value={form.threat_type} onChange={(e) => setForm({ ...form, threat_type: e.target.value })} className="w-full px-4 py-2.5 rounded-xl bg-slate-800/50 border border-slate-700/50 text-white text-sm focus:outline-none focus:border-blue-500" placeholder="brute_force" />
                </div>
              </div>
              <div>
                <label className="block text-sm text-slate-300 mb-1">Condition</label>
                <textarea value={form.condition_text} onChange={(e) => setForm({ ...form, condition_text: e.target.value })} rows={3} className="w-full px-4 py-2.5 rounded-xl bg-slate-800/50 border border-slate-700/50 text-white text-sm font-mono focus:outline-none focus:border-blue-500" placeholder="failed_login_count > 10 FROM same_ip WITHIN 5m" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-slate-300 mb-1">Time Window (sec)</label>
                  <input type="number" value={form.time_window_seconds} onChange={(e) => setForm({ ...form, time_window_seconds: Number(e.target.value) })} className="w-full px-4 py-2.5 rounded-xl bg-slate-800/50 border border-slate-700/50 text-white text-sm focus:outline-none focus:border-blue-500" />
                </div>
                <div>
                  <label className="block text-sm text-slate-300 mb-1">Threshold</label>
                  <input type="number" value={form.threshold} onChange={(e) => setForm({ ...form, threshold: Number(e.target.value) })} className="w-full px-4 py-2.5 rounded-xl bg-slate-800/50 border border-slate-700/50 text-white text-sm focus:outline-none focus:border-blue-500" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-slate-300 mb-1">MITRE Technique</label>
                  <input value={form.mitre_technique} onChange={(e) => setForm({ ...form, mitre_technique: e.target.value })} className="w-full px-4 py-2.5 rounded-xl bg-slate-800/50 border border-slate-700/50 text-white text-sm font-mono focus:outline-none focus:border-blue-500" placeholder="T1110" />
                </div>
                <div>
                  <label className="block text-sm text-slate-300 mb-1">MITRE Tactic</label>
                  <input value={form.mitre_tactic} onChange={(e) => setForm({ ...form, mitre_tactic: e.target.value })} className="w-full px-4 py-2.5 rounded-xl bg-slate-800/50 border border-slate-700/50 text-white text-sm focus:outline-none focus:border-blue-500" placeholder="credential-access" />
                </div>
              </div>
              <div className="flex items-center gap-2">
                <input type="checkbox" checked={form.enabled} onChange={(e) => setForm({ ...form, enabled: e.target.checked })} className="rounded" />
                <span className="text-sm text-slate-300">Enabled</span>
              </div>
              <button onClick={saveRule} className="w-full py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium">
                {editing ? "Save Changes" : "Create Rule"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Rules List */}
      {loading ? (
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => <div key={i} className="h-24 rounded-2xl bg-slate-800/30 animate-pulse" />)}
        </div>
      ) : rules.length === 0 ? (
        <div className="text-center py-16 rounded-2xl border border-slate-800/50 bg-slate-900/30">
          <Target className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <p className="text-slate-400">No detection rules configured.</p>
          <p className="text-slate-500 text-sm mt-1">Create your first rule to start detecting threats.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {rules.map((rule) => (
            <div key={rule.id} className={`p-5 rounded-2xl border transition-all ${rule.enabled ? "border-slate-800/50 bg-slate-900/30" : "border-slate-800/30 bg-slate-900/20 opacity-60"}`}>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-sm font-semibold text-white">{rule.name}</h3>
                    <span className={`px-2 py-0.5 rounded text-xs font-medium border ${severityColor(rule.severity)}`}>
                      {rule.severity?.toUpperCase()}
                    </span>
                    {rule.mitre_technique && (
                      <span className="px-2 py-0.5 rounded text-xs bg-purple-500/10 text-purple-400 border border-purple-500/20">
                        {rule.mitre_technique}
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-400 mb-2">{rule.description}</p>
                  {(rule.conditions || rule.condition_text) && (
                    <code className="text-xs text-blue-400 font-mono bg-blue-500/5 px-2 py-1 rounded">{rule.conditions || rule.condition_text}</code>
                  )}
                  <div className="flex items-center gap-4 mt-2 text-xs text-slate-500">
                    <span>Threshold: {rule.threshold}</span>
                    <span>Window: {rule.time_window_seconds}s</span>
                    {rule.mitre_tactic && <span>Tactic: {rule.mitre_tactic}</span>}
                  </div>
                </div>
                <div className="flex items-center gap-2 ml-4">
                  <button onClick={() => toggleRule(rule.id, rule.enabled)} className={`p-2 rounded-lg transition-colors ${rule.enabled ? "text-green-400 hover:bg-green-500/10" : "text-slate-500 hover:bg-slate-800/50"}`} title={rule.enabled ? "Disable" : "Enable"}>
                    {rule.enabled ? <Power className="w-4 h-4" /> : <PowerOff className="w-4 h-4" />}
                  </button>
                  <button onClick={() => openEdit(rule)} className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/50" title="Edit">
                    <Edit3 className="w-4 h-4" />
                  </button>
                  <button onClick={() => deleteRule(rule.id)} className="p-2 rounded-lg text-slate-400 hover:text-red-400 hover:bg-red-500/10" title="Delete">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
