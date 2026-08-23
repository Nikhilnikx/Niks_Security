import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./pages/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./app/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(240 3.7% 15.9%)",
        input: "hsl(240 3.7% 15.9%)",
        ring: "hsl(217 91% 60%)",
        background: "hsl(224 71% 4%)",
        foreground: "hsl(213 31% 91%)",
        primary: { DEFAULT: "hsl(217 91% 60%)", foreground: "hsl(210 40% 98%)" },
        secondary: { DEFAULT: "hsl(222.2 47.4% 11.2%)", foreground: "hsl(210 40% 98%)" },
        destructive: { DEFAULT: "hsl(0 62% 30%)", foreground: "hsl(210 40% 98%)" },
        muted: { DEFAULT: "hsl(223 47% 11%)", foreground: "hsl(215.4 16.3% 56.9%)" },
        accent: { DEFAULT: "hsl(216 50% 15%)", foreground: "hsl(210 40% 98%)" },
        card: { DEFAULT: "hsl(222 47% 11%)", foreground: "hsl(210 40% 98%)" },
        critical: "hsl(0 84% 60%)",
        high: "hsl(25 95% 53%)",
        medium: "hsl(38 92% 50%)",
        low: "hsl(142 71% 45%)",
        info: "hsl(217 91% 60%)",
        navy: { 900: "#0a0e1a", 800: "#0f1629", 700: "#141c35", 600: "#1a2440" },
      },
      borderRadius: { lg: "0.5rem", md: "calc(0.5rem - 2px)", sm: "calc(0.5rem - 4px)" },
      fontFamily: { sans: ["Inter", "system-ui", "sans-serif"], mono: ["JetBrains Mono", "monospace"] },
      keyframes: { "pulse-glow": { "0%, 100%": { opacity: "1" }, "50%": { opacity: "0.5" } } },
      animation: { "pulse-glow": "pulse-glow 2s ease-in-out infinite" },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
