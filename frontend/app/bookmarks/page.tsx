"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { api } from "@/lib/api";

export default function BookmarksPage() {
  const [bookmarks, setBookmarks] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState("concept");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadBookmarks();
  }, [activeTab]);

  const loadBookmarks = async () => {
    setLoading(true);
    try {
      const data = await api.get<any>(`/api/bookmarks?entity_type=${activeTab}`);
      setBookmarks(data.bookmarks || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const removeBookmark = async (id: number) => {
    try {
      await api.delete(`/api/bookmarks/${id}`);
      setBookmarks((prev) => prev.filter((b) => b.id !== id));
    } catch (err) {
      console.error(err);
    }
  };

  const tabs = [
    { key: "concept", label: "Concepts", icon: "📚" },
    { key: "question", label: "Questions", icon: "❓" },
    { key: "resource", label: "Resources", icon: "🔗" },
    { key: "flashcard", label: "Flashcards", icon: "🃏" },
  ];

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Saved</h1>
      <p className="text-gray-600 mb-6">Your bookmarked items</p>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 bg-gray-100 p-1 rounded-lg w-fit">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === tab.key
                ? "bg-white text-gray-900 shadow-sm"
                : "text-gray-600 hover:text-gray-900"
            }`}
          >
            {tab.icon} {tab.label}
          </button>
        ))}
      </div>

      {/* Bookmarks */}
      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="animate-pulse bg-white rounded-xl h-20 border border-gray-100"></div>
          ))}
        </div>
      ) : bookmarks.length === 0 ? (
        <div className="bg-white rounded-xl border border-gray-100 p-12 text-center">
          <div className="text-4xl mb-4">🔖</div>
          <h3 className="font-semibold text-gray-900 mb-2">No saved items yet</h3>
          <p className="text-gray-600 text-sm">Bookmark concepts, questions, or resources to find them here.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {bookmarks.map((b) => (
            <div key={b.id} className="bg-white rounded-xl border border-gray-100 p-4 flex items-center justify-between">
              <div>
                <div className="text-xs text-gray-400 capitalize">{b.entity_type}</div>
                <div className="font-medium text-gray-900">
                  {b.entity?.name || b.entity?.question_text?.substring(0, 80) || `Item #${b.entity_id}`}
                </div>
                {b.entity?.short_definition && (
                  <div className="text-sm text-gray-600 mt-1">{b.entity.short_definition}</div>
                )}
              </div>
              <div className="flex items-center gap-3">
                {b.entity?.slug && (
                  <Link href={`/certifications/az-900/concepts/${b.entity.slug}`} className="text-sm text-purple-600 hover:underline">
                    View →
                  </Link>
                )}
                <button
                  onClick={() => removeBookmark(b.id)}
                  className="text-gray-400 hover:text-red-500 text-sm"
                >
                  ✕
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
