"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState, useCallback } from "react";
import {
  Shield, LayoutDashboard, AlertTriangle, FileWarning, Target, FileText, Settings, Bell, LogOut,
  Menu, X, Upload, ShieldCheck, Activity, Globe, BarChart3, Users
} from "lucide-react";
import { apiFetch } from "@/lib/utils";
import { useRealtimeAlerts } from "@/lib/useRealtimeAlerts";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/dashboard/alerts", label: "Alerts", icon: AlertTriangle },
  { href: "/dashboard/incidents", label: "Incidents", icon: FileWarning },
  { href: "/dashboard/threat-intel", label: "Threat Intelligence", icon: Globe },
  { href: "/dashboard/logs", label: "Logs", icon: FileText },
  { href: "/dashboard/assets", label: "Assets", icon: ShieldCheck },
  { href: "/dashboard/rules", label: "Detection Rules", icon: Target },
  { href: "/dashboard/mitre", label: "MITRE ATT&CK", icon: Activity },
  { href: "/dashboard/reports", label: "Reports", icon: BarChart3 },
  { href: "/dashboard/simulation", label: "Attack Simulation", icon: Zap },
  { href: "/dashboard/settings", label: "Settings", icon: Settings },
];

function Zap(props: any) {
  return <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...props}><path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"/></svg>;
}

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [user, setUser] = useState<any>(null);
  const [realtimeAlertCount, setRealtimeAlertCount] = useState(0);
  const [latestAlert, setLatestAlert] = useState<any>(null);
  const [showAlertToast, setShowAlertToast] = useState(false);

  // Real-time SSE connection
  const handleNewAlert = useCallback((alert: any) => {
    setRealtimeAlertCount((prev) => prev + 1);
    setLatestAlert(alert);
    setShowAlertToast(true);
    setTimeout(() => setShowAlertToast(false), 5000);
  }, []);

  // We connect once we know the org_id from user data
  // SSE will be initialized in the effect below

  useEffect(() => {
    const token = localStorage.getItem("token");
    const userData = localStorage.getItem("user");
    if (!token) {
      router.push("/login");
      return;
    }
    if (userData) {
      try { setUser(JSON.parse(userData)); } catch {}
    }

    // Check onboarding status for new users
    apiFetch("/api/onboarding/status")
      .then((data) => {
        if (data.onboarding_needed) {
          router.push("/onboarding");
        }
      })
      .catch(() => {}); // Ignore errors — user can still use dashboard
  }, [router]);

  // Initialize SSE once user is loaded
  const orgId = user?.organization_id;
  const { connected } = useRealtimeAlerts({
    orgId: orgId || 0,
    onAlert: handleNewAlert,
  });

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    router.push("/login");
  };

  return (
    <div className="min-h-screen flex bg-[#080b16]">
      {/* Desktop Sidebar */}
      <aside className={`hidden lg:flex flex-col fixed inset-y-0 left-0 z-40 border-r border-slate-800/50 bg-[#0c0f1e] transition-all duration-300 ${sidebarOpen ? "w-64" : "w-20"}`}>
        {/* Logo */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-slate-800/50">
          {sidebarOpen && (
            <Link href="/dashboard" className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-purple-500 to-violet-600 flex items-center justify-center shadow-lg shadow-purple-500/20">
                <Shield className="w-5 h-5 text-white" />
              </div>
              <span className="text-lg font-bold text-white">NIKS <span className="text-purple-400">SECURITY</span></span>
            </Link>
          )}
          {!sidebarOpen && (
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-purple-500 to-violet-600 flex items-center justify-center mx-auto shadow-lg shadow-purple-500/20">
              <Shield className="w-5 h-5 text-white" />
            </div>
          )}
          <button onClick={() => setSidebarOpen(!sidebarOpen)} className={`p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800/50 ${!sidebarOpen ? "hidden" : ""}`}>
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="m15 18-6-6 6-6"/></svg>
          </button>
        </div>

        {/* Nav items */}
        <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
          {navItems.map((item) => {
            const isActive = pathname === item.href || (item.href !== "/dashboard" && pathname?.startsWith(item.href));
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  isActive
                    ? "bg-purple-600/15 text-purple-400 border border-purple-500/20 shadow-lg shadow-purple-500/5"
                    : "text-slate-400 hover:text-white hover:bg-slate-800/50"
                }`}
                title={!sidebarOpen ? item.label : undefined}
              >
                <item.icon className={`w-5 h-5 flex-shrink-0 ${isActive ? "text-purple-400" : ""}`} />
                {sidebarOpen && <span className="whitespace-nowrap">{item.label}</span>}
              </Link>
            );
          })}
        </nav>

        {/* Protection Status */}
        {sidebarOpen && (
          <div className="p-4 mx-3 mb-3 rounded-2xl bg-gradient-to-br from-purple-900/30 to-slate-900/50 border border-purple-500/10">
            <div className="flex items-center justify-center mb-3">
              <div className="relative w-20 h-20">
                <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
                  <circle cx="50" cy="50" r="42" fill="none" stroke="#1e293b" strokeWidth="6" />
                  <circle cx="50" cy="50" r="42" fill="none" stroke="url(#protectGrad)" strokeWidth="6" strokeLinecap="round" strokeDasharray={2 * Math.PI * 42} strokeDashoffset={2 * Math.PI * 42 * 0.13} />
                  <defs>
                    <linearGradient id="protectGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" stopColor="#a855f7" />
                      <stop offset="100%" stopColor="#06b6d4" />
                    </linearGradient>
                  </defs>
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <div className="text-lg font-bold text-white">87%</div>
                    <div className="text-[9px] text-purple-400">SECURE</div>
                  </div>
                </div>
              </div>
            </div>
            <p className="text-[10px] text-slate-400 text-center">All systems are protected</p>
            <button className="w-full mt-2 py-1.5 rounded-lg text-[10px] text-purple-400 border border-purple-500/20 hover:bg-purple-500/10 transition-colors">View Security Score</button>
          </div>
        )}

        {/* User section */}
        <div className="p-3 border-t border-slate-800/50">
          {sidebarOpen ? (
            <div className="flex items-center gap-3 px-3 py-2">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-purple-500 to-violet-600 flex items-center justify-center text-sm font-bold text-white shadow-lg shadow-purple-500/20">
                {user?.username?.[0]?.toUpperCase() || "U"}
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium text-white truncate">{user?.organization_name || "Security Labs"}</div>
                <div className="text-xs text-slate-500 truncate">{user?.role || "Admin"}</div>
              </div>
              <button onClick={logout} className="p-1.5 text-slate-500 hover:text-red-400 rounded-lg hover:bg-slate-800/50" title="Logout">
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <button onClick={logout} className="w-full p-2 text-slate-500 hover:text-red-400 rounded-lg hover:bg-slate-800/50 flex justify-center" title="Logout">
              <LogOut className="w-4 h-4" />
            </button>
          )}
        </div>
      </aside>

      {/* Mobile overlay */}
      {mobileOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="absolute inset-0 bg-black/60" onClick={() => setMobileOpen(false)} />
          <aside className="absolute inset-y-0 left-0 w-72 bg-[#0c0f1e] border-r border-slate-800/50 p-4">
            <div className="flex items-center justify-between mb-6">
              <span className="text-lg font-bold text-white">NIKS <span className="text-purple-400">SECURITY</span></span>
              <button onClick={() => setMobileOpen(false)} className="text-slate-400"><X className="w-5 h-5" /></button>
            </div>
            <nav className="space-y-1">
              {navItems.map((item) => {
                const isActive = pathname === item.href;
                return (
                  <Link key={item.href} href={item.href} onClick={() => setMobileOpen(false)} className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium ${isActive ? "bg-purple-600/15 text-purple-400 border border-purple-500/20" : "text-slate-400 hover:text-white hover:bg-slate-800/50"}`}>
                    <item.icon className="w-5 h-5" />{item.label}
                  </Link>
                );
              })}
            </nav>
          </aside>
        </div>
      )}

      {/* Main content */}
      <div className={`flex-1 flex flex-col transition-all duration-300 ${sidebarOpen ? "lg:ml-64" : "lg:ml-20"}`}>
        {/* Top bar */}
        <header className="h-16 border-b border-slate-800/50 flex items-center justify-between px-6 bg-[#0c0f1e]/80 backdrop-blur-sm sticky top-0 z-30">
          <div className="flex items-center gap-4">
            <button onClick={() => setMobileOpen(true)} className="lg:hidden p-2 text-slate-400 hover:text-white">
              <Menu className="w-5 h-5" />
            </button>
            {/* Search bar */}
            <div className="hidden md:flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800/30 border border-slate-700/30 text-slate-500 text-sm min-w-[200px]">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
              <span>Search</span>
              <span className="ml-auto text-[10px] px-1.5 py-0.5 rounded bg-slate-700/50 text-slate-500">⌘K</span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button className="relative p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800/50">
              <Bell className="w-5 h-5" />
              {realtimeAlertCount > 0 && (
                <span className="absolute -top-0.5 -right-0.5 min-w-[16px] h-4 bg-red-500 rounded-full flex items-center justify-center text-[9px] font-bold text-white px-1 animate-bounce">
                  {realtimeAlertCount > 99 ? "99+" : realtimeAlertCount}
                </span>
              )}
              {realtimeAlertCount === 0 && (
                <span className="absolute -top-0.5 -right-0.5 w-4 h-4 bg-purple-500 rounded-full flex items-center justify-center text-[9px] font-bold text-white">12</span>
              )}
            </button>
            <button className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800/50">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><path d="M12 17h.01"/></svg>
            </button>
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-800/30 border border-slate-700/30 cursor-pointer hover:bg-slate-800/50 transition-colors">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-purple-500 to-violet-600 flex items-center justify-center text-xs font-bold text-white">
                {user?.username?.[0]?.toUpperCase() || "N"}
              </div>
              <div className="hidden sm:block">
                <div className="text-xs font-medium text-white">{user?.full_name || user?.organization_name || "Security Labs"}</div>
                <div className="text-[10px] text-slate-500">{user?.role || "Admin"}</div>
              </div>
            </div>
          </div>
        </header>

        {/* Real-time alert toast */}
        {showAlertToast && latestAlert && (
          <div className="fixed top-20 right-6 z-50 animate-slide-in-right">
            <div className="p-4 rounded-xl border bg-slate-900/95 backdrop-blur-xl shadow-2xl shadow-red-500/10 max-w-sm"
              style={{ borderColor: latestAlert.severity === "critical" ? "rgba(239,68,68,0.3)" : latestAlert.severity === "high" ? "rgba(249,115,22,0.3)" : "rgba(168,85,247,0.3)" }}
            >
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg flex items-center justify-center"
                  style={{ background: latestAlert.severity === "critical" ? "rgba(239,68,68,0.15)" : latestAlert.severity === "high" ? "rgba(249,115,22,0.15)" : "rgba(168,85,247,0.15)" }}
                >
                  <AlertTriangle className="w-4 h-4" style={{ color: latestAlert.severity === "critical" ? "#ef4444" : latestAlert.severity === "high" ? "#f97316" : "#a855f7" }} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-xs font-semibold text-white truncate">{latestAlert.title}</div>
                  <div className="text-[10px] text-slate-400">Risk: {latestAlert.risk_score}/100 · {latestAlert.source_ip}</div>
                </div>
                <span className="text-[9px] px-1.5 py-0.5 rounded-full font-medium"
                  style={{ background: latestAlert.severity === "critical" ? "rgba(239,68,68,0.15)" : latestAlert.severity === "high" ? "rgba(249,115,22,0.15)" : "rgba(168,85,247,0.15)", color: latestAlert.severity === "critical" ? "#ef4444" : latestAlert.severity === "high" ? "#f97316" : "#a855f7" }}
                >
                  {latestAlert.severity?.toUpperCase()}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Connection indicator */}
        <div className="fixed bottom-4 right-4 z-40">
          <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] ${connected ? "bg-green-500/10 text-green-400 border border-green-500/20" : "bg-slate-800/50 text-slate-500 border border-slate-700/30"}`}>
            <div className={`w-1.5 h-1.5 rounded-full ${connected ? "bg-green-400 animate-pulse" : "bg-slate-600"}`} />
            {connected ? "Live" : "Reconnecting..."}
          </div>
        </div>

        {/* Page content */}
        <main className="flex-1 p-6 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
