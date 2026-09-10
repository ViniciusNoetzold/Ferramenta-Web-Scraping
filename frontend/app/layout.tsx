import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Link from "next/link";
import { Sidebar } from "@/components/ui/Sidebar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "WebArchiver Pro | Mezzold Studio",
  description: "Ferramenta profissional de Web Scraping, Extração e Análise de Conteúdo - Desenvolvido pela Mezzold Studio.",
  icons: {
    icon: "/mezzold-emblem.png",
  },
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
            <header className="h-16 border-b border-[var(--border-color)] flex items-center justify-between px-6 glass sticky top-0 z-10">
              <div className="flex items-center gap-3">
                <h1 className="text-xl font-bold tracking-tight">
                  <span className="text-gradient">WebArchiver</span> Pro
                </h1>
                <span className="text-xs text-slate-400 font-mono hidden sm:inline">
                  by <a href="https://mezzoldstudio.com.br/" target="_blank" rel="noopener noreferrer" className="hover:text-white underline decoration-blue-500/50">Mezzold Studio</a>
                </span>
              </div>
              <div className="flex items-center gap-3">
                <a
                  href="https://mezzoldstudio.com.br/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1 rounded-full border border-slate-700 bg-slate-900/80 hover:bg-slate-800 text-[10px] font-mono text-slate-400 hover:text-slate-200 transition-colors"
                >
                  <img src="/mezzold-logo.png" alt="Mezzold" className="w-3 h-3 object-contain" />
                  <span>[ MEZZOLD STUDIO ]</span>
                </a>
                <a
                  href="https://mezzoldstudio.com.br/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 text-xs font-medium text-slate-300 hover:text-white transition-all shadow-sm"
                >
                  <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></span>
                  <span>Mezzold Studio</span>
                  <span className="text-slate-500">↗</span>
                </a>
              </div>
            </header>
            <main className="flex-1 p-6 relative flex flex-col">
              <div className="flex-1">
                {children}
              </div>
              {/* FOOTER: MEZZOLD STUDIO */}
              <footer className="border-t border-[var(--border-color)] py-6 mt-12 text-center flex flex-col items-center gap-2">
                <a
                  href="https://mezzoldstudio.com.br/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 transition-all text-xs text-slate-400 hover:text-white group shadow-sm"
                >
                  <img src="/mezzold-logo.png" alt="Mezzold Studio" className="w-3.5 h-3.5 object-contain opacity-80 group-hover:opacity-100 transition-opacity" />
                  <span>
                    Desenvolvido pela <strong className="font-semibold text-slate-200 group-hover:text-white">Mezzold Studio<span className="text-blue-500 font-bold">.</span></strong>
                  </span>
                  <span className="text-slate-500 group-hover:text-slate-300 transition-colors">↗</span>
                </a>
                <p className="text-[11px] text-slate-500 font-mono">
                  Software House Premium • Micro SaaS & Dashboards de Alta Performance
                </p>
              </footer>
            </main>
          </div>
        </div>
      </body>
    </html>
  );
}
