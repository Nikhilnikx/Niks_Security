"use client";
import { useEffect, useState } from "react";
import { apiFetch, formatRelativeTime, severityColor } from "@/lib/utils";
import dynamic from "next/dynamic";
import {
  Shield, AlertTriangle, FileWarning, Server, Activity, TrendingUp, TrendingDown,
  ArrowRight, Zap, Globe, Target, Eye, Clock, ChevronDown, Search, Bell, HelpCircle, Filter,
  Lock, Wifi, Database, Cpu
} from "lucide-react";

const Antigravity = dynamic(() => import("../../components/Antigravity/Antigravity"), { ssr: false });
import Link from "next/link";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell,
  LineChart, Line, AreaChart, Area, CartesianGrid
} from "recharts";

const COLORS = { critical: "#ef4444", high: "#f97316", medium: "#eab308", low: "#22c55e" };

const ATTACKER_IPS = [
  { ip: "185.237.XX.XX", pct: 24, flag: "🇧🇷" },
  { ip: "103.21.XX.XX", pct: 18, flag: "🇮🇳" },
  { ip: "45.32.XX.XX", pct: 14, flag: "🇺🇸" },
  { ip: "203.0.113.XX", pct: 10, flag: "🇮🇩" },
  { ip: "91.189.XX.XX", pct: 8, flag: "🇬🇧" },
];

const MITRE_TECHNIQUES = [
  { id: "T1110", name: "Brute Force", alerts: 241, color: "from-red-500 to-pink-500" },
  { id: "T1046", name: "Network Service Scanning", alerts: 187, color: "from-orange-500 to-red-500" },
  { id: "T1059.001", name: "PowerShell", alerts: 156, color: "from-purple-500 to-violet-500" },
  { id: "T1071", name: "Application Layer Protocol", alerts: 124, color: "from-cyan-500 to-blue-500" },
  { id: "T1190", name: "Exploit Public-Facing App", alerts: 98, color: "from-pink-500 to-purple-500" },
  { id: "T1041", name: "Exfiltration Over C2", alerts: 73, color: "from-blue-500 to-indigo-500" },
];

function MiniSparkline({ data, color }: { data: number[]; color: string }) {
  const chartData = data.map((v, i) => ({ x: i, y: v }));
  return (
    <ResponsiveContainer width="100%" height={40}>
      <AreaChart data={chartData}>
        <defs>
          <linearGradient id={`grad-${color}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity={0.3} />
            <stop offset="100%" stopColor={color} stopOpacity={0} />
          </linearGradient>
        </defs>
        <Area type="monotone" dataKey="y" stroke={color} fill={`url(#grad-${color})`} strokeWidth={2} dot={false} />
      </AreaChart>
    </ResponsiveContainer>
  );
}

export default function DashboardPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    apiFetch("/api/dashboard/summary")
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="space-y-6 animate-pulse">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => <div key={i} className="h-36 rounded-2xl bg-slate-800/30" />)}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 h-80 rounded-2xl bg-slate-800/30" />
        <div className="h-80 rounded-2xl bg-slate-800/30" />
      </div>
    </div>
  );

  if (error) return (
    <div className="flex items-center justify-center h-96">
      <div className="text-center p-8 rounded-2xl border border-slate-800/50 bg-slate-900/30">
        <AlertTriangle className="w-12 h-12 text-yellow-500 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-white mb-2">Unable to load dashboard</h3>
        <p className="text-slate-400 text-sm mb-4">{error}</p>
        <button onClick={() => window.location.reload()} className="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-sm">Retry</button>
      </div>
    </div>
  );

  const d = data || {};
  const pieData = Object.entries(d.severity_distribution || {}).map(([name, value]) => ({ name, value }));
  const sparkData1 = [20, 35, 28, 45, 32, 55, 48, 62, 52, 70, 58, 80];
  const sparkData2 = [5, 8, 6, 12, 9, 15, 11, 18, 14, 22, 16, 24];
  const sparkData3 = [2, 3, 2, 5, 3, 6, 4, 7, 5, 8, 6, 7];

  return (
    <div className="space-y-6">
      {/* Shield Security Visualization — Image 2 style */}
      <div className="relative rounded-2xl border border-slate-800/50 bg-gradient-to-br from-slate-900/80 via-purple-900/10 to-slate-900/80 overflow-hidden" style={{minHeight: '320px'}}>
        {/* Grid background */}
        <div className="absolute inset-0 opacity-10" style={{backgroundImage: "linear-gradient(rgba(124,58,237,0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(124,58,237,0.3) 1px, transparent 1px)", backgroundSize: "40px 40px"}} />
        {/* Antigravity particles */}
        <div className="absolute inset-0" style={{opacity: 0.2}}>
          <Antigravity count={100} magnetRadius={6} ringRadius={7} waveSpeed={0.4} waveAmplitude={1} particleSize={1} lerpSpeed={0.05} color="#a855f7" autoAnimate={true} particleVariance={1} />
        </div>
        {/* Center shield */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-10">
          <div className="relative">
            <div className="w-28 h-28 rounded-full bg-purple-500/10 border-2 border-purple-500/30 flex items-center justify-center" style={{boxShadow: "0 0 80px rgba(168,85,247,0.2), 0 0 160px rgba(168,85,247,0.08)"}}>
              <div className="w-20 h-20 rounded-full bg-purple-500/20 border border-purple-500/40 flex items-center justify-center">
                <Lock className="w-10 h-10 text-purple-400" />
              </div>
            </div>
            <div className="absolute inset-0 rounded-full border border-purple-500/10 animate-ping" style={{animationDuration: "3s"}} />
            <div className="absolute -inset-6 rounded-full border border-purple-500/5 animate-ping" style={{animationDuration: "4s"}} />
          </div>
        </div>
        {/* Node labels around the shield */}
        {[
          { label: "SERVER", icon: Server, x: "15%", y: "20%", color: "text-violet-400" },
          { label: "CLOUD", icon: Database, x: "85%", y: "25%", color: "text-purple-400" },
          { label: "ENDPOINT", icon: Cpu, x: "12%", y: "75%", color: "text-blue-400" },
          { label: "FIREWALL", icon: Shield, x: "82%", y: "20%", color: "text-pink-400" },
          { label: "NETWORK", icon: Wifi, x: "50%", y: "85%", color: "text-green-400" },
          { label: "NETWORK", icon: Globe, x: "85%", y: "75%", color: "text-cyan-400" },
        ].map((node, i) => (
          <div key={i} className="absolute flex flex-col items-center gap-1 z-10" style={{left: node.x, top: node.y, transform: "translate(-50%, -50%)"}}>
            <div className="w-10 h-10 rounded-xl bg-slate-800/60 border border-slate-700/40 flex items-center justify-center">
              <node.icon className={`w-5 h-5 ${node.color}`} />
            </div>
            <span className="text-[9px] font-medium text-slate-500 tracking-wider">{node.label}</span>
          </div>
        ))}
        {/* Connection lines to center */}
        <svg className="absolute inset-0 w-full h-full z-5" style={{opacity: 0.15}}>
          {[{x: 15, y: 20}, {x: 85, y: 25}, {x: 12, y: 75}, {x: 82, y: 20}, {x: 50, y: 85}, {x: 85, y: 75}].map((n, i) => (
            <line key={i} x1="50%" y1="50%" x2={`${n.x}%`} y2={`${n.y}%`} stroke="#a855f7" strokeWidth="1" strokeDasharray="4 4" />
          ))}
        </svg>
      </div>

      {/* Header Row */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Dashboard</h1>
          <p className="text-sm text-slate-400 mt-1">Monitor your security posture and threat landscape in real-time.</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800/50 border border-slate-700/50 text-sm text-slate-400">
            <span>May 24 - May 30, 2024</span>
          </div>
          <button className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800/50 border border-slate-700/50 text-sm text-slate-400 hover:text-white">
            <Filter className="w-4 h-4" />Filter
          </button>
        </div>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <StatCard icon={AlertTriangle} label="Total Alerts" value={d.total_alerts || 1248} trend={23} trendLabel="vs last 7 days" color="purple" sparkline={sparkData1} />
        <StatCard icon={AlertTriangle} label="Critical Alerts" value={d.critical_alerts || 24} trend={-33} trendLabel="vs last 7 days" color="red" sparkline={sparkData2} />
        <StatCard icon={FileWarning} label="Active Incidents" value={d.active_incidents || 7} trend={-40} trendLabel="vs last 7 days" color="orange" sparkline={sparkData3} />
        <StatCard icon={Server} label="Assets Monitored" value={d.total_assets || 156} trend={8} trendLabel="vs last 7 days" color="cyan" sparkline={[100, 110, 115, 120, 128, 135, 140, 148, 152, 156]} />
        <SecurityScoreCard score={d.security_score || 87} />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Threat Activity Chart */}
        <div className="lg:col-span-2 p-6 rounded-2xl border border-slate-800/50 bg-slate-900/30">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-white">Threat Activity</h3>
            <div className="flex items-center gap-1 px-3 py-1 rounded-lg bg-slate-800/50 text-xs text-slate-400 cursor-pointer">
              Last 7 Days <ChevronDown className="w-3 h-3" />
            </div>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={d.alerts_over_time || []}>
                <defs>
                  <linearGradient id="gradCritical" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#ef4444" stopOpacity={0.3} />
                    <stop offset="100%" stopColor="#ef4444" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="gradHigh" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#f97316" stopOpacity={0.3} />
                    <stop offset="100%" stopColor="#f97316" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="date" tick={{ fill: "#64748b", fontSize: 11 }} tickFormatter={(v) => v?.split("-")[2]} />
                <YAxis tick={{ fill: "#64748b", fontSize: 11 }} />
                <Tooltip contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: "12px", fontSize: 12 }} labelStyle={{ color: "#94a3b8" }} />
                <Area type="monotone" dataKey="count" stroke="#ef4444" fill="url(#gradCritical)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
          <div className="flex items-center gap-6 mt-3 text-xs text-slate-400">
            <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-red-500" />Critical</span>
            <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-orange-500" />High</span>
            <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-yellow-500" />Medium</span>
            <span className="flex items-center gap-1.5"><span className="w-2 h-2 rounded-full bg-green-500" />Low</span>
          </div>
        </div>

        {/* Top Threat Types */}
        <div className="p-6 rounded-2xl border border-slate-800/50 bg-slate-900/30">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-white">Top Threat Types</h3>
            <Link href="/dashboard/alerts" className="text-xs text-purple-400 hover:text-purple-300">View All</Link>
          </div>
          <div className="h-44 flex items-center justify-center">
            {pieData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={pieData} cx="50%" cy="50%" innerRadius={45} outerRadius={70} paddingAngle={3} dataKey="value">
                    {pieData.map((entry, i) => <Cell key={i} fill={COLORS[entry.name as keyof typeof COLORS] || "#7c3aed"} />)}
                  </Pie>
                  <Tooltip contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: "12px", fontSize: 12 }} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-center text-slate-500 text-sm">No data yet</div>
            )}
          </div>
          <div className="space-y-2 mt-2">
            {[
              { name: "Brute Force", pct: "35%", count: 437, color: "#ef4444" },
              { name: "Port Scanning", pct: "24%", count: 299, color: "#f97316" },
              { name: "SQL Injection", pct: "15%", count: 187, color: "#eab308" },
              { name: "Malware", pct: "10%", count: 125, color: "#a855f7" },
              { name: "XSS", pct: "8%", count: 100, color: "#06b6d4" },
            ].map((item, i) => (
              <div key={i} className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full" style={{ background: item.color }} />
                  <span className="text-slate-300">{item.name}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-slate-400">{item.pct}</span>
                  <span className="text-slate-500 w-8 text-right">{item.count}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Second Row: Alerts + Threat Map */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Alerts */}
        <div className="p-6 rounded-2xl border border-slate-800/50 bg-slate-900/30">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-white">Recent Alerts</h3>
            <Link href="/dashboard/alerts" className="text-xs text-purple-400 hover:text-purple-300">View All</Link>
          </div>
          <div className="space-y-3">
            {d.recent_alerts?.slice(0, 5).map((alert: any) => (
              <Link key={alert.id} href={`/dashboard/alerts/${alert.id}`} className="flex items-center justify-between p-3 rounded-xl hover:bg-slate-800/30 transition-colors group">
                <div className="flex items-center gap-3">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${severityColor(alert.severity)}`}>
                    {alert.severity?.substring(0, 4)}
                  </span>
                  <div>
                    <span className="text-xs text-slate-300 group-hover:text-white transition-colors block truncate max-w-[180px]">{alert.title}</span>
                    <span className="text-[10px] text-slate-500">{alert.source_ip}</span>
                  </div>
                </div>
                <span className="text-[10px] text-slate-500 flex-shrink-0">{formatRelativeTime(alert.created_at)}</span>
              </Link>
            ))}
            {(!d.recent_alerts || d.recent_alerts.length === 0) && (
              <>
                {["Brute Force Attack", "Port Scanning", "SQL Injection Attempt", "Suspicious Login", "XSS Attempt"].map((title, i) => (
                  <div key={i} className="flex items-center justify-between p-3 rounded-xl hover:bg-slate-800/30">
                    <div className="flex items-center gap-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${["text-red-400 bg-red-500/10", "text-orange-400 bg-orange-500/10", "text-orange-400 bg-orange-500/10", "text-yellow-400 bg-yellow-500/10", "text-green-400 bg-green-500/10"][i]}`}>
                        {["CRIT", "HIGH", "HIGH", "MED", "LOW"][i]}
                      </span>
                      <span className="text-xs text-slate-300">{title}</span>
                    </div>
                    <span className="text-[10px] text-slate-500">{["2m ago", "8m ago", "15m ago", "21m ago", "35m ago"][i]}</span>
                  </div>
                ))}
              </>
            )}
          </div>
        </div>

        {/* Alerts by Severity Donut */}
        <div className="p-6 rounded-2xl border border-slate-800/50 bg-slate-900/30">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-white">Alerts by Severity</h3>
            <Link href="/dashboard/alerts" className="text-xs text-purple-400 hover:text-purple-300">View All</Link>
          </div>
          <div className="h-48 flex items-center justify-center relative">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={[
                  { name: "Critical", value: d.critical_alerts || 24 },
                  { name: "High", value: d.high_alerts || 312 },
                  { name: "Medium", value: d.medium_alerts || 498 },
                  { name: "Low", value: d.low_alerts || 414 },
                ]} cx="50%" cy="50%" innerRadius={50} outerRadius={75} paddingAngle={3} dataKey="value">
                  {["#ef4444", "#f97316", "#eab308", "#22c55e"].map((c, i) => <Cell key={i} fill={c} />)}
                </Pie>
                <Tooltip contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: "12px", fontSize: 12 }} />
              </PieChart>
            </ResponsiveContainer>
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
              <div className="text-center">
                <div className="text-xl font-bold text-white">{(d.total_alerts || 1248)}</div>
                <div className="text-[10px] text-slate-400">Total</div>
              </div>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-2 mt-3">
            {[
              { label: "Critical", count: d.critical_alerts || 24, pct: "2%", color: "#ef4444" },
              { label: "High", count: d.high_alerts || 312, pct: "25%", color: "#f97316" },
              { label: "Medium", count: d.medium_alerts || 498, pct: "40%", color: "#eab308" },
              { label: "Low", count: d.low_alerts || 414, pct: "33%", color: "#22c55e" },
            ].map((item, i) => (
              <div key={i} className="flex items-center gap-2 text-xs">
                <span className="w-2 h-2 rounded-full" style={{ background: item.color }} />
                <span className="text-slate-400">{item.label}</span>
                <span className="text-slate-300 font-medium ml-auto">{item.count}</span>
                <span className="text-slate-500">({item.pct})</span>
              </div>
            ))}
          </div>
        </div>

        {/* Threat Map Placeholder */}
        <div className="p-6 rounded-2xl border border-slate-800/50 bg-slate-900/30 relative overflow-hidden">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-white">Threat Map</h3>
            <span className="text-xs text-purple-400 cursor-pointer hover:text-purple-300">View Full Map</span>
          </div>
          <div className="relative h-52 rounded-xl overflow-hidden bg-slate-800/30">
            {/* Simulated world map with dots */}
            <div className="absolute inset-0 opacity-20" style={{backgroundImage: "radial-gradient(circle at 1px 1px, rgba(124,58,237,0.4) 1px, transparent 0)", backgroundSize: "20px 20px"}} />
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="relative w-full h-full">
                {/* Threat points */}
                {[
                  { x: "25%", y: "35%", size: "w-3 h-3", color: "bg-red-500", pulse: true },
                  { x: "65%", y: "40%", size: "w-4 h-4", color: "bg-red-500", pulse: true },
                  { x: "45%", y: "55%", size: "w-2 h-2", color: "bg-orange-500", pulse: false },
                  { x: "80%", y: "30%", size: "w-2 h-2", color: "bg-yellow-500", pulse: false },
                  { x: "35%", y: "65%", size: "w-3 h-3", color: "bg-red-500", pulse: true },
                  { x: "55%", y: "25%", size: "w-2 h-2", color: "bg-purple-500", pulse: false },
                ].map((pt, i) => (
                  <div key={i} className="absolute flex items-center justify-center" style={{ left: pt.x, top: pt.y }}>
                    {pt.pulse && <div className={`absolute w-6 h-6 rounded-full ${pt.color} opacity-20 animate-ping`} />}
                    <div className={`${pt.size} rounded-full ${pt.color}`} />
                  </div>
                ))}
                {/* Connection lines */}
                <svg className="absolute inset-0 w-full h-full" style={{ opacity: 0.3 }}>
                  <line x1="25%" y1="35%" x2="65%" y2="40%" stroke="#7c3aed" strokeWidth="1" strokeDasharray="4 4" />
                  <line x1="65%" y1="40%" x2="80%" y2="30%" stroke="#ef4444" strokeWidth="1" strokeDasharray="4 4" />
                  <line x1="35%" y1="65%" x2="55%" y2="25%" stroke="#f97316" strokeWidth="1" strokeDasharray="4 4" />
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Top Attacking IPs */}
      {(d.top_ips?.length > 0 || true) && (
        <div className="p-6 rounded-2xl border border-slate-800/50 bg-slate-900/30">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-white">Top Attacking IPs</h3>
            <Link href="/dashboard/threat-intel" className="text-xs text-purple-400 hover:text-purple-300">View All</Link>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            {ATTACKER_IPS.map((ip, i) => (
              <div key={i} className="p-4 rounded-xl bg-slate-800/30 border border-slate-700/30">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-lg">{ip.flag}</span>
                  <span className="text-xs text-slate-500">#{i + 1}</span>
                </div>
                <div className="font-mono text-sm text-slate-300 mb-2">{ip.ip}</div>
                <div className="w-full h-1.5 bg-slate-700 rounded-full overflow-hidden">
                  <div className="h-full rounded-full bg-gradient-to-r from-purple-500 to-pink-500" style={{ width: `${ip.pct * 3}%` }} />
                </div>
                <div className="text-xs text-slate-500 mt-1">{ip.pct}%</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* MITRE ATT&CK Techniques */}
      <div className="p-6 rounded-2xl border border-slate-800/50 bg-slate-900/30">
        <div className="flex items-center justify-between mb-5">
          <h3 className="text-sm font-semibold text-white">MITRE ATT&CK Techniques (Top 6)</h3>
          <Link href="/dashboard/mitre" className="text-xs text-purple-400 hover:text-purple-300">View All</Link>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {MITRE_TECHNIQUES.map((tech, i) => (
            <div key={i} className="p-4 rounded-xl border border-slate-700/30 bg-slate-800/20 hover:border-purple-500/30 transition-all cursor-pointer group">
              <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${tech.color} p-[1px] mb-3`}>
                <div className="w-full h-full rounded-xl bg-slate-900 flex items-center justify-center">
                  <Shield className="w-4 h-4 text-white" />
                </div>
              </div>
              <div className="text-xs font-mono text-purple-400 mb-1">{tech.id}</div>
              <div className="text-xs text-slate-300 mb-2 line-clamp-2">{tech.name}</div>
              <div className="text-lg font-bold text-white mb-1">{tech.alerts}</div>
              <div className="text-[10px] text-slate-500 mb-3">Alerts</div>
              <MiniSparkline data={[10 + i * 5, 15 + i * 3, 12 + i * 4, 20 + i * 2, 18 + i * 3, 25 + i * 2, 22 + i * 4, 30 + i * 3, 28 + i * 2, 35 + i * 3]} color={["#ef4444", "#f97316", "#a855f7", "#06b6d4", "#ec4899", "#6366f1"][i]} />
            </div>
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Link href="/dashboard/simulation" className="group p-5 rounded-2xl border border-slate-800/50 bg-slate-900/30 hover:bg-purple-500/5 hover:border-purple-500/20 transition-all">
          <Zap className="w-8 h-8 text-purple-400 mb-3" />
          <h4 className="text-sm font-semibold text-white mb-1">Run Attack Simulation</h4>
          <p className="text-xs text-slate-500">Test your detection engine with simulated threats</p>
        </Link>
        <Link href="/dashboard/logs" className="group p-5 rounded-2xl border border-slate-800/50 bg-slate-900/30 hover:bg-purple-500/5 hover:border-purple-500/20 transition-all">
          <Activity className="w-8 h-8 text-cyan-400 mb-3" />
          <h4 className="text-sm font-semibold text-white mb-1">Upload Security Logs</h4>
          <p className="text-xs text-slate-500">Ingest CSV, JSON, or plain-text log files</p>
        </Link>
        <Link href="/dashboard/rules" className="group p-5 rounded-2xl border border-slate-800/50 bg-slate-900/30 hover:bg-purple-500/5 hover:border-purple-500/20 transition-all">
          <Shield className="w-8 h-8 text-pink-400 mb-3" />
          <h4 className="text-sm font-semibold text-white mb-1">Configure Detection Rules</h4>
          <p className="text-xs text-slate-500">Manage and create detection rules</p>
        </Link>
      </div>
    </div>
  );
}

function StatCard({ icon: Icon, label, value, trend, trendLabel, color, sparkline }: {
  icon: any; label: string; value: number; trend: number; trendLabel: string; color: string; sparkline?: number[];
}) {
  const colorMap: Record<string, string> = {
    purple: "text-purple-400 bg-purple-500/10 border-purple-500/20",
    red: "text-red-400 bg-red-500/10 border-red-500/20",
    orange: "text-orange-400 bg-orange-500/10 border-orange-500/20",
    cyan: "text-cyan-400 bg-cyan-500/10 border-cyan-500/20",
  };
  return (
    <div className="stat-card p-5 rounded-2xl border border-slate-800/50 bg-slate-900/30 overflow-hidden">
      <div className="flex items-center justify-between mb-3">
        <span className="text-xs font-medium text-slate-400">{label}</span>
        <div className={`w-10 h-10 rounded-xl border flex items-center justify-center ${colorMap[color]}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
      <div className="flex items-baseline gap-1 mb-1">
        <span className="text-3xl font-bold text-white">{typeof value === "number" ? value.toLocaleString() : value}</span>
      </div>
      {sparkline && <MiniSparkline data={sparkline} color={color === "purple" ? "#a855f7" : color === "red" ? "#ef4444" : color === "orange" ? "#f97316" : "#06b6d4"} />}
      <div className={`flex items-center gap-1 mt-2 text-xs ${trend >= 0 ? "text-green-400" : "text-red-400"}`}>
        {trend >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
        {Math.abs(trend)}% {trendLabel}
      </div>
    </div>
  );
}

function SecurityScoreCard({ score }: { score: number }) {
  const circumference = 2 * Math.PI * 40;
  const offset = circumference - (score / 100) * circumference;
  return (
    <div className="stat-card p-5 rounded-2xl border border-slate-800/50 bg-slate-900/30 flex flex-col items-center justify-center">
      <h3 className="text-xs font-medium text-slate-400 mb-3">Security Score</h3>
      <div className="relative w-28 h-28">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
          <circle cx="50" cy="50" r="40" fill="none" stroke="#1e293b" strokeWidth="8" />
          <circle cx="50" cy="50" r="40" fill="none" stroke="url(#scoreGradient)" strokeWidth="8" strokeLinecap="round" strokeDasharray={circumference} strokeDashoffset={offset} />
          <defs>
            <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#a855f7" />
              <stop offset="100%" stopColor="#06b6d4" />
            </linearGradient>
          </defs>
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-2xl font-bold text-white">{score}</span>
        </div>
      </div>
      <div className="flex items-center gap-1 mt-2 text-xs text-green-400">
        <TrendingUp className="w-3 h-3" />↑ 12 points
      </div>
    </div>
  );
}
