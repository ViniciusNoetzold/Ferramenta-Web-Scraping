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
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center text-white font-bold text-xl mb-8 shadow-lg shadow-blue-500/20">
          W
        </div>
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
      <div className="p-6 text-xs text-slate-500">
        v1.0.0 Pro
      </div>
    </aside>
  );
}
