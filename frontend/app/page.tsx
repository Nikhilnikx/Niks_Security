"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();
  useEffect(() => {
    const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
    if (token) {
      router.push("/dashboard");
    } else {
      router.push("/home");
    }
  }, [router]);
  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0a0e1a]">
      <div className="animate-pulse text-blue-400 text-lg">Loading...</div>
    </div>
  );
}
