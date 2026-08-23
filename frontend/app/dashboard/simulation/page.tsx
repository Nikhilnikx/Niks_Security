"use client";
import { useState } from "react";
import { apiFetch } from "@/lib/utils";
import { Target, Zap, Shield, AlertTriangle, Play, CheckCircle, Loader2 } from "lucide-react";
import Link from "next/link";

const ATTACK_TYPES = [
  { id: "brute_force", name: "Brute Force Attack", desc: "Simulates 15 failed SSH login attempts from a single IP within 5 minutes.", icon: Shield, color: "from-red-500 to-orange-400", severity: "HIGH" },
  { id: "port_scan", name: "Port Scanning", desc: "Simulates connection attempts to 20+ ports on a target server.", icon: Target, color: "from-orange-500 to-yellow-400", severity: "MEDIUM" },
  { id: "sql_injection", name: "SQL Injection", desc: "Simulates SQL injection payloads in web request parameters.", icon: AlertTriangle, color: "from-purple-500 to-pink-400", severity: "CRITICAL" },
  { id: "suspicious_login", name: "Suspicious Login", desc: "Simulates a login from an unusual geographic location at an odd hour.", icon: Shield, color: "from-cyan-500 to-blue-400", severity: "HIGH" },
  { id: "xss_attack", name: "Cross-Site Scripting", desc: "Simulates XSS payloads injected into web application inputs.", icon: AlertTriangle, color: "from-pink-500 to-red-400", severity: "MEDIUM" },
  { id: "command_injection", name: "Command Injection", desc: "Simulates OS command injection attempts through web parameters.", icon: Zap, color: "from-red-500 to-red-400", severity: "CRITICAL" },
];

export default function SimulationPage() {
  const [running, setRunning] = useState<string | null>(null);
  const [results, setResults] = useState<Record<string, any>>({});

  const runSimulation = async (attackId: string) => {
    setRunning(attackId);
    try {
      const data = await apiFetch("/api/simulation/run", {
        method: "POST",
        body: JSON.stringify({ attack_type: attackId }),
      });
      setResults((prev) => ({ ...prev, [attackId]: data }));
    } catch (e: any) {
      setResults((prev) => ({ ...prev, [attackId]: { error: e.message } }));
    } finally {
      setRunning(null);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Attack Simulation</h1>
        <p className="text-sm text-slate-400 mt-1">Test your detection engine with controlled simulations</p>
        <div className="mt-2 px-3 py-2 rounded-lg bg-yellow-500/10 border border-yellow-500/20 text-yellow-400 text-xs">
          ⚠️ These are safe, simulated attacks for testing purposes only. No real attacks are performed.
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {ATTACK_TYPES.map((attack) => {
          const Icon = attack.icon;
          const result = results[attack.id];
          const isRunning = running === attack.id;

          return (
            <div key={attack.id} className={`p-6 rounded-2xl border transition-all ${result?.error ? "border-red-500/20" : result ? "border-green-500/20" : "border-slate-800/50"} bg-slate-900/30`}>
              <div className="flex items-start gap-3 mb-4">
                <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${attack.color} p-[1px]`}>
                  <div className="w-full h-full rounded-xl bg-slate-900 flex items-center justify-center">
                    <Icon className="w-5 h-5 text-white" />
                  </div>
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-white">{attack.name}</h3>
                  <span className={`text-xs px-1.5 py-0.5 rounded border ${attack.severity === "CRITICAL" ? "bg-red-500/10 text-red-400 border-red-500/20" : attack.severity === "HIGH" ? "bg-orange-500/10 text-orange-400 border-orange-500/20" : "bg-yellow-500/10 text-yellow-400 border-yellow-500/20"}`}>
                    {attack.severity}
                  </span>
                </div>
              </div>
              <p className="text-xs text-slate-400 mb-4">{attack.desc}</p>

              {result && !result.error ? (
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-green-400 text-xs">
                    <CheckCircle className="w-3.5 h-3.5" />
                    <span>Simulation complete</span>
                  </div>
                  <div className="text-xs text-slate-400 space-y-1">
                    <div>Events generated: <span className="text-white font-mono">{result.events_created || 0}</span></div>
                    <div>Alerts generated: <span className="text-white font-mono">{result.alerts_generated || 0}</span></div>
                  </div>
                  <Link href="/dashboard/alerts" className="block text-center text-xs text-blue-400 hover:text-blue-300 mt-2">
                    View Alerts →
                  </Link>
                </div>
              ) : result?.error ? (
                <div className="text-xs text-red-400">{result.error}</div>
              ) : (
                <button
                  onClick={() => runSimulation(attack.id)}
                  disabled={!!running}
                  className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-blue-600/10 border border-blue-500/20 text-blue-400 text-sm font-medium hover:bg-blue-600/20 transition-colors disabled:opacity-50"
                >
                  {isRunning ? (
                    <><Loader2 className="w-4 h-4 animate-spin" /> Running...</>
                  ) : (
                    <><Play className="w-4 h-4" /> Run Simulation</>
                  )}
                </button>
              )}
            </div>
          );
        })}
      </div>

      {/* Pipeline visualization */}
      <div className="p-6 rounded-2xl border border-slate-800/50 bg-slate-900/30">
        <h3 className="text-sm font-semibold text-white mb-4">Detection Pipeline</h3>
        <div className="flex items-center justify-between overflow-x-auto gap-2">
          {["COLLECT", "NORMALIZE", "DETECT", "CORRELATE", "ENRICH", "ALERT", "INVESTIGATE", "RESPOND", "REPORT"].map((step, i) => (
            <div key={step} className="flex items-center">
              <div className="px-3 py-2 rounded-lg bg-blue-500/10 border border-blue-500/20 text-xs text-blue-400 font-medium whitespace-nowrap">
                {step}
              </div>
              {i < 8 && <div className="w-4 h-0.5 bg-slate-700 mx-1" />}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
