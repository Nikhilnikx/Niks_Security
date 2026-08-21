"use client";

import Link from "next/link";
import dynamic from "next/dynamic";
import CountUp from "@/components/animations/CountUp";
import SplitText from "@/components/animations/SplitText";
import ScrollReveal from "@/components/animations/ScrollReveal";
import StaggerReveal from "@/components/animations/StaggerReveal";

const Antigravity = dynamic(() => import("@/components/animations/Antigravity"), {
  ssr: false,
  loading: () => <div className="absolute inset-0 bg-gradient-to-br from-purple-900 to-blue-900"></div>,
});

const providers = [
  { name: "Microsoft", color: "#00a4ef", certs: ["AZ-900", "SC-900", "AZ-104", "AZ-204"] },
  { name: "AWS", color: "#ff9900", certs: ["Cloud Practitioner", "Solutions Architect", "Developer"] },
  { name: "Cisco", color: "#049fd9", certs: ["CCNA", "CyberOps", "DevNet"] },
  { name: "CompTIA", color: "#e42527", certs: ["A+", "Network+", "Security+", "Cloud+"] },
];

const features = [
  { icon: "📚", title: "Structured Learning", desc: "Follow official exam blueprints with organized domains, topics, and concepts." },
  { icon: "🎯", title: "Practice Engine", desc: "50 free MCQs per topic with explanations. Premium adds 50 more challenging questions." },
  { icon: "📝", title: "Mock Exams", desc: "Simulate real exam conditions with timed tests, domain distribution, and detailed results." },
  { icon: "🧠", title: "Adaptive Learning", desc: "AI-powered weak area detection and personalized question selection." },
  { icon: "🤖", title: "AI Tutor", desc: "Ask questions and get grounded answers powered by local AI." },
  { icon: "📊", title: "Progress Analytics", desc: "Track readiness score, domain mastery, and study streaks." },
  { icon: "🃏", title: "Flashcards", desc: "Spaced repetition flashcards for efficient memory retention." },
  { icon: "📄", title: "Document Intelligence", desc: "Upload study materials and ask questions against your documents." },
];

const stats = [
  { value: 500, suffix: "+", label: "Practice Questions", prefix: "" },
  { value: 4, suffix: "", label: "Certification Providers", prefix: "" },
  { value: 95, suffix: "%", label: "User Satisfaction", prefix: "" },
  { value: 50, suffix: "+", label: "Topics Covered", prefix: "" },
];

export default function HomePage() {
  return (
    <div className="min-h-screen">
      {/* Navigation */}
      <nav className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-purple-600 rounded-lg flex items-center justify-center text-white font-bold text-lg">N</div>
              <span className="text-xl font-bold text-gray-900">Niksmind</span>
            </div>
            <div className="hidden md:flex items-center gap-8">
              <Link href="#features" className="text-gray-600 hover:text-gray-900">Features</Link>
              <Link href="#providers" className="text-gray-600 hover:text-gray-900">Certifications</Link>
              <Link href="#pricing" className="text-gray-600 hover:text-gray-900">Pricing</Link>
              <Link href="/login" className="text-gray-600 hover:text-gray-900">Login</Link>
              <Link href="/register" className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors">
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero with Antigravity */}
      <section className="relative overflow-hidden">
        {/* Antigravity Background */}
        <div className="absolute inset-0 z-0">
          <Antigravity
            count={800}
            magnetRadius={12}
            ringRadius={8}
            waveSpeed={2.5}
            waveAmplitude={1.8}
            particleSize={0.6}
            lerpSpeed={0.05}
            color="#7c3aed"
            autoAnimate={true}
            particleVariance={0.8}
            rotationSpeed={0.05}
            depthFactor={1.0}
            pulseSpeed={3.5}
            particleShape="sphere"
            fieldStrength={15}
          />
        </div>

        {/* Gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-b from-white/90 via-white/70 to-white z-10"></div>

        <div className="relative z-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 lg:py-32">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h1 className="text-4xl lg:text-6xl font-bold text-gray-900 leading-tight">
                <SplitText text="One Platform." delay={0.2} speed={0.5} staggerChildren={0.04} />
                <br />
                <SplitText text="All Certifications." delay={0.8} speed={0.5} staggerChildren={0.04} />
                <br />
                <SplitText
                  text="Limitless Opportunities."
                  className="text-purple-600"
                  delay={1.4}
                  speed={0.5}
                  staggerChildren={0.04}
                />
              </h1>
              <p className="mt-6 text-lg text-gray-600 max-w-lg">
                Prepare for AWS, Microsoft, Cisco & CompTIA certifications with smart learning, practice tests, and AI guidance.
              </p>
              <div className="mt-8 flex flex-wrap gap-4">
                <Link href="/register" className="bg-purple-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-purple-700 transition-colors shadow-lg shadow-purple-200">
                  Start Learning
                </Link>
                <Link href="#features" className="border border-gray-300 text-gray-700 px-8 py-3 rounded-lg font-semibold hover:bg-gray-50 transition-colors">
                  Explore Features
                </Link>
              </div>
            </div>
            <div className="relative">
              <div className="grid grid-cols-2 gap-4">
                {providers.map((p) => (
                  <div key={p.name} className="bg-white/90 backdrop-blur rounded-xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-shadow">
                    <div className="text-2xl font-bold mb-2" style={{ color: p.color }}>{p.name}</div>
                    <div className="text-sm text-gray-500">{p.certs.length}+ Certifications</div>
                    <div className="mt-3 space-y-1">
                      {p.certs.map((c) => (
                        <div key={c} className="text-xs text-gray-600 flex items-center gap-1">
                          <span className="w-1 h-1 rounded-full" style={{ backgroundColor: p.color }}></span>
                          {c}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats with CountUp */}
      <ScrollReveal direction="up" distance={40} duration={0.8}>
        <section className="py-16 bg-white border-y">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <StaggerReveal stagger={0.1} direction="up" distance={30} className="grid grid-cols-2 lg:grid-cols-4 gap-8">
              {stats.map((stat, i) => (
                <div key={stat.label} className="text-center">
                  <div className="text-4xl lg:text-5xl font-bold text-purple-600">
                    <CountUp
                      to={stat.value}
                      duration={2.5}
                      delay={i * 0.2}
                      prefix={stat.prefix}
                      suffix={stat.suffix}
                    />
                  </div>
                  <div className="text-sm text-gray-600 mt-2">{stat.label}</div>
                </div>
              ))}
            </StaggerReveal>
          </div>
        </section>
      </ScrollReveal>

      {/* How it works */}
      <ScrollReveal direction="up" distance={50} duration={0.8}>
        <section className="py-20 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <SplitText text="How Niksmind Works" className="text-3xl font-bold text-gray-900" delay={0} speed={0.4} splitBy="words" staggerChildren={0.1} />
              <p className="mt-4 text-gray-600 max-w-2xl mx-auto">Your complete certification preparation journey</p>
            </div>
            <StaggerReveal stagger={0.06} direction="up" distance={20} className="flex flex-wrap justify-center gap-4 text-sm">
              {["Discover Certification", "Understand Exam", "Learn", "Practice", "Analyze Mistakes", "Mock Exam", "Readiness Score", "Certify"].map((step, i) => (
                <div key={step} className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-full bg-purple-100 text-purple-600 flex items-center justify-center font-bold">{i + 1}</div>
                  <span className="font-medium text-gray-700">{step}</span>
                  {i < 7 && <span className="text-gray-300 ml-2">→</span>}
                </div>
              ))}
            </StaggerReveal>
          </div>
        </section>
      </ScrollReveal>

      {/* Features */}
      <ScrollReveal direction="up" distance={50} duration={0.8}>
        <section id="features" className="py-20 bg-gray-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <SplitText text="Everything You Need" className="text-3xl font-bold text-gray-900" delay={0} speed={0.4} splitBy="words" staggerChildren={0.1} />
              <p className="mt-4 text-gray-600">A complete learning ecosystem in one platform</p>
            </div>
            <StaggerReveal stagger={0.08} direction="up" distance={30} className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {features.map((f) => (
                <div key={f.title} className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 hover:shadow-md hover:border-purple-200 transition-all">
                  <div className="text-3xl mb-4">{f.icon}</div>
                  <h3 className="font-semibold text-gray-900 mb-2">{f.title}</h3>
                  <p className="text-sm text-gray-600">{f.desc}</p>
                </div>
              ))}
            </StaggerReveal>
          </div>
        </section>
      </ScrollReveal>

      {/* Free vs Premium */}
      <ScrollReveal direction="up" distance={50} duration={0.8}>
        <section id="pricing" className="py-20 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <SplitText text="Free vs Premium" className="text-3xl font-bold text-gray-900" delay={0} speed={0.4} splitBy="words" staggerChildren={0.1} />
              <p className="mt-4 text-gray-600">Start free, upgrade when you need more</p>
            </div>
            <StaggerReveal stagger={0.15} direction="up" distance={40} className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {/* Free */}
            <div className="bg-gray-50 rounded-2xl p-8 border border-gray-200">
              <h3 className="text-xl font-bold text-gray-900 mb-2">Free</h3>
              <p className="text-gray-600 mb-6">Get started with essential features</p>
              <div className="text-4xl font-bold text-gray-900 mb-6">₹0</div>
              <ul className="space-y-3 mb-8">
                {["Learning Content", "50 Free MCQs per topic", "Basic Progress Tracking", "Concept Pages", "Mistake Review"].map((f) => (
                  <li key={f} className="flex items-center gap-2 text-gray-700">
                    <span className="text-green-500">✓</span> {f}
                  </li>
                ))}
                {["Premium MCQs", "Mock Exams", "AI Tutor", "Flashcards", "Adaptive Learning", "Study Plan"].map((f) => (
                  <li key={f} className="flex items-center gap-2 text-gray-400">
                    <span>✗</span> {f}
                  </li>
                ))}
              </ul>
              <Link href="/register" className="block text-center bg-gray-900 text-white py-3 rounded-lg font-semibold hover:bg-gray-800 transition-colors">
                Start Free
              </Link>
            </div>
            {/* Premium */}
            <div className="bg-purple-50 rounded-2xl p-8 border-2 border-purple-600 relative">
              <div className="absolute -top-3 right-6 bg-purple-600 text-white text-xs font-bold px-3 py-1 rounded-full">POPULAR</div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Premium</h3>
              <p className="text-gray-600 mb-6">Complete exam preparation</p>
              <div className="text-4xl font-bold text-purple-600 mb-6">₹499<span className="text-base font-normal text-gray-500">/cert</span></div>
              <ul className="space-y-3 mb-8">
                {["Everything in Free", "50 Premium MCQs per topic", "Full Mock Exams", "AI Tutor", "Flashcards", "Adaptive Learning", "Study Plan", "Advanced Analytics"].map((f) => (
                  <li key={f} className="flex items-center gap-2 text-gray-700">
                    <span className="text-green-500">✓</span> {f}
                  </li>
                ))}
              </ul>
              <Link href="/register" className="block text-center bg-purple-600 text-white py-3 rounded-lg font-semibold hover:bg-purple-700 transition-colors">
                Get Premium
              </Link>
            </div>
            </StaggerReveal>
          </div>
        </section>
      </ScrollReveal>

      {/* CTA */}
      <ScrollReveal direction="up" distance={40} duration={0.8}>
        <section className="py-20 bg-gradient-to-r from-purple-600 to-blue-600">
          <div className="max-w-4xl mx-auto text-center px-4">
            <SplitText text="Ready to Master Your Certification?" className="text-3xl font-bold text-white mb-4" delay={0} speed={0.4} splitBy="words" staggerChildren={0.08} />
            <p className="text-purple-100 mb-8 text-lg">Join Niksmind and start your certification preparation journey today.</p>
            <Link href="/register" className="bg-white text-purple-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors inline-block">
              Get Started Free
            </Link>
          </div>
        </section>
      </ScrollReveal>

      {/* Footer */}
      <ScrollReveal direction="up" distance={30} duration={0.6}>
        <footer className="bg-gray-900 text-gray-400 py-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center gap-2 mb-8">
              <div className="w-8 h-8 bg-purple-600 rounded-lg flex items-center justify-center text-white font-bold text-lg">N</div>
              <span className="text-xl font-bold text-white">Niksmind</span>
            </div>
            <p className="text-sm">© 2026 Niksmind. All rights reserved. Prepare. Practice. Master.</p>
          </div>
        </footer>
      </ScrollReveal>
    </div>
  );
}
