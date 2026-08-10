"use client";

import { useState } from "react";
import { api, CompareResponse } from "@/lib/api";
import { cn } from "@/lib/utils";

export default function ComparePage() {
  const [url1, setUrl1] = useState("");
  const [url2, setUrl2] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<CompareResponse | null>(null);
  const [error, setError] = useState("");

  const handleCompare = async () => {
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const res: any = await api.compare(url1, url2);
      const id = res.id;
      
      const interval = setInterval(async () => {
        try {
          const compareRes: any = await api.getCompare(id);
          if (compareRes.status === "complete") {
            setResult(compareRes);
            setLoading(false);
            clearInterval(interval);
          } else if (compareRes.status === "error") {
            setError(compareRes.error || "Erro durante a comparação.");
            setLoading(false);
            clearInterval(interval);
          }
        } catch(e) {
          console.error(e);
        }
      }, 2000);

      // Stop after 30 seconds
      setTimeout(() => {
        clearInterval(interval);
        if (loading) {
          setLoading(false);
          setError("A comparação demorou muito. Tente novamente.");
        }
      }, 30000);

    } catch (e) {
      console.error(e);
      setError("Erro ao iniciar comparação");
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-fade-in">
      <h2 className="text-3xl font-bold text-white mb-6">Comparar Páginas</h2>
      
      <div className="glass p-6 rounded-2xl">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-400 mb-2">URL 1 (Original)</label>
            <input 
              type="url" 
              value={url1}
              onChange={e => setUrl1(e.target.value)}
              placeholder="https://exemplo.com/v1"
              className="w-full bg-[#0a0a0f]/80 border border-[var(--border-color)] rounded-xl py-3 px-4 text-white placeholder-slate-500 focus:outline-none glow-focus transition-all"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-400 mb-2">URL 2 (Nova)</label>
            <input 
              type="url" 
              value={url2}
              onChange={e => setUrl2(e.target.value)}
              placeholder="https://exemplo.com/v2"
              className="w-full bg-[#0a0a0f]/80 border border-[var(--border-color)] rounded-xl py-3 px-4 text-white placeholder-slate-500 focus:outline-none glow-focus transition-all"
            />
          </div>
        </div>
        <div className="mt-6 flex justify-end">
          <button 
            onClick={handleCompare}
            disabled={loading || !url1 || !url2}
            className={cn(
              "bg-gradient-to-r from-blue-600 to-violet-600 text-white font-semibold py-3 px-6 rounded-xl transition-all duration-300",
              (loading || !url1 || !url2) ? "opacity-50 cursor-not-allowed" : "hover:scale-105 hover:shadow-[0_0_20px_rgba(139,92,246,0.5)]"
            )}
          >
            {loading ? "Comparando..." : "Comparar Agora"}
          </button>
        </div>
      </div>

      {error && <div className="text-red-500 font-medium">{error}</div>}

      {result && (
        <div className="space-y-6">
          <div className="glass p-6 rounded-2xl flex items-center justify-between">
            <h3 className="text-xl font-bold text-white">Score de Similaridade</h3>
            <div className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-violet-400">
              {Math.round(result.similarity_score! * 100)}%
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="glass p-6 rounded-2xl space-y-4">
              <h3 className="text-xl font-bold text-white border-b border-slate-800 pb-2">Conteúdo Adicionado</h3>
              <div className="max-h-96 overflow-y-auto space-y-2 pr-2 custom-scrollbar text-sm">
                {result.text_diffs?.filter(d => d.type === "add").map((d, i) => (
                  <div key={i} className="bg-green-500/10 border border-green-500/20 p-3 rounded-lg text-green-400">
                    {d.text}
                  </div>
                ))}
                {result.text_diffs?.filter(d => d.type === "add").length === 0 && <span className="text-slate-500">Nada adicionado.</span>}
              </div>
            </div>

            <div className="glass p-6 rounded-2xl space-y-4">
              <h3 className="text-xl font-bold text-white border-b border-slate-800 pb-2">Conteúdo Removido</h3>
              <div className="max-h-96 overflow-y-auto space-y-2 pr-2 custom-scrollbar text-sm">
                {result.text_diffs?.filter(d => d.type === "remove").map((d, i) => (
                  <div key={i} className="bg-red-500/10 border border-red-500/20 p-3 rounded-lg text-red-400">
                    <del>{d.text}</del>
                  </div>
                ))}
                {result.text_diffs?.filter(d => d.type === "remove").length === 0 && <span className="text-slate-500">Nada removido.</span>}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
