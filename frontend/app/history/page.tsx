"use client";

import { useEffect, useState } from "react";
import { api, HistoryItem } from "@/lib/api";
import Link from "next/link";
import { cn } from "@/lib/utils";

export default function HistoryPage() {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const data = await api.getHistory();
      setHistory(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await api.deleteHistory(id);
      fetchHistory();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-fade-in">
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold text-white">Histórico de Análises</h2>
      </div>
      
      {loading ? (
        <div className="text-center text-slate-400 py-10 animate-pulse">Carregando histórico...</div>
      ) : history.length === 0 ? (
        <div className="glass p-8 rounded-2xl text-center">
          <div className="text-6xl mb-4">📜</div>
          <h3 className="text-xl text-white font-medium mb-2">Nenhum histórico encontrado</h3>
          <p className="text-slate-400">Você ainda não analisou nenhuma página.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {history.map(item => (
            <div key={item.id} className="glass p-6 rounded-2xl flex items-center justify-between hover:border-blue-500/30 transition-colors">
              <div className="space-y-1 overflow-hidden">
                <h3 className="text-lg font-medium text-white truncate" title={item.title || item.url}>{item.title || item.url}</h3>
                <p className="text-sm text-slate-400 truncate" title={item.url}>{item.url}</p>
                <div className="flex items-center space-x-4 text-xs text-slate-500 mt-2">
                  <span>📅 {new Date(item.created_at).toLocaleString()}</span>
                  {item.word_count !== undefined && <span>📊 {item.word_count} palavras</span>}
                  {item.image_count !== undefined && <span>🖼️ {item.image_count} imagens</span>}
                  <span className={cn("px-2 py-0.5 rounded-full", item.status === "complete" ? "bg-green-500/10 text-green-400" : "bg-yellow-500/10 text-yellow-400")}>
                      {item.status}
                  </span>
                </div>
              </div>
              <div className="flex items-center space-x-3 ml-4 shrink-0">
                <Link href={`/analysis/${item.id}`}>
                  <button className="bg-blue-600/20 text-blue-400 hover:bg-blue-600/40 px-4 py-2 rounded-lg transition-colors font-medium">
                    Ver Análise
                  </button>
                </Link>
                <button 
                  onClick={() => handleDelete(item.id)}
                  className="bg-red-500/10 text-red-400 hover:bg-red-500/20 px-3 py-2 rounded-lg transition-colors"
                  title="Excluir"
                >
                  🗑️
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
