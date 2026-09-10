"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/", label: "Analisar", icon: "🔍" },
  { href: "/compare", label: "Comparar", icon: "📊" },
  { href: "/crawl", label: "Crawler", icon: "🕷️" },
  { href: "/history", label: "Histórico", icon: "📜" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 border-r border-[var(--border-color)] bg-[var(--bg-card)] hidden md:flex flex-col">
      <div className="p-6">
        <a
          href="https://mezzoldstudio.com.br/"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center space-x-3 cursor-pointer group mb-6"
          title="Mezzold Studio (mezzoldstudio.com.br)"
        >
          <div className="w-10 h-10 rounded-xl bg-slate-900 border border-slate-700 flex items-center justify-center p-1.5 shadow-md group-hover:border-blue-500/50 transition-colors shrink-0">
            <img
              src="/mezzold-logo.png"
              alt="Mezzold Studio"
              className="w-full h-full object-contain drop-shadow-[0_0_6px_rgba(59,130,246,0.3)]"
            />
          </div>
          <div>
            <div className="flex items-center space-x-1.5">
              <span className="font-bold text-base tracking-tight text-white group-hover:text-blue-400 transition-colors">
                WebArchiver
              </span>
              <span className="px-1.5 py-0.2 text-[10px] font-semibold bg-blue-500/20 text-blue-400 border border-blue-500/30 rounded-full">
                PRO
              </span>
            </div>
            <p className="text-[10px] text-slate-400 font-mono leading-none mt-1">
              by Mezzold Studio<span className="text-blue-500 font-bold">.</span>
            </p>
          </div>
        </a>
      </div>
      <nav className="flex-1 px-4 space-y-2">
        {navItems.map((item) => {
          const isActive = pathname === item.href || (item.href !== "/" && pathname.startsWith(item.href));
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200",
                isActive 
                  ? "bg-white/10 text-white font-medium shadow-sm" 
                  : "text-slate-400 hover:text-white hover:bg-white/5"
              )}
            >
              <span className="text-xl">{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>
      <div className="p-4 m-4 rounded-xl bg-white/5 border border-white/10 text-xs text-slate-400 flex flex-col gap-2">
        <a
          href="https://mezzoldstudio.com.br/"
          target="_blank"
          rel="noopener noreferrer"
          className="hover:text-white transition-colors flex items-center justify-between group"
        >
          <span className="font-semibold text-slate-300 group-hover:text-white">Mezzold Studio</span>
          <span className="text-[10px] text-blue-400 font-mono">↗</span>
        </a>
        <p className="text-[10px] text-slate-500 font-mono leading-tight">
          Software House Premium
        </p>
      </div>
    </aside>
  );
}
