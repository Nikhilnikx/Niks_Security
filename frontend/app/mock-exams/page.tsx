"use client";

import { useEffect, useState, useRef } from "react";
import { api } from "@/lib/api";

export default function MockExamsPage() {
  const [certifications, setCertifications] = useState<any[]>([]);
  const [selectedCert, setSelectedCert] = useState<number | null>(null);
  const [exam, setExam] = useState<any>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<number, number>>({});
  const [flagged, setFlagged] = useState<Set<number>>(new Set());
  const [timeLeft, setTimeLeft] = useState(0);
  const [submitted, setSubmitted] = useState(false);
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    api.get<any[]>("/api/certifications").then(setCertifications).catch(console.error);
    return () => { if (timerRef.current) clearInterval(timerRef.current); };
  }, []);

  useEffect(() => {
    if (exam && timeLeft > 0 && !submitted) {
      timerRef.current = setInterval(() => {
        setTimeLeft((t) => {
          if (t <= 1) { submitExam(); return 0; }
          return t - 1;
        });
      }, 1000);
      return () => { if (timerRef.current) clearInterval(timerRef.current); };
    }
  }, [exam, submitted]);

  const startExam = async () => {
    if (!selectedCert) return;
    setLoading(true);
    try {
      const data = await api.post<any>("/api/mock-exams/start", { certification_id: selectedCert });
      setExam(data);
      setCurrentIndex(0);
      setAnswers({});
      setFlagged(new Set());
      setTimeLeft(data.duration_minutes * 60);
      setSubmitted(false);
      setResults(null);
    } catch (err: any) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  const answerQuestion = async (questionId: number, optionId: number) => {
    try {
      await api.post(`/api/mock-exams/${exam.id}/answer`, {
        question_id: questionId,
        selected_option_id: optionId,
      });
      setAnswers((prev) => ({ ...prev, [questionId]: optionId }));
    } catch (err: any) {
      console.error(err);
    }
  };

  const toggleFlag = async (questionId: number) => {
    const newFlagged = new Set(flagged);
    const isFlagged = newFlagged.has(questionId);
    if (isFlagged) newFlagged.delete(questionId);
    else newFlagged.add(questionId);
    setFlagged(newFlagged);
    try {
      await api.post(`/api/mock-exams/${exam.id}/flag`, { question_id: questionId, flagged: !isFlagged });
    } catch (err) {}
  };

  const submitExam = async () => {
    if (timerRef.current) clearInterval(timerRef.current);
    try {
      const data = await api.post<any>(`/api/mock-exams/${exam.id}/submit`);
      setResults(data);
      setSubmitted(true);
    } catch (err: any) {
      alert(err.message);
    }
  };

  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s.toString().padStart(2, "0")}`;
  };

  // Results screen
  if (submitted && results) {
    return (
      <div className="p-8 max-w-4xl mx-auto">
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-8">
          <h2 className="text-2xl font-bold text-gray-900 text-center mb-8">Mock Exam Results</h2>

          <div className="grid grid-cols-3 gap-4 mb-8">
            <div className="text-center p-4 bg-purple-50 rounded-xl">
              <div className="text-3xl font-bold text-purple-600">{results.score}%</div>
              <div className="text-sm text-gray-600">Score</div>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-xl">
              <div className="text-3xl font-bold text-green-600">{results.correct_answers}/{results.total_questions}</div>
              <div className="text-sm text-gray-600">Correct</div>
            </div>
            <div className="text-center p-4 bg-blue-50 rounded-xl">
              <div className="text-3xl font-bold text-blue-600">{Math.floor(results.time_spent / 60)}m</div>
              <div className="text-sm text-gray-600">Time Spent</div>
            </div>
          </div>

          {/* Domain Performance */}
          {results.domain_performance && (
            <div className="mb-8">
              <h3 className="font-semibold text-gray-900 mb-4">Domain Performance</h3>
              <div className="space-y-3">
                {Object.entries(results.domain_performance).map(([name, data]: [string, any]) => (
                  <div key={name}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-700">{name}</span>
                      <span className={data.percentage >= 70 ? "text-green-600" : "text-red-600"}>{data.percentage}%</span>
                    </div>
                    <div className="w-full h-2 bg-gray-200 rounded-full">
                      <div className={`h-2 rounded-full ${data.percentage >= 70 ? "bg-green-500" : "bg-red-500"}`} style={{ width: `${data.percentage}%` }}></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Weak/Strong Areas */}
          <div className="grid grid-cols-2 gap-4 mb-8">
            <div>
              <h4 className="font-medium text-sm text-gray-900 mb-2">Strong Areas</h4>
              {results.strong_areas?.map((a: string) => (
                <div key={a} className="text-sm text-green-600 flex items-center gap-1">✅ {a}</div>
              ))}
            </div>
            <div>
              <h4 className="font-medium text-sm text-gray-900 mb-2">Weak Areas</h4>
              {results.weak_areas?.map((a: string) => (
                <div key={a} className="text-sm text-red-600 flex items-center gap-1">⚠️ {a}</div>
              ))}
            </div>
          </div>

          <button
            onClick={() => { setExam(null); setResults(null); setSubmitted(false); }}
            className="w-full bg-purple-600 text-white py-3 rounded-lg font-semibold hover:bg-purple-700"
          >
            Take Another Exam
          </button>
        </div>
      </div>
    );
  }

  // Exam in progress
  if (exam) {
    const currentQ = exam.questions[currentIndex];
    return (
      <div className="p-8 max-w-5xl mx-auto">
        <div className="flex gap-6">
          {/* Main area */}
          <div className="flex-1">
            {/* Header */}
            <div className="flex items-center justify-between mb-6 bg-white rounded-xl p-4 border border-gray-100">
              <div>
                <div className="font-semibold text-gray-900">Question {currentIndex + 1} / {exam.total_questions}</div>
              </div>
              <div className={`text-xl font-mono font-bold ${timeLeft < 300 ? "text-red-600" : "text-gray-900"}`}>
                ⏱ {formatTime(timeLeft)}
              </div>
            </div>

            {/* Question */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-4">
              <p className="text-lg font-medium text-gray-900 mb-6">{currentQ.question_text}</p>
              <div className="space-y-3">
                {currentQ.options.map((opt: any) => (
                  <button
                    key={opt.id}
                    onClick={() => answerQuestion(currentQ.id, opt.id)}
                    className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                      answers[currentQ.id] === opt.id
                        ? "border-purple-500 bg-purple-50"
                        : "border-gray-200 hover:border-gray-300 hover:bg-gray-50"
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                        answers[currentQ.id] === opt.id ? "border-purple-500 bg-purple-500" : "border-gray-300"
                      }`}>
                        {answers[currentQ.id] === opt.id && <span className="text-white text-xs">✓</span>}
                      </div>
                      <span className="text-sm">{opt.text}</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Flag + Navigation */}
            <div className="flex justify-between items-center">
              <button
                onClick={() => toggleFlag(currentQ.id)}
                className={`px-4 py-2 rounded-lg text-sm font-medium ${flagged.has(currentQ.id) ? "bg-orange-100 text-orange-700" : "bg-gray-100 text-gray-600 hover:bg-gray-200"}`}
              >
                {flagged.has(currentQ.id) ? "🚩 Flagged" : "🚩 Flag"}
              </button>
              <div className="flex gap-3">
                <button
                  onClick={() => setCurrentIndex(Math.max(0, currentIndex - 1))}
                  disabled={currentIndex === 0}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-sm disabled:opacity-50"
                >
                  ← Previous
                </button>
                <button
                  onClick={() => setCurrentIndex(Math.min(exam.questions.length - 1, currentIndex + 1))}
                  disabled={currentIndex === exam.questions.length - 1}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg text-sm hover:bg-purple-700 disabled:opacity-50"
                >
                  Next →
                </button>
              </div>
            </div>
          </div>

          {/* Sidebar - Question Navigator */}
          <div className="w-64 bg-white rounded-xl border border-gray-100 p-4 h-fit sticky top-8">
            <h3 className="font-semibold text-sm text-gray-900 mb-3">Question Navigator</h3>
            <div className="grid grid-cols-5 gap-2 mb-4">
              {exam.questions.map((q: any, i: number) => (
                <button
                  key={q.id}
                  onClick={() => setCurrentIndex(i)}
                  className={`w-10 h-10 rounded-lg text-xs font-medium ${
                    i === currentIndex ? "bg-purple-600 text-white" :
                    flagged.has(q.id) ? "bg-orange-100 text-orange-700" :
                    answers[q.id] ? "bg-green-100 text-green-700" :
                    "bg-gray-100 text-gray-600 hover:bg-gray-200"
                  }`}
                >
                  {i + 1}
                </button>
              ))}
            </div>
            <div className="text-xs text-gray-500 space-y-1">
              <div className="flex items-center gap-2"><div className="w-3 h-3 rounded bg-green-100"></div> Answered</div>
              <div className="flex items-center gap-2"><div className="w-3 h-3 rounded bg-orange-100"></div> Flagged</div>
              <div className="flex items-center gap-2"><div className="w-3 h-3 rounded bg-gray-100"></div> Unanswered</div>
            </div>
            <button
              onClick={submitExam}
              className="w-full mt-4 bg-red-600 text-white py-2.5 rounded-lg text-sm font-semibold hover:bg-red-700"
            >
              Submit Exam
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Setup screen
  return (
    <div className="p-8 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Mock Exam</h1>
      <p className="text-gray-600 mb-8">Simulate the real certification exam experience</p>

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

        <div className="bg-blue-50 p-4 rounded-lg text-sm text-blue-800">
          <p className="font-medium mb-1">📋 Mock Exam Features:</p>
          <ul className="space-y-1 text-blue-700">
            <li>• Timed exam with countdown</li>
            <li>• Question flagging and navigation</li>
            <li>• Domain-weighted question distribution</li>
            <li>• Detailed results with domain analysis</li>
          </ul>
        </div>

        <button
          onClick={startExam}
          disabled={!selectedCert || loading}
          className="w-full bg-purple-600 text-white py-3 rounded-lg font-semibold hover:bg-purple-700 disabled:opacity-50"
        >
          {loading ? "Starting Exam..." : "Start Mock Exam"}
        </button>
      </div>
    </div>
  );
}
