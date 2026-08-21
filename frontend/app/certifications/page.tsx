"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import dynamic from "next/dynamic";

const Antigravity = dynamic(() => import("@/components/animations/Antigravity"), {
  ssr: false,
  loading: () => <div className="absolute inset-0 bg-gradient-to-br from-purple-50 to-blue-50"></div>,
});

interface Cert {
  id: number;
  name: string;
  slug: string;
  code: string;
  level: string;
  category: string;
  estimated_hours?: number;
  provider_name?: string;
}

export default function CertificationsPage() {
  const [certs, setCerts] = useState<Cert[]>([]);
  const [loading, setLoading] = useState(true);
  const [providerFilter, setProviderFilter] = useState("all");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [levelFilter, setLevelFilter] = useState("all");

  useEffect(() => {
    loadCertifications();
  }, []);

  const loadCertifications = async () => {
    try {
      const data = await api.get<Cert[]>("/api/certifications");
      setCerts(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const filtered = certs.filter((c) => {
    if (providerFilter !== "all" && !c.code.toLowerCase().includes(providerFilter)) return false;
    if (categoryFilter !== "all" && c.category !== categoryFilter) return false;
    if (levelFilter !== "all" && c.level !== levelFilter) return false;
    return true;
  });

  const certCards = [
    { name: "AZ-900", title: "Azure Fundamentals", provider: "Microsoft", level: "beginner", category: "cloud", color: "#00a4ef", hours: 20, questions: 342 },
    { name: "AWS Cloud Practitioner", title: "AWS Cloud Practitioner", provider: "AWS", level: "beginner", category: "cloud", color: "#ff9900", hours: 25, questions: 150 },
    { name: "CCNA", title: "CCNA 200-301 Associate", provider: "Cisco", level: "associate", category: "networking", color: "#049fd9", hours: 40, questions: 200 },
    { name: "Security+", title: "CompTIA Security+ SY0-701", provider: "CompTIA", level: "associate", category: "security", color: "#e42527", hours: 35, questions: 180 },
  ];

  return (
    <div className="min-h-screen relative">
      {/* Antigravity Background */}
      <div className="absolute inset-0 z-0">
        <Antigravity
          count={400}
          magnetRadius={10}
          ringRadius={6}
          waveSpeed={3.0}
          waveAmplitude={1.5}
          particleSize={0.5}
          lerpSpeed={0.06}
          color="#7c3aed"
          autoAnimate={true}
          particleVariance={0.6}
          rotationSpeed={0.03}
          depthFactor={0.8}
          pulseSpeed={3.2}
          particleShape="sphere"
          fieldStrength={14}
        />
      </div>
      {/* Gradient overlay for readability */}
      <div className="absolute inset-0 bg-gradient-to-b from-white/85 via-white/75 to-white/90 z-10"></div>

      <div className="relative z-20 p-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Explore Certifications</h1>
          <p className="text-gray-600 mt-1">Find and prepare for your next certification</p>
        </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-8">
        <select
          value={providerFilter}
          onChange={(e) => setProviderFilter(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
        >
          <option value="all">All Providers</option>
          <option value="az">Microsoft</option>
          <option value="aws">AWS</option>
          <option value="200">Cisco</option>
          <option value="sy">CompTIA</option>
        </select>

        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
        >
          <option value="all">All Categories</option>
          <option value="cloud">Cloud</option>
          <option value="networking">Networking</option>
          <option value="security">Security</option>
          <option value="ai">AI</option>
          <option value="devops">DevOps</option>
        </select>

        <select
          value={levelFilter}
          onChange={(e) => setLevelFilter(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500"
        >
          <option value="all">All Levels</option>
          <option value="beginner">Beginner</option>
          <option value="associate">Associate</option>
          <option value="professional">Professional</option>
          <option value="specialty">Specialty</option>
        </select>
      </div>

      {/* Certification Cards */}
      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="animate-pulse bg-white rounded-xl p-6 border border-gray-100 h-64"></div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {certCards.map((cert) => (
            <div key={cert.name} className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden hover:shadow-md transition-shadow">
              <div className="h-2" style={{ backgroundColor: cert.color }}></div>
              <div className="p-6">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-xs font-medium px-2 py-0.5 rounded-full" style={{ backgroundColor: cert.color + "20", color: cert.color }}>
                    {cert.provider}
                  </span>
                </div>
                <h3 className="font-bold text-lg text-gray-900">{cert.name}</h3>
                <p className="text-sm text-gray-600 mt-1">{cert.title}</p>
                <div className="flex items-center gap-3 mt-4 text-xs text-gray-500">
                  <span className="capitalize px-2 py-0.5 bg-gray-100 rounded-full">{cert.level}</span>
                  <span>📚 {cert.questions} Questions</span>
                  <span>⏱ {cert.hours} Hours</span>
                </div>
                <Link
                  href={`/certifications/${cert.name.toLowerCase().replace(/\s+/g, "-").replace("+-", "-plus").replace("ccna", "ccna")}`}
                  className="mt-4 block text-center bg-purple-600 text-white py-2.5 rounded-lg text-sm font-semibold hover:bg-purple-700 transition-colors"
                >
                  Start Preparing →
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
      </div>
    </div>
  );
}
