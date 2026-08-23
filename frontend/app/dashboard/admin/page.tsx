"use client";
import { useEffect, useState, useCallback } from "react";
import { apiFetch } from "@/lib/utils";
import {
  Users, Shield, Activity, AlertTriangle, FileWarning, HardDrive,
  Search, MoreVertical, UserCheck, UserX, Trash2, Crown, Eye,
  ChevronLeft, ChevronRight, RefreshCw, Clock, TrendingUp, Zap
} from "lucide-react";

interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  is_verified: boolean;
  last_login: string | null;
  created_at: string | null;
}

interface SystemStats {
  total_users: number;
  active_users: number;
  total_alerts: number;
  critical_alerts: number;
  total_incidents: number;
  total_events: number;
  total_assets: number;
  recent_activity: ActivityLog[];
}

interface ActivityLog {
  id: number;
  action: string;
  resource_type: string;
  details: string;
  ip_address: string;
  user_id: number;
  created_at: string;
}

const ROLE_COLORS: Record<string, string> = {
  admin: "text-purple-400 bg-purple-500/10 border-purple-500/20",
  analyst: "text-blue-400 bg-blue-500/10 border-blue-500/20",
  viewer: "text-slate-400 bg-slate-500/10 border-slate-500/20",
};

const ACTION_COLORS: Record<string, string> = {
  user_signup: "text-green-400",
  user_login: "text-blue-400",
  admin_user_updated: "text-yellow-400",
  admin_user_deactivated: "text-red-400",
  password_reset_requested: "text-orange-400",
  alert_updated: "text-purple-400",
  onboarding_completed: "text-cyan-400",
  team_invite_sent: "text-indigo-400",
};

export default function AdminPage() {
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [totalUsers, setTotalUsers] = useState(0);
  const [userPage, setUserPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState("");
  const [roleFilter, setRoleFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [editingUser, setEditingUser] = useState<number | null>(null);

  const fetchStats = useCallback(async () => {
    try {
      const data = await apiFetch("/api/auth/admin/stats");
      setStats(data);
    } catch (err) {
      console.error("Failed to load admin stats", err);
    }
  }, []);

  const fetchUsers = useCallback(async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({ page: String(userPage), limit: "10" });
      if (searchQuery) params.set("search", searchQuery);
      if (roleFilter) params.set("role", roleFilter);
      const data = await apiFetch(`/api/auth/admin/users?${params}`);
      setUsers(data.users);
      setTotalUsers(data.total);
    } catch (err) {
      console.error("Failed to load users", err);
    } finally {
      setLoading(false);
    }
  }, [userPage, searchQuery, roleFilter]);

  useEffect(() => { fetchStats(); fetchUsers(); }, [fetchStats, fetchUsers]);

  const updateUser = async (userId: number, updates: { role?: string; is_active?: boolean }) => {
    try {
      await apiFetch(`/api/auth/admin/users/${userId}`, {
        method: "PUT",
        body: JSON.stringify(updates),
      });
      setEditingUser(null);
      fetchUsers();
      fetchStats();
    } catch (err: any) {
      alert(err.message || "Failed to update user");
    }
  };

  const deactivateUser = async (userId: number) => {
    if (!confirm("Are you sure you want to deactivate this user?")) return;
    try {
      await apiFetch(`/api/auth/admin/users/${userId}`, { method: "DELETE" });
      fetchUsers();
      fetchStats();
    } catch (err: any) {
      alert(err.message || "Failed to deactivate user");
    }
  };

  const formatAction = (action: string) => {
    return action.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return "Never";
    const d = new Date(dateStr);
    const now = new Date();
    const diffMins = Math.floor((now.getTime() - d.getTime()) / 60000);
    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHrs = Math.floor(diffMins / 60);
    if (diffHrs < 24) return `${diffHrs}h ago`;
    return d.toLocaleDateString();
  };

  const totalPages = Math.ceil(totalUsers / 10);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <Crown className="w-7 h-7 text-purple-400" />
            Admin Dashboard
          </h1>
          <p className="text-slate-400 text-sm mt-1">Manage users, roles, and system activity</p>
        </div>
        <button onClick={() => { fetchStats(); fetchUsers(); }} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800/50 border border-slate-700/30 text-slate-400 hover:text-white hover:bg-slate-800 transition-colors text-sm">
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>

      {/* Stats Grid */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard icon={Users} label="Total Users" value={stats.total_users} sub={`${stats.active_users} active`} color="purple" />
          <StatCard icon={AlertTriangle} label="Total Alerts" value={stats.total_alerts} sub={`${stats.critical_alerts} critical`} color="red" />
          <StatCard icon={FileWarning} label="Incidents" value={stats.total_incidents} sub="Active" color="orange" />
          <StatCard icon={HardDrive} label="Events Analyzed" value={stats.total_events} sub={`${stats.total_assets} assets`} color="cyan" />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* User Management Table */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white">User Management</h2>
            <span className="text-xs text-slate-500">{totalUsers} total users</span>
          </div>

          {/* Search & Filter */}
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => { setSearchQuery(e.target.value); setUserPage(1); }}
                placeholder="Search by name or email..."
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-800/50 border border-slate-700/30 text-white text-sm placeholder-slate-500 focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500 transition-colors"
              />
            </div>
            <select
              value={roleFilter}
              onChange={(e) => { setRoleFilter(e.target.value); setUserPage(1); }}
              className="px-4 py-2.5 rounded-xl bg-slate-800/50 border border-slate-700/30 text-white text-sm focus:outline-none focus:border-purple-500"
            >
              <option value="">All Roles</option>
              <option value="admin">Admin</option>
              <option value="analyst">Analyst</option>
              <option value="viewer">Viewer</option>
            </select>
          </div>

          {/* Users Table */}
          <div className="rounded-2xl border border-slate-800/50 bg-slate-900/30 backdrop-blur-xl overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-800/50">
                  <th className="text-left px-4 py-3 text-xs font-medium text-slate-400 uppercase tracking-wider">User</th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-slate-400 uppercase tracking-wider">Role</th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-slate-400 uppercase tracking-wider">Status</th>
                  <th className="text-left px-4 py-3 text-xs font-medium text-slate-400 uppercase tracking-wider">Last Login</th>
                  <th className="text-right px-4 py-3 text-xs font-medium text-slate-400 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/30">
                {loading ? (
                  <tr><td colSpan={5} className="px-4 py-12 text-center text-slate-500 text-sm">Loading users...</td></tr>
                ) : users.length === 0 ? (
                  <tr><td colSpan={5} className="px-4 py-12 text-center text-slate-500 text-sm">No users found</td></tr>
                ) : users.map((user) => (
                  <tr key={user.id} className="hover:bg-slate-800/20 transition-colors">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-violet-600 flex items-center justify-center text-xs font-bold text-white">
                          {user.username[0]?.toUpperCase()}
                        </div>
                        <div>
                          <div className="text-sm font-medium text-white">{user.full_name || user.username}</div>
                          <div className="text-xs text-slate-500">{user.email}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      {editingUser === user.id ? (
                        <select
                          value={user.role}
                          onChange={(e) => updateUser(user.id, { role: e.target.value })}
                          onBlur={() => setEditingUser(null)}
                          autoFocus
                          className="px-2 py-1 rounded-lg bg-slate-800 border border-slate-700/50 text-xs text-white focus:outline-none focus:border-purple-500"
                        >
                          <option value="admin">Admin</option>
                          <option value="analyst">Analyst</option>
                          <option value="viewer">Viewer</option>
                        </select>
                      ) : (
                        <button onClick={() => setEditingUser(user.id)} className={`inline-flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-medium border cursor-pointer hover:opacity-80 ${ROLE_COLORS[user.role] || ROLE_COLORS.viewer}`}>
                          {user.role === "admin" && <Crown className="w-3 h-3" />}
                          {user.role.charAt(0).toUpperCase() + user.role.slice(1)}
                        </button>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() => updateUser(user.id, { is_active: !user.is_active })}
                        className={`inline-flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-medium border cursor-pointer hover:opacity-80 ${
                          user.is_active
                            ? "text-green-400 bg-green-500/10 border-green-500/20"
                            : "text-red-400 bg-red-500/10 border-red-500/20"
                        }`}
                      >
                        {user.is_active ? <UserCheck className="w-3 h-3" /> : <UserX className="w-3 h-3" />}
                        {user.is_active ? "Active" : "Inactive"}
                      </button>
                    </td>
                    <td className="px-4 py-3 text-xs text-slate-400">{formatDate(user.last_login)}</td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end gap-1">
                        <button
                          onClick={() => setEditingUser(editingUser === user.id ? null : user.id)}
                          className="p-1.5 rounded-lg text-slate-500 hover:text-white hover:bg-slate-800/50 transition-colors"
                          title="Edit role"
                        >
                          <MoreVertical className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => deactivateUser(user.id)}
                          className="p-1.5 rounded-lg text-slate-500 hover:text-red-400 hover:bg-red-500/10 transition-colors"
                          title="Deactivate user"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between px-4 py-3 border-t border-slate-800/50">
                <span className="text-xs text-slate-500">Page {userPage} of {totalPages}</span>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setUserPage(Math.max(1, userPage - 1))}
                    disabled={userPage === 1}
                    className="p-1.5 rounded-lg text-slate-500 hover:text-white hover:bg-slate-800/50 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => setUserPage(Math.min(totalPages, userPage + 1))}
                    disabled={userPage === totalPages}
                    className="p-1.5 rounded-lg text-slate-500 hover:text-white hover:bg-slate-800/50 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                  >
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Activity Log */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-white flex items-center gap-2">
            <Activity className="w-5 h-5 text-purple-400" />
            Recent Activity
          </h2>

          <div className="rounded-2xl border border-slate-800/50 bg-slate-900/30 backdrop-blur-xl divide-y divide-slate-800/30">
            {stats?.recent_activity.map((log) => (
              <div key={log.id} className="px-4 py-3 hover:bg-slate-800/20 transition-colors">
                <div className="flex items-start gap-3">
                  <div className="mt-0.5">
                    <Clock className={`w-3.5 h-3.5 ${ACTION_COLORS[log.action] || "text-slate-500"}`} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-xs font-medium text-white">{formatAction(log.action)}</div>
                    {log.details && <div className="text-[10px] text-slate-500 truncate mt-0.5">{log.details}</div>}
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-[10px] text-slate-600">{formatDate(log.created_at)}</span>
                      {log.ip_address && <span className="text-[10px] text-slate-600">· {log.ip_address}</span>}
                    </div>
                  </div>
                </div>
              </div>
            ))}
            {(!stats || stats.recent_activity.length === 0) && (
              <div className="px-4 py-8 text-center text-slate-500 text-xs">No activity yet</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}


function StatCard({ icon: Icon, label, value, sub, color }: {
  icon: any;
  label: string;
  value: number;
  sub: string;
  color: string;
}) {
  const colorMap: Record<string, string> = {
    purple: "from-purple-500/10 to-purple-600/5 border-purple-500/15",
    red: "from-red-500/10 to-red-600/5 border-red-500/15",
    orange: "from-orange-500/10 to-orange-600/5 border-orange-500/15",
    cyan: "from-cyan-500/10 to-cyan-600/5 border-cyan-500/15",
  };
  const iconColor: Record<string, string> = {
    purple: "text-purple-400",
    red: "text-red-400",
    orange: "text-orange-400",
    cyan: "text-cyan-400",
  };
  return (
    <div className={`p-4 rounded-2xl bg-gradient-to-br ${colorMap[color]} border backdrop-blur-xl`}>
      <div className="flex items-center justify-between mb-3">
        <Icon className={`w-5 h-5 ${iconColor[color]}`} />
      </div>
      <div className="text-2xl font-bold text-white">{value.toLocaleString()}</div>
      <div className="text-xs text-slate-400 mt-1">{label}</div>
      <div className="text-[10px] text-slate-500 mt-0.5">{sub}</div>
    </div>
  );
}
