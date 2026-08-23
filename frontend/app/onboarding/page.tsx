"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/utils";
import {
  Shield, Building, Users, Target, CheckCircle, ArrowRight, ArrowLeft,
  Plus, Trash2, Loader2, Zap, Globe, Lock, Eye, AlertTriangle, Activity
} from "lucide-react";

const STEPS = [
  { id: "org", title: "Organization Setup", desc: "Configure your organization details", icon: Building },
  { id: "team", title: "Invite Team", desc: "Add your security team members", icon: Users },
  { id: "rules", title: "Detection Rules", desc: "Enable threat detection rules", icon: Target },
];

const PRESET_RULES = [
  { name: "SSH Brute Force Detection", desc: "Multiple failed login attempts", severity: "high", technique: "T1110", icon: Lock, color: "text-orange-400" },
  { name: "Port Scanning Detection", desc: "Reconnaissance port scanning activity", severity: "medium", technique: "T1046", icon: Globe, color: "text-yellow-400" },
  { name: "SQL Injection Detection", desc: "SQL injection payloads in web inputs", severity: "critical", technique: "T1190", icon: AlertTriangle, color: "text-red-400" },
  { name: "Suspicious Login Location", desc: "Authentication from unusual locations", severity: "medium", technique: "T1078", icon: Eye, color: "text-purple-400" },
  { name: "Malware Indicator Detection", desc: "Known malware signatures and hashes", severity: "critical", technique: "T1059", icon: Shield, color: "text-red-400" },
  { name: "XSS Attack Detection", desc: "Cross-site scripting payloads", severity: "high", technique: "T1189", icon: Activity, color: "text-orange-400" },
];

const SEVERITY_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  critical: { bg: "bg-red-500/10", text: "text-red-400", border: "border-red-500/20" },
  high: { bg: "bg-orange-500/10", text: "text-orange-400", border: "border-orange-500/20" },
  medium: { bg: "bg-yellow-500/10", text: "text-yellow-400", border: "border-yellow-500/20" },
  low: { bg: "bg-green-500/10", text: "text-green-400", border: "border-green-500/20" },
};

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // Step 1: Org
  const [orgName, setOrgName] = useState("");
  const [orgDesc, setOrgDesc] = useState("");

  // Step 2: Team
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteRole, setInviteRole] = useState("analyst");
  const [invites, setInvites] = useState<any[]>([]);

  // Step 3: Rules
  const [selectedRules, setSelectedRules] = useState<Set<number>>(new Set([0, 1, 2, 3, 4, 5]));

  useEffect(() => {
    const token = localStorage.getItem("token");
    const userData = localStorage.getItem("user");
    if (!token) {
      router.push("/login");
      return;
    }
    if (userData) {
      try {
        const u = JSON.parse(userData);
        setUser(u);
        setOrgName(u.organization_name || "");
      } catch {}
    }

    // Check if onboarding already done
    apiFetch("/api/onboarding/status")
      .then((data) => {
        if (!data.onboarding_needed) {
          router.push("/dashboard");
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [router]);

  const toggleRule = (idx: number) => {
    setSelectedRules((prev) => {
      const next = new Set(prev);
      if (next.has(idx)) next.delete(idx);
      else next.add(idx);
      return next;
    });
  };

  const saveOrg = async () => {
    setSaving(true);
    try {
      await apiFetch("/api/onboarding/org-setup", {
        method: "PUT",
        body: JSON.stringify({ name: orgName, description: orgDesc }),
      });
      // Update local storage
      const userData = JSON.parse(localStorage.getItem("user") || "{}");
      userData.organization_name = orgName;
      localStorage.setItem("user", JSON.stringify(userData));
      setStep(1);
    } catch (e: any) {
      alert(e.message);
    } finally {
      setSaving(false);
    }
  };

  const sendInvite = async () => {
    if (!inviteEmail.trim()) return;
    try {
      const data = await apiFetch("/api/onboarding/invite", {
        method: "POST",
        body: JSON.stringify({ email: inviteEmail, role: inviteRole }),
      });
      setInvites((prev) => [...prev, { email: inviteEmail, role: inviteRole, ...data.user }]);
      setInviteEmail("");
    } catch (e: any) {
      alert(e.message);
    }
  };

  const setupRules = async () => {
    setSaving(true);
    try {
      await apiFetch("/api/onboarding/quick-rules", {
        method: "POST",
        body: JSON.stringify({ rules: Array.from(selectedRules) }),
      });
      await apiFetch("/api/onboarding/complete", { method: "POST" });
      router.push("/dashboard");
    } catch (e: any) {
      alert(e.message);
    } finally {
      setSaving(false);
    }
  };

  const skipTeam = () => setStep(2);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#080b16]">
        <Loader2 className="w-8 h-8 text-purple-400 animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#080b16] flex items-center justify-center px-4 py-12 relative overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 opacity-[0.03]" style={{backgroundImage: "radial-gradient(circle at 1px 1px, rgba(168,85,247,0.5) 1px, transparent 0)", backgroundSize: "40px 40px"}} />
      <div className="absolute top-20 left-1/4 w-96 h-96 bg-purple-600/8 rounded-full blur-[150px]" />
      <div className="absolute bottom-20 right-1/4 w-96 h-96 bg-violet-600/8 rounded-full blur-[150px]" />

      <div className="w-full max-w-2xl relative z-10">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2.5 mb-4">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-violet-600 flex items-center justify-center shadow-lg shadow-purple-500/20">
              <Shield className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold text-white">NIKS <span className="text-purple-400">SECURITY</span></span>
          </div>
          <h1 className="text-2xl font-bold text-white mb-2">Welcome to Niks Security</h1>
          <p className="text-slate-400 text-sm">Let&apos;s get your security platform configured in 3 quick steps</p>
        </div>

        {/* Step indicator */}
        <div className="flex items-center justify-center gap-2 mb-8">
          {STEPS.map((s, i) => (
            <div key={i} className="flex items-center gap-2">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all ${
                i < step ? "bg-purple-600 text-white" :
                i === step ? "bg-purple-600/20 text-purple-400 border border-purple-500/30" :
                "bg-slate-800/50 text-slate-500 border border-slate-700/30"
              }`}>
                {i < step ? <CheckCircle className="w-4 h-4" /> : i + 1}
              </div>
              {i < STEPS.length - 1 && <div className={`w-12 h-0.5 ${i < step ? "bg-purple-600" : "bg-slate-800"}`} />}
            </div>
          ))}
        </div>

        {/* Step content */}
        <div className="p-8 rounded-2xl border border-slate-800/50 bg-slate-900/30 backdrop-blur-xl">
          {step === 0 && (
            <div className="space-y-6">
              <div>
                <h2 className="text-lg font-semibold text-white mb-1 flex items-center gap-2">
                  <Building className="w-5 h-5 text-purple-400" />Organization Setup
                </h2>
                <p className="text-sm text-slate-400">Tell us about your organization to customize your experience</p>
              </div>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-slate-300 mb-1.5">Organization Name *</label>
                  <input value={orgName} onChange={(e) => setOrgName(e.target.value)} className="w-full px-4 py-3 rounded-xl bg-slate-800/50 border border-slate-700/50 text-white text-sm focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500 transition-colors" placeholder="Acme Security Team" />
                </div>
                <div>
                  <label className="block text-sm text-slate-300 mb-1.5">Description (optional)</label>
                  <textarea value={orgDesc} onChange={(e) => setOrgDesc(e.target.value)} rows={3} className="w-full px-4 py-3 rounded-xl bg-slate-800/50 border border-slate-700/50 text-white text-sm focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500 transition-colors resize-none" placeholder="What does your team protect?" />
                </div>
              </div>
              <button onClick={saveOrg} disabled={!orgName.trim() || saving} className="w-full py-3 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2">
                {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <>Continue <ArrowRight className="w-4 h-4" /></>}
              </button>
            </div>
          )}

          {step === 1 && (
            <div className="space-y-6">
              <div>
                <h2 className="text-lg font-semibold text-white mb-1 flex items-center gap-2">
                  <Users className="w-5 h-5 text-purple-400" />Invite Team Members
                </h2>
                <p className="text-sm text-slate-400">Add analysts and viewers to your security team</p>
              </div>
              <div className="flex gap-2">
                <input value={inviteEmail} onChange={(e) => setInviteEmail(e.target.value)} onKeyDown={(e) => e.key === "Enter" && sendInvite()} className="flex-1 px-4 py-3 rounded-xl bg-slate-800/50 border border-slate-700/50 text-white text-sm focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500 transition-colors" placeholder="colleague@company.com" />
                <select value={inviteRole} onChange={(e) => setInviteRole(e.target.value)} className="px-3 py-3 rounded-xl bg-slate-800/50 border border-slate-700/50 text-white text-sm focus:outline-none focus:border-purple-500">
                  <option value="analyst">Analyst</option>
                  <option value="viewer">Viewer</option>
                  <option value="admin">Admin</option>
                </select>
                <button onClick={sendInvite} className="px-4 py-3 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-sm font-medium flex items-center gap-1.5">
                  <Plus className="w-4 h-4" />Invite
                </button>
              </div>
              {invites.length > 0 && (
                <div className="space-y-2">
                  {invites.map((inv, i) => (
                    <div key={i} className="flex items-center justify-between p-3 rounded-xl bg-slate-800/30 border border-slate-700/30">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-purple-500/10 flex items-center justify-center text-xs font-bold text-purple-400">
                          {inv.email[0].toUpperCase()}
                        </div>
                        <div>
                          <div className="text-sm text-white">{inv.email}</div>
                          <div className="text-[10px] text-slate-500 capitalize">{inv.role}</div>
                        </div>
                      </div>
                      <CheckCircle className="w-4 h-4 text-green-400" />
                    </div>
                  ))}
                </div>
              )}
              <div className="flex gap-3">
                <button onClick={skipTeam} className="flex-1 py-3 rounded-xl border border-slate-700/50 text-slate-300 hover:text-white hover:bg-slate-800/50 font-medium transition-all text-sm">
                  Skip for now
                </button>
                <button onClick={() => setStep(2)} className="flex-1 py-3 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-medium transition-all flex items-center justify-center gap-2">
                  Continue <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-6">
              <div>
                <h2 className="text-lg font-semibold text-white mb-1 flex items-center gap-2">
                  <Zap className="w-5 h-5 text-purple-400" />Detection Rules
                </h2>
                <p className="text-sm text-slate-400">Enable pre-built rules to start detecting threats immediately</p>
              </div>
              <div className="space-y-2">
                {PRESET_RULES.map((rule, i) => {
                  const selected = selectedRules.has(i);
                  const sev = SEVERITY_COLORS[rule.severity] || SEVERITY_COLORS.medium;
                  return (
                    <button
                      key={i}
                      onClick={() => toggleRule(i)}
                      className={`w-full flex items-center gap-4 p-4 rounded-xl border transition-all text-left ${
                        selected ? "border-purple-500/30 bg-purple-500/5" : "border-slate-700/30 bg-slate-800/20 hover:bg-slate-800/30"
                      }`}
                    >
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${selected ? "bg-purple-500/20" : "bg-slate-800/50"}`}>
                        <rule.icon className={`w-4 h-4 ${selected ? "text-purple-400" : "text-slate-500"}`} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium text-white">{rule.name}</div>
                        <div className="text-[11px] text-slate-500">{rule.desc}</div>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`text-[10px] px-2 py-0.5 rounded-full ${sev.bg} ${sev.text} border ${sev.border} font-medium`}>
                          {rule.severity.toUpperCase()}
                        </span>
                        <span className="text-[10px] text-slate-500 font-mono">{rule.technique}</span>
                        <div className={`w-5 h-5 rounded-md border flex items-center justify-center transition-all ${
                          selected ? "bg-purple-600 border-purple-500" : "border-slate-600"
                        }`}>
                          {selected && <CheckCircle className="w-3 h-3 text-white" />}
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
              <div className="flex gap-3">
                <button onClick={() => setStep(1)} className="px-4 py-3 rounded-xl border border-slate-700/50 text-slate-300 hover:text-white hover:bg-slate-800/50 transition-all">
                  <ArrowLeft className="w-4 h-4" />
                </button>
                <button onClick={setupRules} disabled={saving || selectedRules.size === 0} className="flex-1 py-3 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2">
                  {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : (
                    <>
                      <Zap className="w-4 h-4" />
                      Enable {selectedRules.size} Rules & Launch Dashboard
                    </>
                  )}
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Step label */}
        <div className="text-center mt-4 text-xs text-slate-500">
          Step {step + 1} of {STEPS.length}: {STEPS[step].title}
        </div>
      </div>
    </div>
  );
}
