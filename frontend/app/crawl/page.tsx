"use client";

import { useEffect, useState } from "react";
import { api, CrawlResponse, ProgressEvent } from "@/lib/api";
import { cn } from "@/lib/utils";

export default function CrawlPage() {
  const [url, setUrl] = useState("");
  const [depth, setDepth] = useState(2);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<CrawlResponse | null>(null);
  const [progress, setProgress] = useState<string>("Aguardando...");
  const [error, setError] = useState("");

  const handleCrawl = async () => {
    setLoading(true);
    setResult(null);
    setError("");
    
    try {
      const res = await api.crawl(url, depth, 100);
      const crawlId = res.id;
      
      const apiBase = process.env.NEXT_PUBLIC_API_URL || "";
      const eventSource = new EventSource(`${apiBase}/api/crawl/${crawlId}/progress`);
      eventSource.onmessage = async (event) => {
        const data: ProgressEvent = JSON.parse(event.data);
        setProgress(data.message);
        
        if (data.status === "complete") {
          eventSource.close();
          const finalResult = await api.getCrawl(crawlId);
          setResult(finalResult);
          setLoading(false);
        } else if (data.status === "error") {
          eventSource.close();
          setError("Erro durante o rastreamento.");
          setLoading(false);
        }
      };
      
      eventSource.onerror = () => {
        eventSource.close();
        // Fallback polling
        const fallbackPoll = setInterval(async () => {
            try {
                const pollRes = await api.getCrawl(crawlId);
                if (pollRes.status === "complete") {
                    setResult(pollRes);
                    setLoading(false);
                    clearInterval(fallbackPoll);
                } else if (pollRes.status === "error") {
                    setError("Erro durante o rastreamento.");
                    setLoading(false);
                    clearInterval(fallbackPoll);
                }
            } catch(e) {}
        }, 2000);
      };

    } catch (e) {
      console.error(e);
      setError("Falha ao iniciar o crawler.");
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-fade-in">
      <h2 className="text-3xl font-bold text-white mb-6">Web Crawler</h2>
      
      <div className="glass p-8 rounded-2xl">
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-slate-400 mb-2">URL Base</label>
            <input 
              type="url" 
              value={url}
              onChange={e => setUrl(e.target.value)}
              placeholder="https://exemplo.com"
              className="w-full bg-[#0a0a0f]/80 border border-[var(--border-color)] rounded-xl py-3 px-4 text-white placeholder-slate-500 focus:outline-none glow-focus transition-all"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-400 mb-2">Profundidade Máxima: {depth}</label>
            <input 
              type="range" 
              min="1" max="5" 
              value={depth}
              onChange={e => setDepth(parseInt(e.target.value))}
              className="w-full accent-blue-500"
            />
          </div>
          <button 
            onClick={handleCrawl}
            disabled={loading || !url}
            className={cn(
              "w-full bg-gradient-to-r from-blue-600 to-violet-600 text-white font-semibold py-4 rounded-xl transition-all duration-300",
              (loading || !url) ? "opacity-50 cursor-not-allowed" : "hover:scale-105 hover:shadow-[0_0_20px_rgba(139,92,246,0.5)]"
            )}
          >
            {loading ? "Rastreando..." : "Iniciar Crawler"}
          </button>
        </div>
      </div>
      
      {loading && (
          <div className="text-center text-blue-400 font-medium animate-pulse">
              {progress}
          </div>
      )}

      {error && <div className="text-red-500 font-medium text-center">{error}</div>}

      {result && (
        <div className="space-y-6 animate-fade-in">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="glass p-6 rounded-2xl flex flex-col items-center justify-center">
              <span className="text-slate-400 mb-2">Páginas Encontradas</span>
              <span className="text-4xl font-black text-white">{result.pages_found}</span>
            </div>
            <div className="glass p-6 rounded-2xl flex flex-col items-center justify-center">
              <span className="text-slate-400 mb-2">Páginas Extraídas</span>
              <span className="text-4xl font-black text-blue-400">{result.pages_scraped}</span>
            </div>
          </div>
          
          <div className="glass p-6 rounded-2xl">
            <h3 className="text-xl font-bold text-white border-b border-slate-800 pb-4 mb-4">Sitemap Encontrado</h3>
            <div className="max-h-96 overflow-y-auto space-y-2 pr-2 custom-scrollbar">
              {result.pages?.map((p, i) => (
                <div key={i} className="bg-slate-900/50 p-3 rounded-lg border border-slate-800 flex justify-between items-center">
                    <div className="overflow-hidden">
                        <p className="text-white text-sm truncate" title={p.title || p.url}>{p.title || "Sem Título"}</p>
                        <a href={p.url} target="_blank" rel="noreferrer" className="text-xs text-blue-400 truncate block hover:underline">{p.url}</a>
                    </div>
                    <span className="text-xs px-2 py-1 bg-slate-800 rounded-md text-slate-300">Nível {p.depth}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
