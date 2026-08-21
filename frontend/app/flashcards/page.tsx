"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api";

export default function FlashcardsPage() {
  const [cards, setCards] = useState<any[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [loading, setLoading] = useState(true);
  const [newFront, setNewFront] = useState("");
  const [newBack, setNewBack] = useState("");
  const [showCreate, setShowCreate] = useState(false);

  useEffect(() => {
    loadFlashcards();
  }, []);

  const loadFlashcards = async () => {
    try {
      const data = await api.get<any>("/api/flashcards/review?limit=50");
      setCards(data.flashcards || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const reviewCard = async (confidence: number) => {
    const card = cards[currentIndex];
    if (!card) return;

    try {
      await api.post("/api/flashcards/review", {
        flashcard_id: card.id,
        confidence,
      });
      setFlipped(false);
      setCurrentIndex((i) => (i + 1) % cards.length);
    } catch (err) {
      console.error(err);
    }
  };

  const createCard = async () => {
    if (!newFront || !newBack) return;
    try {
      await api.post("/api/flashcards", { front: newFront, back: newBack });
      setNewFront("");
      setNewBack("");
      setShowCreate(false);
      loadFlashcards();
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-2xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Flashcards</h1>
          <p className="text-gray-600 mt-1">Review with spaced repetition</p>
        </div>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="bg-purple-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-purple-700"
        >
          + Create Card
        </button>
      </div>

      {showCreate && (
        <div className="bg-white rounded-xl border border-gray-100 p-6 mb-6">
          <h3 className="font-semibold text-gray-900 mb-4">Create Flashcard</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Front (Question)</label>
              <textarea
                value={newFront}
                onChange={(e) => setNewFront(e.target.value)}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm"
                rows={2}
                placeholder="What is cloud computing?"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Back (Answer)</label>
              <textarea
                value={newBack}
                onChange={(e) => setNewBack(e.target.value)}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm"
                rows={2}
                placeholder="The delivery of computing services over the internet..."
              />
            </div>
            <button onClick={createCard} className="bg-purple-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-purple-700">
              Create
            </button>
          </div>
        </div>
      )}

      {cards.length === 0 ? (
        <div className="bg-white rounded-xl border border-gray-100 p-12 text-center">
          <div className="text-4xl mb-4">🃏</div>
          <h3 className="font-semibold text-gray-900 mb-2">No Flashcards Yet</h3>
          <p className="text-gray-600 text-sm">Complete a quiz or create your first flashcard to get started.</p>
        </div>
      ) : (
        <>
          {/* Card Counter */}
          <div className="text-center text-sm text-gray-600 mb-4">
            Card {currentIndex + 1} of {cards.length}
          </div>

          {/* Flashcard */}
          <div
            className="bg-white rounded-2xl shadow-lg border border-gray-100 p-8 min-h-[250px] flex items-center justify-center cursor-pointer mb-6 transition-all hover:shadow-xl"
            onClick={() => setFlipped(!flipped)}
          >
            <div className="text-center">
              <div className="text-xs text-gray-400 mb-4">{flipped ? "BACK" : "FRONT"}</div>
              <p className="text-lg font-medium text-gray-900">
                {flipped ? cards[currentIndex]?.back : cards[currentIndex]?.front}
              </p>
              <div className="text-xs text-gray-400 mt-4">Click to flip</div>
            </div>
          </div>

          {/* Confidence buttons */}
          {flipped && (
            <div className="grid grid-cols-4 gap-3 mb-6">
              <button onClick={() => reviewCard(0.2)} className="bg-red-50 text-red-700 py-3 rounded-lg text-sm font-medium hover:bg-red-100 border border-red-200">
                😟 Again
              </button>
              <button onClick={() => reviewCard(0.5)} className="bg-orange-50 text-orange-700 py-3 rounded-lg text-sm font-medium hover:bg-orange-100 border border-orange-200">
                🤔 Hard
              </button>
              <button onClick={() => reviewCard(0.8)} className="bg-green-50 text-green-700 py-3 rounded-lg text-sm font-medium hover:bg-green-100 border border-green-200">
                😊 Good
              </button>
              <button onClick={() => reviewCard(1.0)} className="bg-blue-50 text-blue-700 py-3 rounded-lg text-sm font-medium hover:bg-blue-100 border border-blue-200">
                🎯 Easy
              </button>
            </div>
          )}

          {/* Navigation */}
          <div className="flex justify-between">
            <button
              onClick={() => { setFlipped(false); setCurrentIndex((i) => (i - 1 + cards.length) % cards.length); }}
              className="px-4 py-2 border border-gray-300 rounded-lg text-sm hover:bg-gray-50"
            >
              ← Previous
            </button>
            <button
              onClick={() => { setFlipped(false); setCurrentIndex((i) => (i + 1) % cards.length); }}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg text-sm hover:bg-purple-700"
            >
              Next →
            </button>
          </div>
        </>
      )}
    </div>
  );
}
