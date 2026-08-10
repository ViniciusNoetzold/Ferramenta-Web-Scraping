"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { api, HistoryItem } from "@/lib/api";
import { cn } from "@/lib/utils";

export default function Home() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const router = useRouter();

  useEffect(() => {
    api.getHistory().then(data => {
      // Show only last 5 items (or all if < 5)
      setHistory(data.slice(0, 5));
    }).catch(err => console.error("Error loading history", err));
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url) return;
    try {
      new URL(url); // validate URL
    } catch {
      alert("URL inválida");
      return;
    }
    
    setLoading(true);
    try {
      const { id } = await api.scrape(url, true, true);
      router.push(`/analysis/${id}`);
    } catch (err) {
      console.error(err);
      alert("Erro ao iniciar análise.");
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-12 pb-10 animate-fade-in">
      <section className="relative rounded-3xl overflow-hidden glass p-10 md:p-16 text-center animate-slide-up">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 via-violet-500/10 to-cyan-500/10 z-0"></div>
        <div className="relative z-10">
          <h2 className="text-4xl md:text-5xl font-extrabold mb-4 tracking-tight">
            Arquive a Web <br/> com <span className="text-gradient">Precisão</span>
          </h2>
          <p className="text-slate-400 mb-8 max-w-2xl mx-auto text-lg">
            Extraia, compare e arquive páginas com a ferramenta profissional definitiva.
          </p>
          
          <form onSubmit={handleSubmit} className="max-w-2xl mx-auto flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <span className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 text-xl">🔗</span>
              <input 
                type="url" 
                value={url}
                onChange={e => setUrl(e.target.value)}
                placeholder="https://exemplo.com"
                required
                className="w-full bg-[#0a0a0f]/80 border border-[var(--border-color)] rounded-xl py-4 pl-12 pr-4 text-white placeholder-slate-500 focus:outline-none glow-focus transition-all text-lg"
              />
            </div>
            <button 
              type="submit" 
              disabled={loading}
              className={cn(
                "bg-gradient-to-r from-blue-600 to-violet-600 text-white font-semibold py-4 px-8 rounded-xl transition-all duration-300 transform hover:scale-105 hover:shadow-[0_0_20px_rgba(139,92,246,0.5)]",
                loading && "opacity-70 cursor-not-allowed transform-none hover:scale-100"
              )}
            >
              {loading ? "Processando..." : "ANALISAR SITE"}
            </button>
          </form>
        </div>
      </section>

      <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 animate-slide-up" style={{ animationDelay: '0.1s' }}>
        {[
          { title: "Extração HTML", desc: "Código limpo e estruturado", icon: "📄" },
          { title: "IA Inteligente", desc: "Sumarização e tags", icon: "🧠" },
          { title: "Comparação", desc: "Encontre diferenças visuais", icon: "⚖️" },
          { title: "Exportação", desc: "PDF, JSON, MD, ZIP", icon: "📦" }
        ].map((feature, i) => (
          <div key={i} className="glass glass-hover p-6 rounded-2xl transition-all">
            <div className="text-3xl mb-4">{feature.icon}</div>
            <h3 className="text-lg font-semibold text-white mb-2">{feature.title}</h3>
            <p className="text-slate-400 text-sm">{feature.desc}</p>
          </div>
        ))}
      </section>

      <section className="animate-slide-up" style={{ animationDelay: '0.2s' }}>
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-bold text-white">Análises Recentes</h3>
          <button onClick={() => router.push('/history')} className="text-sm text-blue-400 hover:text-blue-300">Ver todas &rarr;</button>
        </div>
        <div className="glass rounded-2xl overflow-hidden">
          {history.length === 0 ? (
            <div className="p-8 text-center text-slate-500">Nenhuma análise recente.</div>
          ) : (
            <ul className="divide-y divide-[var(--border-color)]">
              {history.map(item => (
                <li key={item.id} className="p-4 hover:bg-white/5 transition-colors flex items-center justify-between cursor-pointer" onClick={() => router.push(`/analysis/${item.id}`)}>
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-full bg-[#0a0a0f] flex items-center justify-center border border-[var(--border-color)]">
                      🌐
                    </div>
                    <div>
                      <h4 className="text-white font-medium truncate max-w-[200px] md:max-w-md">{item.title || item.url}</h4>
                      <p className="text-xs text-slate-500">{item.url}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className={cn(
                      "px-2.5 py-1 text-xs rounded-full font-medium border",
                      item.status === 'completed' ? "bg-green-500/10 text-green-400 border-green-500/20" :
                      item.status === 'error' ? "bg-red-500/10 text-red-400 border-red-500/20" :
                      "bg-blue-500/10 text-blue-400 border-blue-500/20"
                    )}>
                      {item.status}
                    </span>
                    <span className="text-xs text-slate-500 hidden md:inline-block">
                      {new Date(item.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>
    </div>
  );
}
