"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { api } from "@/lib/api";

export default function CareersPage() {
  const [careers, setCareers] = useState<any[]>([]);
  const [selectedCareer, setSelectedCareer] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [goal, setGoal] = useState<any>(null);

  useEffect(() => {
    loadCareers();
    loadGoal();
  }, []);

  const loadCareers = async () => {
    try {
      const data = await api.get<any>("/api/careers/");
      setCareers(data.career_paths || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadGoal = async () => {
    try {
      const data = await api.get<any>("/api/careers/goal/me");
      if (data.goal) setGoal(data.goal);
    } catch (err) {}
  };

  const loadCareerDetail = async (slug: string) => {
    try {
      const data = await api.get<any>(`/api/careers/${slug}`);
      setSelectedCareer(data);
    } catch (err) {
      console.error(err);
    }
  };

  const setCareerGoal = async (careerId: number) => {
    try {
      await api.post("/api/careers/goal", { career_path_id: careerId });
      loadGoal();
    } catch (err) {
      console.error(err);
    }
  };

  const careerIcons: Record<string, string> = {
    "cloud-engineer": "☁️",
    "cloud-security-engineer": "🛡️",
    "cybersecurity-analyst": "🔒",
    "network-engineer": "🌐",
    "devops-engineer": "⚙️",
    "cloud-developer": "💻",
    "data-engineer": "📊",
    "ai-ml-engineer": "🤖",
    "systems-administrator": "🖥️",
    "security-engineer": "🔐",
  };

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Career Paths</h1>
        <p className="text-gray-600 mt-1">Choose your target career and get a personalized certification roadmap</p>
      </div>

      {/* Current Goal */}
      {goal && goal.career_path && (
        <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-2xl p-6 text-white mb-8">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm text-purple-200">Your Career Goal</div>
              <div className="text-xl font-bold mt-1">{goal.career_path.name}</div>
              {goal.target_role && <div className="text-purple-200 text-sm mt-1">Target: {goal.target_role}</div>}
            </div>
            <Link href={`/careers/${goal.career_path.slug}`} className="bg-white text-purple-600 px-6 py-2 rounded-lg font-semibold hover:bg-gray-100">
              View Roadmap →
            </Link>
          </div>
        </div>
      )}

      {/* Career Cards */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <div key={i} className="animate-pulse bg-white rounded-xl h-48 border border-gray-100"></div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {careers.map((career) => (
            <div
              key={career.id}
              className="bg-white rounded-xl border border-gray-100 shadow-sm p-6 hover:shadow-md transition-shadow cursor-pointer"
              onClick={() => loadCareerDetail(career.slug)}
            >
              <div className="text-3xl mb-3">{careerIcons[career.slug] || "🎯"}</div>
              <h3 className="font-bold text-gray-900">{career.name}</h3>
              <p className="text-sm text-gray-600 mt-1 line-clamp-2">{career.description}</p>
              <div className="flex items-center gap-3 mt-4 text-xs text-gray-500">
                <span className="capitalize px-2 py-0.5 bg-gray-100 rounded-full">{career.difficulty}</span>
                {career.estimated_months && <span>⏱ {career.estimated_months} months</span>}
                <span>📋 {career.certifications_count} certs</span>
              </div>
              <button className="mt-4 w-full bg-purple-50 text-purple-600 py-2 rounded-lg text-sm font-semibold hover:bg-purple-100 transition-colors">
                Explore Career →
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Career Detail Modal */}
      {selectedCareer && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4" onClick={() => setSelectedCareer(null)}>
          <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[80vh] overflow-y-auto p-8" onClick={(e) => e.stopPropagation()}>
            <div className="flex justify-between items-start mb-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{selectedCareer.name}</h2>
                <p className="text-gray-600 mt-1">{selectedCareer.description}</p>
              </div>
              <button onClick={() => setSelectedCareer(null)} className="text-gray-400 hover:text-gray-600 text-xl">✕</button>
            </div>

            <div className="flex items-center gap-4 mb-6 text-sm text-gray-600">
              <span className="capitalize px-3 py-1 bg-purple-50 text-purple-600 rounded-full">{selectedCareer.difficulty}</span>
              {selectedCareer.estimated_months && <span>⏱ {selectedCareer.estimated_months} months</span>}
            </div>

            {/* Roadmap */}
            <h3 className="font-semibold text-gray-900 mb-4">Certification Roadmap</h3>
            <div className="space-y-3">
              {selectedCareer.roadmap?.map((item: any, idx: number) => (
                <div key={idx} className="flex items-start gap-4">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0 ${
                    idx === 0 ? "bg-green-100 text-green-600" :
                    idx === 1 ? "bg-blue-100 text-blue-600" :
                    "bg-gray-100 text-gray-600"
                  }`}>
                    {idx + 1}
                  </div>
                  <div className="flex-1">
                    <div className="text-xs text-gray-400 uppercase">{item.stage}</div>
                    <div className="font-medium text-gray-900">
                      {item.certification ? `${item.certification.code} - ${item.certification.name}` : "TBD"}
                    </div>
                    {item.description && <div className="text-sm text-gray-600">{item.description}</div>}
                  </div>
                  {item.required && <span className="text-xs bg-red-50 text-red-600 px-2 py-0.5 rounded">Required</span>}
                </div>
              ))}
            </div>

            <button
              onClick={() => setCareerGoal(selectedCareer.id)}
              className="mt-6 w-full bg-purple-600 text-white py-3 rounded-lg font-semibold hover:bg-purple-700 transition-colors"
            >
              Set as My Career Goal
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
