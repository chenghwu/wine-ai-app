import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });
const geistMono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Wine Intelligence Analyzer",
  description: "Discover wine profiles with expert reviews.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${geistSans.variable} ${geistMono.variable} overflow-x-hidden flex flex-col min-h-screen bg-zinc-900 text-white antialiased items-center justify-center`}
      >
        <div className="w-full max-w-2xl mx-atuo px-4">
          {children}
        </div>
      </body>
    </html>
  );
}