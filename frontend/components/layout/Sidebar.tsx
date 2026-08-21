"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useAuthStore } from "@/lib/store";
import { useEffect, useState } from "react";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: "🏠" },
  { href: "/careers", label: "Career Paths", icon: "🚀" },
  { href: "/certifications", label: "Certifications", icon: "📋" },
  { href: "/practice", label: "Practice", icon: "🎯" },
  { href: "/mock-exams", label: "Mock Exams", icon: "📝" },
  { href: "/flashcards", label: "Flashcards", icon: "🃏" },
  { href: "/ai-tutor", label: "AI Tutor", icon: "🤖", badge: "New" },
  { href: "/bookmarks", label: "Saved", icon: "🔖" },
  { href: "/study-stats", label: "Statistics", icon: "📊" },
  { href: "/achievements", label: "Achievements", icon: "🏆" },
  { href: "/premium", label: "Upgrade to Pro", icon: "⭐" },
];

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuthStore();
  const [collapsed, setCollapsed] = useState(false);

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  return (
    <aside className={`${collapsed ? "w-16" : "w-64"} bg-gray-900 text-white min-h-screen flex flex-col transition-all duration-300`}>
      {/* Logo */}
      <div className="p-4 flex items-center justify-between">
        {!collapsed && (
          <Link href="/dashboard" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-purple-600 rounded-lg flex items-center justify-center font-bold text-lg">N</div>
            <span className="text-xl font-bold">Niksmind</span>
          </Link>
        )}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="text-gray-400 hover:text-white p-1"
        >
          {collapsed ? "→" : "←"}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-2 py-4 space-y-1">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
              pathname === item.href
                ? "bg-purple-600 text-white"
                : "text-gray-400 hover:text-white hover:bg-gray-800"
            }`}
          >
            <span className="text-lg">{item.icon}</span>
            {!collapsed && (
              <>
                <span>{item.label}</span>
                {item.badge && (
                  <span className="bg-purple-500 text-white text-xs px-2 py-0.5 rounded-full">{item.badge}</span>
                )}
              </>
            )}
          </Link>
        ))}
      </nav>

      {/* User */}
      <div className="p-4 border-t border-gray-800">
        {!collapsed ? (
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3 min-w-0">
              <div className="w-8 h-8 bg-purple-600 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0">
                {user?.name?.charAt(0) || "U"}
              </div>
              <div className="min-w-0">
                <div className="text-sm font-medium truncate">{user?.name}</div>
                <div className="text-xs text-gray-400 truncate">{user?.email}</div>
              </div>
            </div>
            <button onClick={handleLogout} className="text-gray-400 hover:text-red-400 text-sm" title="Logout">
              ⏻
            </button>
          </div>
        ) : (
          <button onClick={handleLogout} className="text-gray-400 hover:text-red-400 w-full text-center" title="Logout">
            ⏻
          </button>
        )}
      </div>
    </aside>
  );
}
