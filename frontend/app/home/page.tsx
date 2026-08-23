"use client";
import Link from "next/link";
import dynamic from "next/dynamic";
import { useEffect, useState } from "react";
import {
  Shield, Zap, Eye, Lock, Server, Globe, Activity, AlertTriangle, Search, FileText,
  Users, ArrowRight, ChevronRight, Database, Wifi, Cpu, Target, CheckCircle,
  BarChart3, Fingerprint, Network, HardDrive
} from "lucide-react";

const Antigravity = dynamic(() => import("../../components/Antigravity/Antigravity"), { ssr: false });

const features = [
  {
    icon: Shield,
    title: "SECURITY THAT ADAPTS TO EVERY THREAT",
    desc: "Advanced threat detection using machine learning and behavioral analysis to identify and stop attacks before they happen.",
    bullets: ["Behavioral Analysis", "Anomaly Detection", "Threat Intelligence", "Automated Response"],
    gradient: "from-purple-600/20 to-violet-600/20",
    borderColor: "border-purple-500/20",
    iconBg: "bg-purple-500/10",
    iconColor: "text-purple-400",
    visual: "shield",
  },
  {
    icon: Eye,
    title: "COMPLETE VISIBILITY. TOTAL CONTROL.",
    desc: "Monitor, analyze, and respond to threats across your entire infrastructure from a single, unified platform.",
    bullets: ["Unified Dashboard", "Centralized Logging", "Real-time Alerts", "Custom Reports"],
    gradient: "from-blue-600/20 to-cyan-600/20",
    borderColor: "border-blue-500/20",
    iconBg: "bg-blue-500/10",
    iconColor: "text-blue-400",
    visual: "dashboard",
  },
  {
    icon: Target,
    title: "RESPOND FASTER. REDUCE RISK.",
    desc: "Automated response and intelligent workflows help your team act faster and minimize the impact of threats.",
    bullets: ["Automated Workflows", "Incident Management", "Threat Containment", "Evidence Collection"],
    gradient: "from-pink-600/20 to-rose-600/20",
    borderColor: "border-pink-500/20",
    iconBg: "bg-pink-500/10",
    iconColor: "text-pink-400",
    visual: "incident",
  },
  {
    icon: Globe,
    title: "THREAT INTELLIGENCE YOU CAN TRUST",
    desc: "Leverage global threat intelligence to stay ahead of attackers and make smarter security decisions.",
    bullets: ["IP Reputation", "IOC Enrichment", "Global Threat Feeds", "Risk Scoring"],
    gradient: "from-violet-600/20 to-purple-600/20",
    borderColor: "border-violet-500/20",
    iconBg: "bg-violet-500/10",
    iconColor: "text-violet-400",
    visual: "threat-intel",
  },
  {
    icon: Users,
    title: "BUILT FOR SECURITY TEAMS",
    desc: "Powerful tools designed to help security teams detect, investigate, and respond with confidence.",
    bullets: ["Role-Based Access", "Team Collaboration", "Audit Logging", "Compliance Ready"],
    gradient: "from-cyan-600/20 to-blue-600/20",
    borderColor: "border-cyan-500/20",
    iconBg: "bg-cyan-500/10",
    iconColor: "text-cyan-400",
    visual: "team",
  },
  {
    icon: Lock,
    title: "YOUR SECURITY. OUR PRIORITY.",
    desc: "Enterprise-grade security with scalability, reliability, and performance you can count on.",
    bullets: ["99.99% Uptime", "Scalable Architecture", "Data Encryption", "Compliance & Privacy"],
    gradient: "from-purple-600/20 to-indigo-600/20",
    borderColor: "border-purple-500/20",
    iconBg: "bg-purple-500/10",
    iconColor: "text-purple-400",
    visual: "priority",
  },
];

const stats = [
  { value: "10+", label: "Detection Rules" },
  { value: "<1s", label: "Alert Latency" },
  { value: "99.9%", label: "Uptime" },
  { value: "24/7", label: "Monitoring" },
];

/* Mini dashboard mock for the "COMPLETE VISIBILITY" card */
function DashboardMock() {
  return (
    <div className="w-full h-full p-3 rounded-xl bg-slate-900/80 border border-slate-700/30">
      <div className="text-[9px] font-semibold text-slate-400 mb-2">Security Overview</div>
      <div className="grid grid-cols-2 gap-1.5 mb-2">
        {[
          { label: "Firewalls", value: "1,248", icon: Shield, color: "text-purple-400" },
          { label: "Malwares", value: "24", icon: AlertTriangle, color: "text-red-400" },
          { label: "Servers", value: "156", icon: Server, color: "text-blue-400" },
          { label: "Policies", value: "87%", icon: Lock, color: "text-green-400" },
        ].map((s, i) => (
          <div key={i} className="flex items-center gap-1.5 p-1.5 rounded-lg bg-slate-800/50">
            <s.icon className={`w-3 h-3 ${s.color}`} />
            <div>
              <div className="text-[8px] text-slate-500">{s.label}</div>
              <div className="text-[10px] font-bold text-white">{s.value}</div>
            </div>
          </div>
        ))}
      </div>
      <div className="flex gap-2">
        <div className="flex-1">
          <div className="text-[8px] text-slate-500 mb-1">Alerts by Severity</div>
          <div className="flex gap-1 items-end h-8">
            {[60, 45, 30, 15].map((h, i) => (
              <div key={i} className="flex-1 rounded-sm" style={{ height: `${h}%`, background: ["#a855f7", "#ec4899", "#f97316", "#22c55e"][i] }} />
            ))}
          </div>
        </div>
        <div className="flex-1">
          <div className="text-[8px] text-slate-500 mb-1">Response Time</div>
          <svg className="w-full h-8" viewBox="0 0 100 30">
            <polyline fill="none" stroke="#a855f7" strokeWidth="1.5" points="0,25 20,20 40,15 60,18 80,8 100,5" />
            <polyline fill="none" stroke="#3b82f6" strokeWidth="1" strokeDasharray="3 2" points="0,22 20,18 40,20 60,12 80,10 100,7" />
          </svg>
        </div>
      </div>
    </div>
  );
}

/* Incident mock for "RESPOND FASTER" card */
function IncidentMock() {
  return (
    <div className="w-full h-full p-3 rounded-xl bg-slate-900/80 border border-slate-700/30">
      <div className="flex items-center justify-between mb-2">
        <div className="text-[9px] font-semibold text-red-400">INCIDENT INC-2024-1048</div>
        <span className="text-[7px] px-1.5 py-0.5 rounded-full bg-yellow-500/20 text-yellow-400 font-medium">INVESTIGATING</span>
      </div>
      <div className="flex gap-1 mb-2">
        {["NEW", "TRIAGE", "INVESTIGATING", "CONTAINED", "RESOLVED"].map((s, i) => (
          <div key={i} className="flex-1 text-center">
            <div className={`h-1 rounded-full ${i <= 2 ? "bg-purple-500" : "bg-slate-700"}`} />
            <div className={`text-[6px] mt-0.5 ${i <= 2 ? "text-purple-400" : "text-slate-600"}`}>{s}</div>
          </div>
        ))}
      </div>
      <div className="space-y-1">
        {[
          { label: "Type", value: "Brute Force Attack" },
          { label: "Severity", value: "High", color: "text-red-400" },
          { label: "Source", value: "185.237.XX.XX" },
        ].map((item, i) => (
          <div key={i} className="flex justify-between text-[8px]">
            <span className="text-slate-500">{item.label}</span>
            <span className={item.color || "text-slate-300"}>{item.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

/* Threat intel mock for "THREAT INTELLIGENCE" card */
function ThreatIntelMock() {
  return (
    <div className="w-full h-full p-3 rounded-xl bg-slate-900/80 border border-slate-700/30">
      <div className="text-[9px] font-semibold text-slate-400 mb-2">IOC Lookup</div>
      <div className="space-y-2">
        <div className="p-2 rounded-lg bg-red-500/5 border border-red-500/10">
          <div className="flex items-center gap-1 mb-1">
            <div className="w-1.5 h-1.5 rounded-full bg-red-500" />
            <span className="text-[8px] font-medium text-red-400">Malicious IP</span>
          </div>
          <div className="text-[8px] text-slate-400">185.237.XX.XX</div>
          <div className="text-[8px] text-slate-500">Risk Score: 92/100 · Country: RU</div>
          <div className="mt-1 inline-block text-[7px] px-1.5 py-0.5 rounded-full bg-red-500/20 text-red-400 font-medium">HIGH RISK</div>
        </div>
        <div className="p-2 rounded-lg bg-yellow-500/5 border border-yellow-500/10">
          <div className="flex items-center gap-1 mb-1">
            <div className="w-1.5 h-1.5 rounded-full bg-yellow-500" />
            <span className="text-[8px] font-medium text-yellow-400">Suspicious Domain</span>
          </div>
          <div className="text-[8px] text-slate-400">malicious-example.com</div>
          <div className="text-[8px] text-slate-500">Risk: 78/100 · Category: Phishing</div>
          <div className="mt-1 inline-block text-[7px] px-1.5 py-0.5 rounded-full bg-yellow-500/20 text-yellow-400 font-medium">MEDIUM RISK</div>
        </div>
      </div>
    </div>
  );
}

/* Team / SOC mock */
function TeamMock() {
  return (
    <div className="w-full h-full flex items-center justify-center p-3">
      <div className="relative w-full h-full rounded-xl bg-slate-900/80 border border-slate-700/30 overflow-hidden">
        {/* Grid background */}
        <div className="absolute inset-0 opacity-20" style={{backgroundImage: "linear-gradient(rgba(124,58,237,0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(124,58,237,0.3) 1px, transparent 1px)", backgroundSize: "20px 20px"}} />
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-16 h-16 rounded-full bg-purple-500/10 border border-purple-500/30 flex items-center justify-center">
            <Users className="w-8 h-8 text-purple-400" />
          </div>
        </div>
        {/* Orbiting dots */}
        {[0, 60, 120, 180, 240, 300].map((deg, i) => (
          <div key={i} className="absolute w-2 h-2 rounded-full bg-purple-400/60" style={{
            top: `${50 + 35 * Math.sin(deg * Math.PI / 180)}%`,
            left: `${50 + 35 * Math.cos(deg * Math.PI / 180)}%`,
            transform: "translate(-50%, -50%)",
          }} />
        ))}
      </div>
    </div>
  );
}

/* Priority / fortress mock */
function PriorityMock() {
  return (
    <div className="w-full h-full p-3 rounded-xl bg-slate-900/80 border border-slate-700/30 flex flex-col items-center justify-center gap-2">
      <div className="relative">
        <div className="w-14 h-14 rounded-full bg-purple-500/10 border-2 border-purple-500/30 flex items-center justify-center">
          <Shield className="w-8 h-8 text-purple-400" />
        </div>
        <div className="absolute -inset-2 rounded-full border border-purple-500/10 animate-ping" style={{animationDuration: "3s"}} />
      </div>
      <div className="grid grid-cols-3 gap-2 w-full">
        {[
          { icon: Lock, label: "Encryption" },
          { icon: Shield, label: "Compliance" },
          { icon: Activity, label: "Reliability" },
        ].map((item, i) => (
          <div key={i} className="text-center p-1.5 rounded-lg bg-slate-800/50">
            <item.icon className="w-3 h-3 text-purple-400 mx-auto mb-0.5" />
            <div className="text-[7px] text-slate-500">{item.label}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

const visuals: Record<string, React.FC> = {
  shield: () => (
    <div className="w-full h-full flex items-center justify-center">
      <div className="relative">
        <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-purple-500/20 to-violet-600/20 border border-purple-500/20 flex items-center justify-center">
          <Shield className="w-10 h-10 text-purple-400" />
        </div>
        <div className="absolute -inset-4 rounded-2xl border border-purple-500/10" />
        <div className="absolute -inset-8 rounded-2xl border border-purple-500/5" />
      </div>
    </div>
  ),
  dashboard: DashboardMock,
  incident: IncidentMock,
  "threat-intel": ThreatIntelMock,
  team: TeamMock,
  priority: PriorityMock,
};

function NetworkVisualization({ mounted }: { mounted: boolean }) {
  const nodes = [
    { x: 50, y: 12, label: "INTERNET", icon: Globe, color: "text-cyan-400", bg: "bg-cyan-500/10", border: "border-cyan-500/30" },
    { x: 18, y: 28, label: "CLOUD", icon: Database, color: "text-purple-400", bg: "bg-purple-500/10", border: "border-purple-500/30" },
    { x: 82, y: 22, label: "SERVER", icon: Server, color: "text-violet-400", bg: "bg-violet-500/10", border: "border-violet-500/30" },
    { x: 50, y: 48, label: "FIREWALL", icon: Shield, color: "text-pink-400", bg: "bg-pink-500/10", border: "border-pink-500/30" },
    { x: 18, y: 68, label: "ENDPOINT", icon: Cpu, color: "text-blue-400", bg: "bg-blue-500/10", border: "border-blue-500/30" },
    { x: 50, y: 82, label: "NETWORK", icon: Wifi, color: "text-green-400", bg: "bg-green-500/10", border: "border-green-500/30" },
    { x: 82, y: 72, label: "DATABASE", icon: Database, color: "text-cyan-400", bg: "bg-cyan-500/10", border: "border-cyan-500/30" },
  ];

  return (
    <div className="relative w-full h-[520px] hidden lg:block">
      <div className="absolute inset-0 rounded-2xl overflow-hidden border border-slate-800/30 bg-slate-900/20">
        {/* Grid */}
        <div className="absolute inset-0 opacity-10" style={{backgroundImage: "linear-gradient(rgba(124,58,237,0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(124,58,237,0.3) 1px, transparent 1px)", backgroundSize: "40px 40px"}} />

        {/* Center shield with glow */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
          <div className="w-32 h-32 rounded-full bg-purple-500/10 border-2 border-purple-500/30 flex items-center justify-center" style={{boxShadow: "0 0 60px rgba(168,85,247,0.15), 0 0 120px rgba(168,85,247,0.05)"}}>
            <div className="w-20 h-20 rounded-full bg-purple-500/20 border border-purple-500/40 flex items-center justify-center">
              <Lock className="w-10 h-10 text-purple-400" />
            </div>
          </div>
          <div className="absolute inset-0 rounded-full border border-purple-500/10 animate-ping" style={{animationDuration: "3s"}} />
          <div className="absolute -inset-8 rounded-full border border-purple-500/5 animate-ping" style={{animationDuration: "4s"}} />
        </div>

        {/* Nodes */}
        {nodes.map((node, i) => (
          <div key={i} className="absolute flex flex-col items-center gap-1.5" style={{ left: `${node.x}%`, top: `${node.y}%`, transform: "translate(-50%, -50%)" }}>
            <div className={`w-12 h-12 rounded-xl ${node.bg} border ${node.border} flex items-center justify-center transition-all duration-500 ${mounted ? "opacity-100 scale-100" : "opacity-0 scale-75"}`}>
              <node.icon className={`w-6 h-6 ${node.color}`} />
            </div>
            <span className="text-[10px] font-medium text-slate-500">{node.label}</span>
          </div>
        ))}

        {/* Connection lines */}
        <svg className="absolute inset-0 w-full h-full" style={{ opacity: 0.2 }}>
          {nodes.slice(1).map((node, i) => (
            <line key={i} x1="50%" y1="50%" x2={`${node.x}%`} y2={`${node.y}%`} stroke="#7c3aed" strokeWidth="1" strokeDasharray="6 6" />
          ))}
        </svg>

        {/* Threat detected card */}
        <div className="absolute top-6 right-6 p-3 rounded-xl bg-red-500/10 border border-red-500/20">
          <div className="flex items-center gap-2 mb-1">
            <AlertTriangle className="w-4 h-4 text-red-400" />
            <span className="text-[10px] font-bold text-red-400">THREAT DETECTED</span>
          </div>
          <div className="text-[10px] text-slate-400">Source IP: 185.237.XX.XX</div>
          <div className="text-[10px] text-slate-400">Risk Score: 92/100</div>
          <div className="text-[10px] text-slate-400">Location: Eastern Europe</div>
        </div>

        {/* Active threats */}
        <div className="absolute top-6 left-6 p-3 rounded-xl bg-slate-800/60 border border-slate-700/50">
          <div className="text-[10px] text-slate-500 mb-1">ACTIVE THREATS</div>
          <div className="text-xl font-bold text-white">1,248</div>
          <div className="text-[10px] text-green-400">+ 23% vs last 24h</div>
        </div>

        {/* Protection status */}
        <div className="absolute bottom-6 right-6 p-3 rounded-xl bg-slate-800/60 border border-slate-700/50">
          <div className="text-[10px] text-slate-500 mb-1">PROTECTION STATUS</div>
          <div className="flex items-center gap-3">
            <div className="relative w-10 h-10">
              <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="42" fill="none" stroke="#1e293b" strokeWidth="8" />
                <circle cx="50" cy="50" r="42" fill="none" stroke="#a855f7" strokeWidth="8" strokeLinecap="round" strokeDasharray={264} strokeDashoffset={34} />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center text-xs font-bold text-white">87%</div>
            </div>
            <div>
              <div className="text-xs font-bold text-white">SECURE</div>
              <div className="text-[9px] text-slate-500">All systems protected</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function HomePage() {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  return (
    <div className="min-h-screen bg-[#080b16] text-slate-200 overflow-x-hidden">
      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 border-b border-slate-800/50 bg-[#080b16]/80 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link href="/home" className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-purple-500 to-violet-600 flex items-center justify-center shadow-lg shadow-purple-500/20">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-white">NIKS <span className="text-purple-400">SECURITY</span></span>
          </Link>
          <div className="hidden md:flex items-center gap-8 text-sm text-slate-400">
            <Link href="/home#features" className="hover:text-white transition-colors">Features</Link>
            <Link href="/home#how-it-works" className="hover:text-white transition-colors">How It Works</Link>
            <Link href="/home#pricing" className="hover:text-white transition-colors">Pricing</Link>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/login" className="text-sm text-slate-300 hover:text-white transition-colors px-4 py-2">Login</Link>
            <Link href="/signup" className="text-sm font-medium bg-purple-600 hover:bg-purple-500 text-white px-5 py-2 rounded-xl transition-all hover:shadow-lg hover:shadow-purple-500/20">
              Start Free Trial
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section with Antigravity */}
      <section className="relative pt-32 pb-20 px-6 overflow-hidden">
        {/* Background effects */}
        <div className="absolute inset-0 opacity-[0.03]" style={{backgroundImage: "radial-gradient(circle at 1px 1px, rgba(124,58,237,0.5) 1px, transparent 0)", backgroundSize: "40px 40px"}} />
        <div className="absolute top-20 left-1/4 w-96 h-96 bg-purple-600/10 rounded-full blur-[120px]" />
        <div className="absolute top-40 right-1/4 w-96 h-96 bg-violet-600/10 rounded-full blur-[120px]" />

        {/* Antigravity particle background */}
        <div className="absolute inset-0 z-0" style={{ opacity: 0.3 }}>
          {mounted && (
            <Antigravity
              count={200}
              magnetRadius={6}
              ringRadius={7}
              waveSpeed={0.4}
              waveAmplitude={1}
              particleSize={1.2}
              lerpSpeed={0.05}
              color="#a855f7"
              autoAnimate={true}
              particleVariance={1}
            />
          )}
        </div>

        <div className="max-w-7xl mx-auto relative z-10">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            {/* Left content */}
            <div className="max-w-xl">
              <div className={`inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-purple-500/20 bg-purple-500/5 text-purple-400 text-sm mb-6 transition-all duration-700 ${mounted ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"}`}>
                <Zap className="w-3.5 h-3.5" />
                AI-POWERED THREAT DETECTION
              </div>
              <h1 className={`text-5xl md:text-7xl font-bold leading-tight mb-6 transition-all duration-700 delay-100 ${mounted ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"}`}>
                <span className="text-white">DETECT.</span><br />
                <span className="text-white">INVESTIGATE.</span><br />
                <span className="bg-gradient-to-r from-purple-400 via-violet-400 to-pink-400 bg-clip-text text-transparent">RESPOND.</span>
              </h1>
              <p className={`text-lg text-slate-400 mb-8 leading-relaxed transition-all duration-700 delay-200 ${mounted ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"}`}>
                AI-powered threat detection and response platform for modern infrastructure.
              </p>

              {/* Feature bullets */}
              <div className={`grid grid-cols-2 gap-4 mb-8 transition-all duration-700 delay-300 ${mounted ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"}`}>
                {[
                  { icon: Activity, text: "Real-Time Protection", desc: "24/7 monitoring across your infrastructure" },
                  { icon: Eye, text: "AI-Powered Detection", desc: "Identify advanced threats before they impact" },
                  { icon: Search, text: "Deep Investigation", desc: "Powerful tools to analyze and respond faster" },
                  { icon: BarChart3, text: "Actionable Intelligence", desc: "Threat intelligence enriched with context" },
                ].map((f, i) => (
                  <div key={i} className="flex items-start gap-3">
                    <div className="w-8 h-8 rounded-lg bg-purple-500/10 border border-purple-500/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                      <f.icon className="w-4 h-4 text-purple-400" />
                    </div>
                    <div>
                      <div className="text-xs font-semibold text-white mb-0.5">{f.text}</div>
                      <div className="text-[10px] text-slate-500 leading-relaxed">{f.desc}</div>
                    </div>
                  </div>
                ))}
              </div>

              <div className={`flex items-center gap-4 transition-all duration-700 delay-500 ${mounted ? "opacity-100" : "opacity-0"}`}>
                <Link href="/signup" className="inline-flex items-center gap-2 bg-purple-600 hover:bg-purple-500 text-white font-medium px-8 py-3.5 rounded-xl transition-all hover:shadow-xl hover:shadow-purple-500/20 hover:-translate-y-0.5">
                  Explore Platform <ArrowRight className="w-4 h-4" />
                </Link>
              </div>
            </div>

            {/* Right visualization */}
            <div className={`transition-all duration-1000 delay-300 ${mounted ? "opacity-100 translate-x-0" : "opacity-0 translate-x-12"}`}>
              <NetworkVisualization mounted={mounted} />
            </div>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-12 border-y border-slate-800/50">
        <div className="max-w-7xl mx-auto px-6 grid grid-cols-2 md:grid-cols-4 gap-8">
          {stats.map((s, i) => (
            <div key={i} className="text-center">
              <div className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-violet-300 bg-clip-text text-transparent">{s.value}</div>
              <div className="text-sm text-slate-500 mt-1">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* 6 Feature Cards — matching the reference image grid */}
      <section id="features" className="py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">Everything You Need to <span className="bg-gradient-to-r from-purple-400 to-violet-400 bg-clip-text text-transparent">Stay Secure</span></h2>
            <p className="text-slate-400 max-w-2xl mx-auto">A complete security operations platform built for modern infrastructure</p>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            {features.map((f, i) => {
              const Visual = visuals[f.visual];
              return (
                <div key={i} className={`group rounded-2xl border ${f.borderColor} bg-gradient-to-br ${f.gradient} overflow-hidden hover:shadow-lg hover:shadow-purple-500/5 transition-all duration-300`}>
                  {/* Visual area */}
                  <div className="h-48 p-4">
                    {Visual && <Visual />}
                  </div>
                  {/* Content area */}
                  <div className="p-6 border-t border-slate-800/30">
                    <h3 className="text-sm font-bold text-white mb-2 tracking-wide">{f.title}</h3>
                    <p className="text-xs text-slate-400 mb-4 leading-relaxed">{f.desc}</p>
                    <ul className="space-y-1.5">
                      {f.bullets.map((b, j) => (
                        <li key={j} className="flex items-center gap-2 text-xs text-slate-400">
                          <CheckCircle className={`w-3 h-3 ${f.iconColor} flex-shrink-0`} />{b}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-24 px-6 border-t border-slate-800/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">How It Works</h2>
            <p className="text-slate-400">The complete security workflow from collection to response</p>
          </div>
          <div className="grid md:grid-cols-5 gap-4">
            {[
              { num: "01", title: "Collect", desc: "Ingest security logs from servers, endpoints, and applications" },
              { num: "02", title: "Detect", desc: "AI-powered detection rules identify threats in real-time" },
              { num: "03", title: "Alert", desc: "Priority-ranked alerts with full context and MITRE mapping" },
              { num: "04", title: "Investigate", desc: "Deep investigation tools with timeline and evidence analysis" },
              { num: "05", title: "Respond", desc: "Incident response workflow from detection to resolution" },
            ].map((s, i) => (
              <div key={i} className="relative text-center p-6 rounded-2xl border border-slate-800/50 bg-slate-900/20 hover:border-purple-500/20 transition-all">
                <div className="text-4xl font-bold text-purple-600/20 mb-3">{s.num}</div>
                <h3 className="text-lg font-semibold text-white mb-2">{s.title}</h3>
                <p className="text-xs text-slate-400">{s.desc}</p>
                {i < 4 && <ChevronRight className="absolute top-1/2 -right-3 w-5 h-5 text-slate-700 hidden md:block" />}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="py-24 px-6 border-t border-slate-800/50">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">Simple Pricing</h2>
            <p className="text-slate-400">Start free, scale as you grow</p>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            {[
              { name: "Free", price: "$0", period: "forever", features: ["10 assets", "10,000 events/day", "3 users", "5 detection rules", "Community support"], cta: "Get Started", highlighted: false },
              { name: "Pro", price: "$99", period: "/month", features: ["100 assets", "1M events/day", "10 users", "Unlimited rules", "Priority support", "Custom reports", "API access"], cta: "Start Free Trial", highlighted: true },
              { name: "Enterprise", price: "Custom", period: "", features: ["Unlimited assets", "Unlimited events", "Unlimited users", "Custom rules", "24/7 support", "SSO/SAML", "On-premise option", "SLA guarantee"], cta: "Contact Sales", highlighted: false },
            ].map((p, i) => (
              <div key={i} className={`relative p-8 rounded-2xl border transition-all ${p.highlighted ? "border-purple-500/30 bg-purple-500/5 shadow-xl shadow-purple-500/10" : "border-slate-800/50 bg-slate-900/20"}`}>
                {p.highlighted && <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-0.5 bg-purple-600 text-white text-xs font-medium rounded-full">Most Popular</div>}
                <h3 className="text-lg font-semibold text-white mb-1">{p.name}</h3>
                <div className="flex items-baseline gap-1 mb-6">
                  <span className="text-4xl font-bold text-white">{p.price}</span>
                  <span className="text-sm text-slate-500">{p.period}</span>
                </div>
                <ul className="space-y-3 mb-8">
                  {p.features.map((f, j) => (
                    <li key={j} className="flex items-center gap-2 text-sm text-slate-400">
                      <CheckCircle className="w-4 h-4 text-purple-400 flex-shrink-0" />{f}
                    </li>
                  ))}
                </ul>
                <Link href="/signup" className={`block text-center py-3 rounded-xl font-medium transition-all ${p.highlighted ? "bg-purple-600 hover:bg-purple-500 text-white" : "border border-slate-700 hover:border-slate-500 text-slate-300 hover:text-white"}`}>
                  {p.cta}
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <div className="p-12 rounded-3xl border border-slate-800/50 bg-gradient-to-br from-slate-900/50 to-purple-900/10 relative overflow-hidden">
            <div className="absolute inset-0 opacity-5" style={{backgroundImage: "radial-gradient(circle at 2px 2px, rgba(124,58,237,1) 1px, transparent 0)", backgroundSize: "32px 32px"}} />
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4 relative">Ready to Secure Your Infrastructure?</h2>
            <p className="text-slate-400 mb-8 relative">Start detecting threats in minutes. No credit card required.</p>
            <Link href="/signup" className="relative inline-flex items-center gap-2 bg-purple-600 hover:bg-purple-500 text-white font-medium px-8 py-4 rounded-xl transition-all hover:shadow-xl hover:shadow-purple-500/20">
              Start Free Trial <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-800/50 py-12 px-6">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-violet-600 flex items-center justify-center">
              <Shield className="w-4 h-4 text-white" />
            </div>
            <span className="font-bold text-white">NIKS <span className="text-purple-400">SECURITY</span></span>
          </div>
          <div className="text-sm text-slate-500">© 2026 Niks Security. All rights reserved.</div>
        </div>
      </footer>
    </div>
  );
}
