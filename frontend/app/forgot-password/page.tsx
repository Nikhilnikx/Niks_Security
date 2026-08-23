"use client";
import Link from "next/link";
import dynamic from "next/dynamic";
import { useState, useEffect } from "react";
import { Shield, Mail, ArrowLeft, CheckCircle } from "lucide-react";

const Antigravity = dynamic(() => import("../../components/Antigravity/Antigravity"), { ssr: false });

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [debugUrl, setDebugUrl] = useState("");
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await fetch("/api/auth/forgot-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email }),
      });

      const data = await res.json();

      // Always show success to prevent email enumeration
      setSent(true);
      if (data.debug_url) {
        setDebugUrl(data.debug_url);
      }
    } catch {
      setSent(true); // Still show success
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#080b16] px-4 relative overflow-hidden">
      {/* Grid background */}
      <div className="absolute inset-0 opacity-[0.03]" style={{backgroundImage: "radial-gradient(circle at 1px 1px, rgba(168,85,247,0.5) 1px, transparent 0)", backgroundSize: "40px 40px"}} />

      {/* Purple glow blobs */}
      <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-purple-600/8 rounded-full blur-[150px]" />
      <div className="absolute bottom-0 right-1/4 w-[500px] h-[500px] bg-violet-600/8 rounded-full blur-[150px]" />

      {/* Antigravity particle background */}
      <div className="absolute inset-0 z-0" style={{ opacity: 0.25 }}>
        {mounted && (
          <Antigravity
            count={150}
            magnetRadius={6}
            ringRadius={7}
            waveSpeed={0.4}
            waveAmplitude={1}
            particleSize={1.2}
            lerpSpeed={0.05}
            color="#a855f7"
            autoAnimate={true}
            particleVariance={1}
          />
        )}
      </div>

      <div className="w-full max-w-md relative z-10">
        {/* Logo */}
        <div className="text-center mb-8">
          <Link href="/home" className="inline-flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-violet-600 flex items-center justify-center shadow-lg shadow-purple-500/20">
              <Shield className="w-6 h-6 text-white" />
            </div>
            <span className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-violet-300 bg-clip-text text-transparent">NIKS SECURITY</span>
          </Link>
          <h1 className="text-2xl font-bold text-white mb-2">
            {sent ? "Check your email" : "Forgot your password?"}
          </h1>
          <p className="text-slate-400 text-sm">
            {sent
              ? "We've sent a password reset link to your email address."
              : "Enter your email and we'll send you a reset link."
            }
          </p>
        </div>

        {/* Form Card */}
        <div className="p-8 rounded-2xl border border-slate-800/50 bg-slate-900/30 backdrop-blur-xl">
          {error && (
            <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
              {error}
            </div>
          )}

          {sent ? (
            <div className="text-center space-y-6">
              <div className="w-16 h-16 mx-auto rounded-full bg-green-500/10 border border-green-500/20 flex items-center justify-center">
                <CheckCircle className="w-8 h-8 text-green-400" />
              </div>

              <p className="text-slate-300 text-sm">
                If an account exists with <span className="text-white font-medium">{email}</span>, you&apos;ll receive a password reset link shortly.
              </p>

              {/* Dev mode: show reset link */}
              {debugUrl && (
                <div className="p-3 rounded-lg bg-purple-500/10 border border-purple-500/20 text-left">
                  <p className="text-purple-400 text-xs font-medium mb-2">🔧 Dev Mode — Reset Link:</p>
                  <Link href={debugUrl.replace("http://localhost:3000", "")} className="text-purple-300 text-xs break-all hover:text-purple-200 underline">
                    {debugUrl}
                  </Link>
                </div>
              )}

              <Link
                href="/login"
                className="inline-flex items-center gap-2 text-purple-400 hover:text-purple-300 text-sm transition-colors"
              >
                <ArrowLeft className="w-4 h-4" />
                Back to Sign In
              </Link>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Email Address</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="w-full pl-10 pr-4 py-3 rounded-xl bg-slate-800/50 border border-slate-700/50 text-white placeholder-slate-500 focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500 transition-colors"
                    placeholder="you@company.com"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-medium transition-all hover:shadow-lg hover:shadow-purple-500/20 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? "Sending..." : "Send Reset Link"}
              </button>
            </form>
          )}
        </div>

        {!sent && (
          <p className="text-center mt-6 text-sm text-slate-400">
            Remember your password?{" "}
            <Link href="/login" className="text-purple-400 hover:text-purple-300 transition-colors">
              Sign in
            </Link>
          </p>
        )}
      </div>
    </div>
  );
}
