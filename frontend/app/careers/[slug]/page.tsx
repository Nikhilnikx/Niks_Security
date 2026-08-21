"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";

export default function CareerRoadmapPage() {
  const { slug } = useParams();
  const [career, setCareer] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (slug) loadCareer();
  }, [slug]);

  const loadCareer = async () => {
    try {
      const data = await api.get<any>(`/api/careers/${slug}`);
      setCareer(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-8 flex justify-center"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div></div>;
  }

  if (!career) {
    return <div className="p-8 text-center text-gray-500">Career path not found</div>;
  }

  const stageColors: Record<string, string> = {
    foundation: "bg-green-100 text-green-700 border-green-200",
    intermediate: "bg-blue-100 text-blue-700 border-blue-200",
    advanced: "bg-purple-100 text-purple-700 border-purple-200",
    specialty: "bg-orange-100 text-orange-700 border-orange-200",
  };

  // Group by stage
  const stages: Record<string, any[]> = {};
  career.roadmap?.forEach((item: any) => {
    if (!stages[item.stage]) stages[item.stage] = [];
    stages[item.stage].push(item);
  });

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="mb-8">
        <Link href="/careers" className="text-sm text-purple-600 hover:underline">← Back to Careers</Link>
        <h1 className="text-3xl font-bold text-gray-900 mt-2">{career.name}</h1>
        <p className="text-gray-600 mt-2">{career.description}</p>
      </div>

      {/* Roadmap */}
      <div className="relative">
        {/* Vertical line */}
        <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200"></div>

        {Object.entries(stages).map(([stage, items], stageIdx) => (
          <div key={stage} className="mb-8 relative">
            <div className="flex items-center gap-3 mb-4">
              <div className={`w-8 h-8 rounded-full border-2 flex items-center justify-center text-sm font-bold z-10 ${stageColors[stage] || "bg-gray-100 text-gray-600"}`}>
                {stageIdx + 1}
              </div>
              <h2 className="text-lg font-bold text-gray-900 capitalize">{stage}</h2>
            </div>

            <div className="ml-12 space-y-3">
              {items.map((item: any, idx: number) => (
                <div key={idx} className={`bg-white rounded-xl border p-4 ${item.required ? "border-red-200" : "border-gray-100"}`}>
                  <div className="flex items-center justify-between">
                    <div>
                      {item.certification ? (
                        <Link
                          href={`/certifications/${item.certification.slug || item.certification.code?.toLowerCase()}`}
                          className="font-semibold text-purple-600 hover:underline"
                        >
                          {item.certification.code} — {item.certification.name}
                        </Link>
                      ) : (
                        <span className="font-semibold text-gray-400">Coming soon</span>
                      )}
                      {item.description && <p className="text-sm text-gray-600 mt-1">{item.description}</p>}
                    </div>
                    <div className="flex items-center gap-2">
                      {item.required && <span className="text-xs bg-red-50 text-red-600 px-2 py-0.5 rounded">Required</span>}
                      {item.certification?.level && (
                        <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded capitalize">{item.certification.level}</span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
