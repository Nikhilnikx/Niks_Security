"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useAuthStore } from "@/lib/store";

interface QuizState {
  quizId: number | null;
  questions: any[];
  currentIndex: number;
  answers: Record<number, number>;
  results: Record<number, { is_correct: boolean; explanation: string; correct_option_id: number }>;
  completed: boolean;
  score: number;
}

export default function PracticePage() {
  const { user } = useAuthStore();
  const [certifications, setCertifications] = useState<any[]>([]);
  const [selectedCert, setSelectedCert] = useState<number | null>(null);
  const [numQuestions, setNumQuestions] = useState(10);
  const [quiz, setQuiz] = useState<QuizState>({
    quizId: null,
    questions: [],
    currentIndex: 0,
    answers: {},
    results: {},
    completed: false,
    score: 0,
  });
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadCertifications();
  }, []);

  const loadCertifications = async () => {
    try {
      const data = await api.get<any[]>("/api/certifications");
      setCertifications(data);
    } catch (err) {
      console.error(err);
    }
  };

  const startQuiz = async () => {
    if (!selectedCert) return;
    setLoading(true);
    try {
      const data = await api.post<any>("/api/quizzes/start", {
        certification_id: selectedCert,
        quiz_type: "quick",
        num_questions: numQuestions,
      });
      setQuiz({
        quizId: data.id,
        questions: data.questions,
        currentIndex: 0,
        answers: {},
        results: {},
        completed: false,
        score: 0,
      });
    } catch (err: any) {
      alert(err.message || "Failed to start quiz");
    } finally {
      setLoading(false);
    }
  };

  const answerQuestion = async (questionId: number, optionId: number) => {
    if (quiz.results[questionId]) return;

    setSubmitting(true);
    try {
      const data = await api.post<any>(`/api/quizzes/${quiz.quizId}/answer`, {
        question_id: questionId,
        selected_option_id: optionId,
      });

      setQuiz((prev) => ({
        ...prev,
        answers: { ...prev.answers, [questionId]: optionId },
        results: {
          ...prev.results,
          [questionId]: {
            is_correct: data.is_correct,
            explanation: data.explanation,
            correct_option_id: data.correct_option_id,
          },
        },
      }));
    } catch (err: any) {
      alert(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const nextQuestion = () => {
    setQuiz((prev) => ({
      ...prev,
      currentIndex: Math.min(prev.currentIndex + 1, prev.questions.length - 1),
    }));
  };

  const prevQuestion = () => {
    setQuiz((prev) => ({
      ...prev,
      currentIndex: Math.max(prev.currentIndex - 1, 0),
    }));
  };

  const completeQuiz = async () => {
    try {
      const data = await api.post<any>(`/api/quizzes/${quiz.quizId}/complete`);
      setQuiz((prev) => ({ ...prev, completed: true, score: data.score }));
    } catch (err: any) {
      alert(err.message);
    }
  };

  // Results screen
  if (quiz.completed) {
    return (
      <div className="p-8 max-w-4xl mx-auto">
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-8 text-center">
          <div className="text-5xl mb-4">{quiz.score >= 70 ? "🎉" : "📚"}</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Quiz Complete!</h2>
          <div className="text-5xl font-bold text-purple-600 my-4">{quiz.score}%</div>
          <p className="text-gray-600 mb-8">
            You answered {Object.values(quiz.results).filter((r) => r.is_correct).length} out of {quiz.questions.length} correctly.
          </p>

          {/* Question Review */}
          <div className="text-left space-y-4">
            {quiz.questions.map((q: any, idx: number) => {
              const result = quiz.results[q.id];
              if (!result) return null;
              return (
                <div key={q.id} className={`p-4 rounded-lg border ${result.is_correct ? "bg-green-50 border-green-200" : "bg-red-50 border-red-200"}`}>
                  <div className="flex items-start gap-2">
                    <span className="text-lg">{result.is_correct ? "✅" : "❌"}</span>
                    <div className="flex-1">
                      <div className="font-medium text-sm">Q{idx + 1}: {q.question_text}</div>
                      {!result.is_correct && (
                        <div className="text-xs text-gray-600 mt-1">
                          Correct: {q.options.find((o: any) => o.id === result.correct_option_id)?.text}
                        </div>
                      )}
                      <div className="text-xs text-gray-500 mt-1">{result.explanation}</div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          <button
            onClick={() => setQuiz({ quizId: null, questions: [], currentIndex: 0, answers: {}, results: {}, completed: false, score: 0 })}
            className="mt-8 bg-purple-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-purple-700 transition-colors"
          >
            Start New Quiz
          </button>
        </div>
      </div>
    );
  }

  // Quiz in progress
  if (quiz.quizId && quiz.questions.length > 0) {
    const currentQ = quiz.questions[quiz.currentIndex];
    const answered = Object.keys(quiz.answers).length;

    return (
      <div className="p-8 max-w-3xl mx-auto">
        {/* Progress bar */}
        <div className="mb-6">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Question {quiz.currentIndex + 1} / {quiz.questions.length}</span>
            <span>{answered} answered</span>
          </div>
          <div className="w-full h-2 bg-gray-200 rounded-full">
            <div className="h-2 bg-purple-600 rounded-full transition-all" style={{ width: `${((quiz.currentIndex + 1) / quiz.questions.length) * 100}%` }}></div>
          </div>
        </div>

        {/* Question */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
          <div className="flex items-center gap-2 mb-4">
            {currentQ.difficulty && (
              <span className={`text-xs px-2 py-0.5 rounded-full ${
                currentQ.difficulty === "easy" ? "bg-green-100 text-green-700" :
                currentQ.difficulty === "medium" ? "bg-yellow-100 text-yellow-700" :
                "bg-red-100 text-red-700"
              }`}>
                {currentQ.difficulty}
              </span>
            )}
          </div>
          <h2 className="text-lg font-medium text-gray-900 mb-6">{currentQ.question_text}</h2>

          <div className="space-y-3">
            {currentQ.options.map((opt: any) => {
              const isSelected = quiz.answers[currentQ.id] === opt.id;
              const result = quiz.results[currentQ.id];
              const isCorrectOption = result && result.correct_option_id === opt.id;
              const isWrongSelection = isSelected && result && !result.is_correct;

              return (
                <button
                  key={opt.id}
                  onClick={() => answerQuestion(currentQ.id, opt.id)}
                  disabled={!!result || submitting}
                  className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                    isCorrectOption ? "border-green-500 bg-green-50" :
                    isWrongSelection ? "border-red-500 bg-red-50" :
                    isSelected ? "border-purple-500 bg-purple-50" :
                    "border-gray-200 hover:border-gray-300 hover:bg-gray-50"
                  } ${result ? "cursor-default" : "cursor-pointer"}`}
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center flex-shrink-0 ${
                      isCorrectOption ? "border-green-500 bg-green-500" :
                      isWrongSelection ? "border-red-500 bg-red-500" :
                      isSelected ? "border-purple-500 bg-purple-500" :
                      "border-gray-300"
                    }`}>
                      {(isCorrectOption || isWrongSelection || isSelected) && (
                        <span className="text-white text-xs">✓</span>
                      )}
                    </div>
                    <span className="text-sm">{opt.text}</span>
                  </div>
                </button>
              );
            })}
          </div>

          {/* Explanation */}
          {quiz.results[currentQ.id] && (
            <div className={`mt-4 p-4 rounded-lg ${quiz.results[currentQ.id].is_correct ? "bg-green-50" : "bg-orange-50"}`}>
              <div className="font-medium text-sm mb-1">
                {quiz.results[currentQ.id].is_correct ? "✅ Correct!" : "❌ Incorrect"}
              </div>
              <div className="text-sm text-gray-700">{quiz.results[currentQ.id].explanation}</div>
            </div>
          )}
        </div>

        {/* Navigation */}
        <div className="flex justify-between">
          <button
            onClick={prevQuestion}
            disabled={quiz.currentIndex === 0}
            className="px-6 py-2.5 border border-gray-300 rounded-lg text-sm font-medium hover:bg-gray-50 disabled:opacity-50"
          >
            Previous
          </button>
          <div className="flex gap-3">
            {quiz.currentIndex < quiz.questions.length - 1 ? (
              <button
                onClick={nextQuestion}
                className="px-6 py-2.5 bg-purple-600 text-white rounded-lg text-sm font-medium hover:bg-purple-700"
              >
                Next
              </button>
            ) : (
              <button
                onClick={completeQuiz}
                className="px-6 py-2.5 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700"
              >
                Complete Quiz
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Setup screen
  return (
    <div className="p-8 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Practice Quiz</h1>
      <p className="text-gray-600 mb-8">Select a certification and start practicing</p>

      <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Certification</label>
          <select
            value={selectedCert || ""}
            onChange={(e) => setSelectedCert(Number(e.target.value))}
            className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
          >
            <option value="">Select a certification</option>
            {certifications.map((c) => (
              <option key={c.id} value={c.id}>{c.code} - {c.name}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Number of Questions</label>
          <select
            value={numQuestions}
            onChange={(e) => setNumQuestions(Number(e.target.value))}
            className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
          >
            {[5, 10, 15, 20, 30, 50].map((n) => (
              <option key={n} value={n}>{n} Questions</option>
            ))}
          </select>
        </div>

        <button
          onClick={startQuiz}
          disabled={!selectedCert || loading}
          className="w-full bg-purple-600 text-white py-3 rounded-lg font-semibold hover:bg-purple-700 transition-colors disabled:opacity-50"
        >
          {loading ? "Starting Quiz..." : "Start Practice Quiz"}
        </button>
      </div>
    </div>
  );
}
