"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api";

export default function AchievementsPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAchievements();
  }, []);

  const loadAchievements = async () => {
    try {
      const result = await api.get<any>("/api/achievements");
      setData(result);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const checkAchievements = async () => {
    try {
      const result = await api.post<any>("/api/achievements/check");
      if (result.newly_unlocked?.length > 0) {
        alert(`🎉 Unlocked: ${result.newly_unlocked.map((a: any) => a.name).join(", ")}`);
        loadAchievements();
      } else {
        alert("No new achievements unlocked yet. Keep practicing!");
      }
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) {
    return <div className="p-8 flex justify-center"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div></div>;
  }

  const gamification = data?.gamification;
  const achievements = data?.achievements || [];
  const unlocked = achievements.filter((a: any) => a.unlocked);
  const locked = achievements.filter((a: any) => !a.unlocked);

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Achievements</h1>
      <p className="text-gray-600 mb-8">Track your milestones and earn rewards</p>

      {/* Gamification Card */}
      {gamification && (
        <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-2xl p-6 text-white mb-8">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm text-purple-200">Level {gamification.level}</div>
              <div className="text-2xl font-bold mt-1">{gamification.title}</div>
              <div className="text-purple-200 text-sm mt-1">{gamification.total_xp} XP</div>
            </div>
            <div className="text-right">
              <div className="text-5xl">🏆</div>
              <div className="text-sm text-purple-200 mt-2">{unlocked.length}/{achievements.length} unlocked</div>
            </div>
          </div>
          {/* XP Progress Bar */}
          <div className="mt-4 bg-white/20 rounded-full h-2">
            <div className="bg-white rounded-full h-2 transition-all" style={{ width: `${Math.min((gamification.total_xp % 500) / 5, 100)}%` }}></div>
          </div>
          <div className="text-xs text-purple-200 mt-1">{500 - (gamification.total_xp % 500)} XP to next level</div>
        </div>
      )}

      <button
        onClick={checkAchievements}
        className="mb-8 bg-purple-50 text-purple-600 px-4 py-2 rounded-lg text-sm font-medium hover:bg-purple-100"
      >
        Check for New Achievements
      </button>

      {/* Unlocked */}
      {unlocked.length > 0 && (
        <div className="mb-8">
          <h2 className="font-semibold text-gray-900 mb-4">✅ Unlocked ({unlocked.length})</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {unlocked.map((a: any) => (
              <div key={a.id} className="bg-white rounded-xl border border-green-200 p-4 flex items-center gap-4">
                <div className="text-3xl">{a.icon || "🏅"}</div>
                <div>
                  <div className="font-semibold text-gray-900">{a.name}</div>
                  <div className="text-sm text-gray-600">{a.description}</div>
                  <div className="text-xs text-green-600 mt-1">+{a.xp_reward} XP</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Locked */}
      {locked.length > 0 && (
        <div>
          <h2 className="font-semibold text-gray-900 mb-4">🔒 Locked ({locked.length})</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {locked.map((a: any) => (
              <div key={a.id} className="bg-gray-50 rounded-xl border border-gray-200 p-4 flex items-center gap-4 opacity-60">
                <div className="text-3xl grayscale">{a.icon || "🏅"}</div>
                <div>
                  <div className="font-semibold text-gray-700">{a.name}</div>
                  <div className="text-sm text-gray-500">{a.description}</div>
                  <div className="text-xs text-gray-400 mt-1">+{a.xp_reward} XP</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
