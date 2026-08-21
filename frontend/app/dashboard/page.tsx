"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { useAuthStore } from "@/lib/store";
import NotificationCenter from "@/components/layout/NotificationCenter";
import CountUp from "@/components/animations/CountUp";

interface DashboardData {
  total_questions_attempted: number;
  total_correct: number;
  accuracy: number;
  certifications_count: number;
  recent_quizzes: any[];
  recent_mock_exams: any[];
}

export default function DashboardPage() {
  const { user } = useAuthStore();
  const [data, setData] = useState<DashboardData | null>(null);
  const [streak, setStreak] = useState<any>(null);
  const [stats, setStats] = useState<any>(null);
  const [careerGoal, setCareerGoal] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const [dash, st, act, goal] = await Promise.all([
        api.get<DashboardData>("/api/dashboard").catch(() => null),
        api.get<any>("/api/activity/streak").catch(() => null),
        api.get<any>("/api/activity/statistics").catch(() => null),
        api.get<any>("/api/careers/goal/me").catch(() => null),
      ]);
      setData(dash);
      setStreak(st);
      setStats(act);
      setCareerGoal(goal?.goal);
    } catch (err) {
      console.error("Failed to load dashboard:", err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-8">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-200 rounded w-64"></div>
          <div className="grid grid-cols-4 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-24 bg-gray-200 rounded-xl"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  const hour = new Date().getHours();
  const greeting = hour < 12 ? "Good morning" : hour < 17 ? "Good afternoon" : "Good evening";

  return (
    <div className="p-8">
      {/* Header with greeting and notifications */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            {greeting}, {user?.name?.split(" ")[0]}! 👋
          </h1>
          <p className="text-gray-600 mt-1">Continue your certification preparation journey.</p>
        </div>
        <NotificationCenter />
      </div>

      {/* Career Goal + Exam Countdown */}
      {careerGoal && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-8">
          <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl p-5 text-white">
            <div className="text-sm text-purple-200">Your Career Goal</div>
            <div className="text-lg font-bold mt-1">{careerGoal.career_path?.name || "Not set"}</div>
            {careerGoal.target_role && <div className="text-purple-200 text-sm mt-1">Target: {careerGoal.target_role}</div>}
          </div>
          {careerGoal.target_date && (() => {
            const daysLeft = Math.max(0, Math.ceil((new Date(careerGoal.target_date).getTime() - Date.now()) / (1000 * 60 * 60 * 24)));
            return (
              <div className={`rounded-xl p-5 text-center ${daysLeft <= 7 ? "bg-red-50 border border-red-200" : "bg-white border border-gray-100"}`}>
                <div className="text-sm text-gray-600">Exam Countdown</div>
                <div className={`text-3xl font-bold mt-1 ${daysLeft <= 7 ? "text-red-600" : "text-gray-900"}`}>
                  {daysLeft} <span className="text-base font-normal">days left</span>
                </div>
              </div>
            );
          })()}
          {streak && (
            <div className="bg-white rounded-xl p-5 border border-gray-100 text-center">
              <div className="text-sm text-gray-600">Study Streak</div>
              <div className="text-3xl font-bold text-orange-500 mt-1">🔥 {streak.current_streak} <span className="text-base font-normal">days</span></div>
              <div className="text-xs text-gray-500 mt-1">Best: {streak.longest_streak} days</div>
            </div>
          )}
        </div>
      )}

      {/* Stats with animated counters */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="bg-green-50 rounded-xl p-5 border border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Questions Solved</p>
              <p className="text-2xl font-bold text-green-600 mt-1">
                <CountUp to={data?.total_questions_attempted || 0} duration={1.5} />
              </p>
            </div>
            <div className="text-2xl">✅</div>
          </div>
        </div>
        <div className="bg-blue-50 rounded-xl p-5 border border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Accuracy</p>
              <p className="text-2xl font-bold text-blue-600 mt-1">
                <CountUp to={data?.accuracy || 0} duration={1.5} suffix="%" />
              </p>
            </div>
            <div className="text-2xl">🎯</div>
          </div>
        </div>
        <div className="bg-purple-50 rounded-xl p-5 border border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Certifications</p>
              <p className="text-2xl font-bold text-purple-600 mt-1">
                <CountUp to={data?.certifications_count || 0} duration={1.5} />
              </p>
            </div>
            <div className="text-2xl">📋</div>
          </div>
        </div>
        <div className="bg-orange-50 rounded-xl p-5 border border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Mock Exams</p>
              <p className="text-2xl font-bold text-orange-600 mt-1">
                <CountUp to={data?.recent_mock_exams?.length || 0} duration={1.5} />
              </p>
            </div>
            <div className="text-2xl">📝</div>
          </div>
        </div>
      </div>

      {/* Today's Study Plan */}
      {stats && (
        <div className="bg-white rounded-xl p-6 border border-gray-100 shadow-sm mb-8">
          <h2 className="font-semibold text-gray-900 mb-4">📊 This Week&apos;s Progress</h2>
          <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
            <div className="text-center">
              <div className="text-lg font-bold text-blue-600">
                {Math.floor((stats.this_week?.study_minutes || 0) / 60)}h {Math.round((stats.this_week?.study_minutes || 0) % 60)}m
              </div>
              <div className="text-xs text-gray-600">Study Time</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-bold text-gray-900">{stats.this_week?.questions_attempted || 0}</div>
              <div className="text-xs text-gray-600">Questions</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-bold text-green-600">{stats.this_week?.accuracy || 0}%</div>
              <div className="text-xs text-gray-600">Accuracy</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-bold text-purple-600">{stats.this_week?.quizzes_completed || 0}</div>
              <div className="text-xs text-gray-600">Quizzes</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-bold text-orange-600">{stats.this_week?.mock_exams_completed || 0}</div>
              <div className="text-xs text-gray-600">Mock Exams</div>
            </div>
          </div>
        </div>
      )}

      {/* Quick Actions + Certifications */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-xl p-6 border border-gray-100 shadow-sm">
          <h2 className="font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-2 gap-3">
            <Link href="/certifications" className="flex items-center gap-3 p-3 rounded-lg border border-gray-200 hover:border-purple-300 hover:bg-purple-50 transition-colors">
              <span className="text-xl">📋</span>
              <span className="text-sm font-medium">Browse Certifications</span>
            </Link>
            <Link href="/practice" className="flex items-center gap-3 p-3 rounded-lg border border-gray-200 hover:border-purple-300 hover:bg-purple-50 transition-colors">
              <span className="text-xl">🎯</span>
              <span className="text-sm font-medium">Quick Practice</span>
            </Link>
            <Link href="/mock-exams" className="flex items-center gap-3 p-3 rounded-lg border border-gray-200 hover:border-purple-300 hover:bg-purple-50 transition-colors">
              <span className="text-xl">📝</span>
              <span className="text-sm font-medium">Mock Exam</span>
            </Link>
            <Link href="/ai-tutor" className="flex items-center gap-3 p-3 rounded-lg border border-gray-200 hover:border-purple-300 hover:bg-purple-50 transition-colors">
              <span className="text-xl">🤖</span>
              <span className="text-sm font-medium">Ask AI Tutor</span>
            </Link>
          </div>
        </div>

        <div className="bg-white rounded-xl p-6 border border-gray-100 shadow-sm">
          <h2 className="font-semibold text-gray-900 mb-4">Popular Certifications</h2>
          <div className="space-y-3">
            {[
              { name: "AZ-900", title: "Azure Fundamentals", level: "Beginner", color: "#00a4ef", slug: "az-900" },
              { name: "AWS Cloud Practitioner", title: "AWS Cloud Practitioner", level: "Beginner", color: "#ff9900", slug: "aws-cloud-practitioner" },
              { name: "CCNA", title: "CCNA 200-301 Associate", level: "Associate", color: "#049fd9", slug: "ccna" },
              { name: "Security+", title: "CompTIA Security+ SY0-701", level: "Associate", color: "#e42527", slug: "security-plus" },
            ].map((cert) => (
              <Link
                key={cert.name}
                href={`/certifications/${cert.slug}`}
                className="flex items-center justify-between p-3 rounded-lg border border-gray-200 hover:border-purple-300 hover:bg-purple-50 transition-colors"
              >
                <div>
                  <div className="font-medium text-sm" style={{ color: cert.color }}>{cert.name}</div>
                  <div className="text-xs text-gray-500">{cert.title}</div>
                </div>
                <span className="text-xs bg-gray-100 px-2 py-1 rounded-full text-gray-600">{cert.level}</span>
              </Link>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      {data?.recent_quizzes && data.recent_quizzes.length > 0 && (
        <div className="bg-white rounded-xl p-6 border border-gray-100 shadow-sm">
          <h2 className="font-semibold text-gray-900 mb-4">Recent Quizzes</h2>
          <div className="space-y-3">
            {data.recent_quizzes.map((quiz: any) => (
              <div key={quiz.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <div className="font-medium text-sm">{quiz.quiz_type} Quiz</div>
                  <div className="text-xs text-gray-500">
                    {quiz.correct_answers}/{quiz.total_questions} correct
                  </div>
                </div>
                <div className={`text-lg font-bold ${quiz.score >= 70 ? "text-green-600" : "text-orange-600"}`}>
                  {quiz.score}%
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {(!data?.total_questions_attempted || data.total_questions_attempted === 0) && (
        <div className="bg-white rounded-xl p-8 border border-gray-100 shadow-sm text-center">
          <div className="text-4xl mb-4">🚀</div>
          <h3 className="font-semibold text-gray-900 mb-2">Start Your Journey</h3>
          <p className="text-gray-600 mb-6 max-w-md mx-auto">
            Begin by selecting a certification and taking your first practice quiz.
          </p>
          <div className="flex justify-center gap-4">
            <Link
              href="/careers"
              className="bg-purple-600 text-white px-6 py-2.5 rounded-lg font-semibold hover:bg-purple-700 transition-colors"
            >
              Choose a Career Path
            </Link>
            <Link
              href="/certifications"
              className="border border-gray-300 text-gray-700 px-6 py-2.5 rounded-lg font-semibold hover:bg-gray-50 transition-colors"
            >
              Browse Certifications
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
