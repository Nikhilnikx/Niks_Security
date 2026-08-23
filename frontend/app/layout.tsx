import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Niks Security - Cybersecurity SaaS Platform",
  description: "Detect. Investigate. Respond. Real-time threat detection and security intelligence for modern infrastructure.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-[#0a0e1a] text-slate-200 antialiased">
        {children}
      </body>
    </html>
  );
}
