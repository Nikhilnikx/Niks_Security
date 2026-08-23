"use client";
import Link from "next/link";
import dynamic from "next/dynamic";
import { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { Shield, Lock, Eye, EyeOff, CheckCircle, ArrowLeft } from "lucide-react";

const Antigravity = dynamic(() => import("../../components/Antigravity/Antigravity"), { ssr: false });

function ResetPasswordForm() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token") || "";

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [tokenValid, setTokenValid] = useState<boolean | null>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => setMounted(true), []);

  // Verify token on mount
  useEffect(() => {
    if (!token) {
      setTokenValid(false);
      return;
    }
    fetch(`/api/auth/reset-password/verify?token=${encodeURIComponent(token)}`)
      .then((res) => {
        setTokenValid(res.ok);
      })
      .catch(() => setTokenValid(false));
  }, [token]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters");
      return;
    }

    setLoading(true);

    try {
      const res = await fetch("/api/auth/reset-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, new_password: password }),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.detail || "Reset failed");
        setLoading(false);
        return;
      }

      setSuccess(true);
    } catch {
      setError("Connection failed. Please try again.");
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
            {success ? "Password Reset Complete" : "Set New Password"}
          </h1>
          <p className="text-slate-400 text-sm">
            {success
              ? "Your password has been updated. You can now sign in."
              : "Enter your new password below."
            }
          </p>
        </div>

        {/* Form Card */}
        <div className="p-8 rounded-2xl border border-slate-800/50 bg-slate-900/30 backdrop-blur-xl">
          {/* Invalid token state */}
          {tokenValid === false && (
            <div className="text-center space-y-4">
              <div className="w-16 h-16 mx-auto rounded-full bg-red-500/10 border border-red-500/20 flex items-center justify-center">
                <Lock className="w-8 h-8 text-red-400" />
              </div>
              <p className="text-red-400 text-sm">This reset link is invalid or has expired.</p>
              <Link
                href="/forgot-password"
                className="inline-flex items-center gap-2 text-purple-400 hover:text-purple-300 text-sm transition-colors"
              >
                <ArrowLeft className="w-4 h-4" />
                Request a new reset link
              </Link>
            </div>
          )}

          {/* Loading state */}
          {tokenValid === null && (
            <div className="text-center py-8">
              <div className="w-8 h-8 mx-auto border-2 border-purple-500 border-t-transparent rounded-full animate-spin" />
              <p className="text-slate-400 text-sm mt-3">Verifying reset link...</p>
            </div>
          )}

          {/* Success state */}
          {success && (
            <div className="text-center space-y-6">
              <div className="w-16 h-16 mx-auto rounded-full bg-green-500/10 border border-green-500/20 flex items-center justify-center">
                <CheckCircle className="w-8 h-8 text-green-400" />
              </div>
              <p className="text-slate-300 text-sm">Your password has been successfully reset.</p>
              <Link
                href="/login"
                className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-medium transition-all hover:shadow-lg hover:shadow-purple-500/20"
              >
                Sign In
              </Link>
            </div>
          )}

          {/* Reset form */}
          {tokenValid === true && !success && (
            <form onSubmit={handleSubmit} className="space-y-5">
              {error && (
                <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
                  {error}
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">New Password</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                  <input
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    className="w-full pl-10 pr-12 py-3 rounded-xl bg-slate-800/50 border border-slate-700/50 text-white placeholder-slate-500 focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500 transition-colors"
                    placeholder="Min 8 characters"
                  />
                  <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300">
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Confirm Password</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                  <input
                    type={showPassword ? "text" : "password"}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    required
                    className="w-full pl-10 pr-4 py-3 rounded-xl bg-slate-800/50 border border-slate-700/50 text-white placeholder-slate-500 focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500 transition-colors"
                    placeholder="Re-enter password"
                  />
                </div>
                {password && confirmPassword && password !== confirmPassword && (
                  <p className="text-xs text-red-400 mt-1">Passwords don&apos;t match</p>
                )}
              </div>

              <p className="text-xs text-slate-500">Must include uppercase, lowercase, and a number</p>

              <button
                type="submit"
                disabled={loading || !password || !confirmPassword}
                className="w-full py-3 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-medium transition-all hover:shadow-lg hover:shadow-purple-500/20 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? "Resetting..." : "Reset Password"}
              </button>
            </form>
          )}
        </div>

        <p className="text-center mt-6 text-sm text-slate-400">
          <Link href="/login" className="text-purple-400 hover:text-purple-300 transition-colors">
            Back to Sign In
          </Link>
        </p>
      </div>
    </div>
  );
}

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center bg-[#080b16]">
        <div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin" />
      </div>
    }>
      <ResetPasswordForm />
    </Suspense>
  );
}
