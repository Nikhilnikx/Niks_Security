"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api";

export default function AdminAnalyticsPage() {
  const [overview, setOverview] = useState<any>(null);
  const [certAnalytics, setCertAnalytics] = useState<any[]>([]);
  const [revenue, setRevenue] = useState<any>(null);
  const [questionHealth, setQuestionHealth] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAll();
  }, []);

  const loadAll = async () => {
    try {
      const [ov, ca, rev, qh] = await Promise.all([
        api.get<any>("/api/admin/analytics/overview"),
        api.get<any>("/api/admin/analytics/certifications"),
        api.get<any>("/api/admin/analytics/revenue"),
        api.get<any>("/api/admin/analytics/questions/health"),
      ]);
      setOverview(ov);
      setCertAnalytics(ca.certifications || []);
      setRevenue(rev);
      setQuestionHealth(qh);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-8 flex justify-center"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div></div>;
  }

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-8">Admin Analytics</h1>

      {/* Overview Cards */}
      {overview && (
        <div className="grid grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
          <div className="bg-white rounded-xl p-5 border border-gray-100">
            <div className="text-sm text-gray-600">Total Users</div>
            <div className="text-2xl font-bold text-gray-900 mt-1">{overview.total_users}</div>
          </div>
          <div className="bg-white rounded-xl p-5 border border-gray-100">
            <div className="text-sm text-gray-600">New This Week</div>
            <div className="text-2xl font-bold text-green-600 mt-1">{overview.new_users_this_week}</div>
          </div>
          <div className="bg-white rounded-xl p-5 border border-gray-100">
            <div className="text-sm text-gray-600">Total Quizzes</div>
            <div className="text-2xl font-bold text-blue-600 mt-1">{overview.total_quizzes}</div>
          </div>
          <div className="bg-white rounded-xl p-5 border border-gray-100">
            <div className="text-sm text-gray-600">Premium Purchases</div>
            <div className="text-2xl font-bold text-purple-600 mt-1">{overview.total_premium_purchases}</div>
          </div>
          <div className="bg-white rounded-xl p-5 border border-gray-100">
            <div className="text-sm text-gray-600">Revenue</div>
            <div className="text-2xl font-bold text-green-600 mt-1">₹{overview.total_revenue}</div>
          </div>
        </div>
      )}

      {/* Revenue */}
      {revenue && (
        <div className="bg-white rounded-xl p-6 border border-gray-100 mb-8">
          <h2 className="font-semibold text-gray-900 mb-4">Revenue</h2>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">₹{revenue.today}</div>
              <div className="text-sm text-gray-600">Today</div>
            </div>
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">₹{revenue.this_week}</div>
              <div className="text-sm text-gray-600">This Week</div>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">₹{revenue.this_month}</div>
              <div className="text-sm text-gray-600">This Month</div>
            </div>
          </div>
        </div>
      )}

      {/* Certification Analytics */}
      <div className="bg-white rounded-xl p-6 border border-gray-100 mb-8">
        <h2 className="font-semibold text-gray-900 mb-4">Certification Analytics</h2>
        {certAnalytics.length === 0 ? (
          <p className="text-gray-500 text-sm">No data yet</p>
        ) : (
          <div className="space-y-3">
            {certAnalytics.map((c) => (
              <div key={c.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <div className="font-medium text-sm">{c.code} — {c.name}</div>
                  <div className="text-xs text-gray-500">{c.quiz_attempts} quiz attempts</div>
                </div>
                <div className="text-right">
                  <div className="font-bold text-sm">{c.average_score}%</div>
                  <div className="text-xs text-gray-500">avg score</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Question Health */}
      {questionHealth && (
        <div className="bg-white rounded-xl p-6 border border-gray-100">
          <h2 className="font-semibold text-gray-900 mb-4">Question Health</h2>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-gray-900">{questionHealth.total_questions}</div>
              <div className="text-sm text-gray-600">Total Questions</div>
            </div>
            <div className="p-4 bg-red-50 rounded-lg">
              <div className="text-2xl font-bold text-red-600">{questionHealth.problematic_count}</div>
              <div className="text-sm text-gray-600">Problematic ({"<"}20% success)</div>
            </div>
          </div>
          {questionHealth.most_difficult?.length > 0 && (
            <div>
              <h3 className="font-medium text-sm text-gray-900 mb-2">Most Difficult Questions</h3>
              <div className="space-y-2">
                {questionHealth.most_difficult.map((q: any) => (
                  <div key={q.id} className="flex items-center justify-between text-sm p-2 bg-gray-50 rounded">
                    <span className="truncate">{q.question_text}</span>
                    <span className="text-red-600 font-medium ml-2">{q.success_rate}%</span>
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
