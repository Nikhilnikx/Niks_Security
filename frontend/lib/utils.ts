import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function apiFetch(path: string, options: RequestInit = {}) {
  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((options.headers as Record<string, string>) || {}),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (res.status === 401 && typeof window !== "undefined") {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    window.location.href = "/login";
    throw new Error("Unauthorized");
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(err.detail || "Request failed");
  }

  return res.json();
}

export function formatRelativeTime(dateStr: string) {
  if (!dateStr) return "N/A";
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  if (diffMins < 1) return "just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  const diffHrs = Math.floor(diffMins / 60);
  if (diffHrs < 24) return `${diffHrs}h ago`;
  const diffDays = Math.floor(diffHrs / 24);
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString();
}

export function severityColor(severity: string) {
  const colors: Record<string, string> = {
    critical: "text-red-400 bg-red-500/10 border-red-500/20",
    high: "text-orange-400 bg-orange-500/10 border-orange-500/20",
    medium: "text-yellow-400 bg-yellow-500/10 border-yellow-500/20",
    low: "text-green-400 bg-green-500/10 border-green-500/20",
    info: "text-blue-400 bg-blue-500/10 border-blue-500/20",
  };
  return colors[severity] || colors.low;
}

export function statusColor(status: string) {
  const colors: Record<string, string> = {
    new: "text-blue-400 bg-blue-500/10",
    acknowledged: "text-yellow-400 bg-yellow-500/10",
    investigating: "text-purple-400 bg-purple-500/10",
    resolved: "text-green-400 bg-green-500/10",
    false_positive: "text-slate-400 bg-slate-500/10",
    open: "text-blue-400 bg-blue-500/10",
  };
  return colors[status] || colors.new;
}
