import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Link from "next/link";
import { Sidebar } from "@/components/ui/Sidebar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "WebArchiver Pro",
  description: "Professional Web Scraping and Archiving Tool",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR">
      <body className={`${inter.className} bg-[var(--bg-dark)] text-[var(--text-primary)] min-h-screen flex flex-col`}>
        <div className="flex flex-1 h-screen overflow-hidden">
          <Sidebar />
          <div className="flex-1 flex flex-col relative overflow-y-auto">
            <header className="h-16 border-b border-[var(--border-color)] flex items-center px-6 glass sticky top-0 z-10">
              <h1 className="text-xl font-bold tracking-tight">
                <span className="text-gradient">WebArchiver</span> Pro
              </h1>
            </header>
            <main className="flex-1 p-6 relative">
              {children}
            </main>
          </div>
        </div>
      </body>
    </html>
  );
}
