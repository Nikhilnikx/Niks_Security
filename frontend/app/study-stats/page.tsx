"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api";

export default function StudyStatsPage() {
  const [stats, setStats] = useState<any>(null);
  const [trends, setTrends] = useState<any>(null);
  const [streak, setStreak] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAll();
  }, []);

  const loadAll = async () => {
    try {
      const [s, t, st] = await Promise.all([
        api.get<any>("/api/activity/statistics"),
        api.get<any>("/api/activity/trends"),
        api.get<any>("/api/activity/streak"),
      ]);
      setStats(s);
      setTrends(t);
      setStreak(st);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-8 flex justify-center"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div></div>;
  }

  const dayNames = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-8">Study Statistics</h1>

      {/* Streak */}
      {streak && (
        <div className="bg-white rounded-2xl p-6 border border-gray-100 mb-8">
          <div className="flex items-center gap-6">
            <div className="text-center">
              <div className="text-4xl">🔥</div>
              <div className="text-3xl font-bold text-orange-600 mt-2">{streak.current_streak}</div>
              <div className="text-sm text-gray-600">Day Streak</div>
            </div>
            <div className="flex-1">
              <div className="text-sm text-gray-600 mb-2">This Week</div>
              <div className="flex gap-2">
                {dayNames.map((day, i) => {
                  const date = new Date();
                  date.setDate(date.getDate() - date.getDay() + i);
                  const dateStr = date.toISOString().split("T")[0];
                  const active = streak.weekly_activity?.[dateStr];
                  return (
                    <div key={day} className="text-center">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium ${
                        active ? "bg-green-500 text-white" : "bg-gray-100 text-gray-400"
                      }`}>
                        {active ? "✓" : day.charAt(0)}
                      </div>
                      <div className="text-xs text-gray-500 mt-1">{day}</div>
                    </div>
                  );
                })}
              </div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-gray-900">{streak.longest_streak}</div>
              <div className="text-xs text-gray-600">Best Streak</div>
            </div>
          </div>
        </div>
      )}

      {/* This Week Stats */}
      {stats && (
        <div className="grid grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
          <div className="bg-white rounded-xl p-5 border border-gray-100">
            <div className="text-sm text-gray-600">Study Time</div>
            <div className="text-2xl font-bold text-blue-600 mt-1">
              {Math.floor(stats.this_week?.study_minutes / 60)}h {Math.round(stats.this_week?.study_minutes % 60)}m
            </div>
          </div>
          <div className="bg-white rounded-xl p-5 border border-gray-100">
            <div className="text-sm text-gray-600">Questions</div>
            <div className="text-2xl font-bold text-gray-900 mt-1">{stats.this_week?.questions_attempted}</div>
          </div>
          <div className="bg-white rounded-xl p-5 border border-gray-100">
            <div className="text-sm text-gray-600">Accuracy</div>
            <div className="text-2xl font-bold text-green-600 mt-1">{stats.this_week?.accuracy}%</div>
          </div>
          <div className="bg-white rounded-xl p-5 border border-gray-100">
            <div className="text-sm text-gray-600">Quizzes</div>
            <div className="text-2xl font-bold text-purple-600 mt-1">{stats.this_week?.quizzes_completed}</div>
          </div>
          <div className="bg-white rounded-xl p-5 border border-gray-100">
            <div className="text-sm text-gray-600">Mock Exams</div>
            <div className="text-2xl font-bold text-orange-600 mt-1">{stats.this_week?.mock_exams_completed}</div>
          </div>
        </div>
      )}

      {/* Performance Trends */}
      {trends && (
        <div className="space-y-6">
          {/* Quiz Trends */}
          {trends.quiz_trends?.length > 0 && (
            <div className="bg-white rounded-xl p-6 border border-gray-100">
              <h2 className="font-semibold text-gray-900 mb-4">Quiz Score Trends</h2>
              <div className="flex items-end gap-2 h-40">
                {trends.quiz_trends.map((q: any, i: number) => (
                  <div key={i} className="flex-1 flex flex-col items-center">
                    <div className="text-xs text-gray-600 mb-1">{q.score}%</div>
                    <div
                      className={`w-full rounded-t ${q.score >= 70 ? "bg-green-400" : "bg-orange-400"}`}
                      style={{ height: `${q.score}%` }}
                    ></div>
                    <div className="text-xs text-gray-400 mt-1">{q.date?.split("T")[0]?.slice(5)}</div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Daily Activity */}
          {trends.daily_trends?.length > 0 && (
            <div className="bg-white rounded-xl p-6 border border-gray-100">
              <h2 className="font-semibold text-gray-900 mb-4">Daily Questions (Last 14 Days)</h2>
              <div className="flex items-end gap-1 h-32">
                {trends.daily_trends.map((d: any, i: number) => {
                  const maxQ = Math.max(...trends.daily_trends.map((t: any) => t.questions), 1);
                  return (
                    <div key={i} className="flex-1 flex flex-col items-center">
                      <div
                        className="w-full bg-purple-400 rounded-t"
                        style={{ height: `${(d.questions / maxQ) * 100}%`, minHeight: d.questions > 0 ? "4px" : "0" }}
                      ></div>
                      <div className="text-xs text-gray-400 mt-1">{d.date?.slice(8)}</div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Mock Exam Trends */}
          {trends.mock_trends?.length > 0 && (
            <div className="bg-white rounded-xl p-6 border border-gray-100">
              <h2 className="font-semibold text-gray-900 mb-4">Mock Exam Scores</h2>
              <div className="space-y-2">
                {trends.mock_trends.map((m: any, i: number) => (
                  <div key={i} className="flex items-center gap-3">
                    <div className="w-20 text-sm text-gray-600">Mock {i + 1}</div>
                    <div className="flex-1 bg-gray-100 rounded-full h-4">
                      <div
                        className={`h-4 rounded-full ${m.score >= 70 ? "bg-green-500" : "bg-orange-500"}`}
                        style={{ width: `${m.score}%` }}
                      ></div>
                    </div>
                    <div className="w-12 text-sm font-medium text-right">{m.score}%</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
