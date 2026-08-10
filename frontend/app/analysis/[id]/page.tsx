"use client";

import { useState, useEffect, useCallback } from "react";
import { useParams } from "next/navigation";
import { api, ScrapeResponse, ContentNode, ImageInfo, StructureNode } from "@/lib/api";
import { cn } from "@/lib/utils";

/* ═══════════════════════════════════════════════════════════ */
/* ANALYSIS PAGE                                              */
/* ═══════════════════════════════════════════════════════════ */
export default function AnalysisPage() {
  const { id } = useParams();
  const [data, setData] = useState<ScrapeResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("texto");
  const [progress, setProgress] = useState(0);
  const [progressMsg, setProgressMsg] = useState("");
  const [lightbox, setLightbox] = useState<ImageInfo | null>(null);
  const [jsonCopied, setJsonCopied] = useState(false);
  const [exporting, setExporting] = useState<string | null>(null);

  /* ── poll until complete ─────────────────────────────────── */
  const pollScrape = useCallback(async (analysisId: string) => {
    try {
      const res = await api.getScrape(analysisId);
      if (res.status === "complete" || res.status === "error") {
        setData(res);
        setLoading(false);
        setProgress(100);
        return;
      }
      setProgress(prev => Math.min(prev + 8, 90));
      setProgressMsg("Extraindo conteúdo...");
      setTimeout(() => pollScrape(analysisId), 2000);
    } catch {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (typeof id === "string") {
      pollScrape(id);
    }
  }, [id, pollScrape]);

  /* ── loading state ──────────────────────────────────────── */
  if (loading) {
    return (
      <div className="max-w-6xl mx-auto space-y-6 animate-fade-in">
        <div className="glass rounded-2xl p-6 space-y-4">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-3 h-3 rounded-full bg-blue-500 animate-pulse" />
            <span className="text-slate-300 font-medium">{progressMsg || "Iniciando análise..."}</span>
          </div>
          <div className="w-full h-2 bg-[#1a1a2e] rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-blue-500 via-violet-500 to-cyan-500 rounded-full transition-all duration-700"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map(i => <div key={i} className="skeleton h-32 rounded-xl" />)}
        </div>
        <div className="skeleton h-96 rounded-2xl w-full" />
      </div>
    );
  }

  if (!data) {
    return <div className="text-center p-10 text-red-400 glass rounded-2xl animate-fade-in">Erro ao carregar análise.</div>;
  }

  /* ── tabs ────────────────────────────────────────────────── */
  const tabs = [
    { id: "html", label: "HTML", icon: "📄" },
    { id: "texto", label: "Texto", icon: "📝" },
    { id: "imagens", label: "Imagens", icon: "🖼️" },
    { id: "estrutura", label: "Estrutura", icon: "🏗️" },
    { id: "json", label: "JSON", icon: "📦" },
    { id: "exportar", label: "Exportar", icon: "📥" },
  ];

  /* ── helpers ─────────────────────────────────────────────── */
  const handleCopyJson = () => {
    navigator.clipboard.writeText(JSON.stringify(data, null, 2));
    setJsonCopied(true);
    setTimeout(() => setJsonCopied(false), 2000);
  };

  const handleExport = async (format: string) => {
    if (!id || typeof id !== "string") return;
    setExporting(format);
    try {
      const res = await api.exportAnalysis(id, format);
      window.open(`http://localhost:8000${res.download_url}`, "_blank");
    } catch (err) {
      console.error("Export error", err);
    }
    setExporting(null);
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-fade-in pb-10">
      {/* ── Top bar ──────────────────────────────────── */}
      <div className="glass p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-4 min-w-0">
          {data.metadata?.favicon && (
            <img src={data.metadata.favicon} alt="" className="w-8 h-8 rounded" onError={e => (e.currentTarget.style.display = "none")} />
          )}
          <div className="min-w-0">
            <h2 className="text-2xl font-bold text-white mb-1 truncate">{data.metadata?.title || data.url}</h2>
            <a href={data.url} target="_blank" rel="noreferrer" className="text-blue-400 text-sm hover:underline truncate block">{data.url}</a>
          </div>
        </div>
        <div className="flex items-center gap-3 flex-wrap">
          <StatusBadge status={data.status} />
          {data.technologies?.map((tech, i) => (
            <span key={i} className="px-2 py-0.5 text-xs rounded-full bg-violet-500/10 text-violet-300 border border-violet-500/20">{tech}</span>
          ))}
          {data.metadata?.language && (
            <span className="px-2 py-0.5 text-xs rounded-full bg-cyan-500/10 text-cyan-300 border border-cyan-500/20">{data.metadata.language}</span>
          )}
        </div>
      </div>

      {/* ── Stats row ────────────────────────────────── */}
      {data.stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard title="Palavras" value={data.stats.word_count} icon="📝" />
          <StatCard title="Imagens" value={data.stats.image_count} icon="🖼️" />
          <StatCard title="Links" value={data.stats.link_count} icon="🔗" />
          <StatCard title="Headings" value={data.stats.heading_count} icon="🏷️" />
        </div>
      )}

      {/* ── Tabs ──────────────────────────────────── */}
      <div className="glass rounded-2xl overflow-hidden flex flex-col min-h-[500px]">
        <div className="flex border-b border-[var(--border-color)] overflow-x-auto">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                "flex items-center gap-2 px-6 py-4 transition-all whitespace-nowrap relative",
                activeTab === tab.id
                  ? "text-blue-400 bg-white/5"
                  : "text-slate-400 hover:text-slate-200 hover:bg-white/5"
              )}
            >
              <span>{tab.icon}</span>
              <span className="font-medium">{tab.label}</span>
              {activeTab === tab.id && (
                <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-blue-500 to-violet-500" />
              )}
            </button>
          ))}
        </div>

        <div className="p-6 flex-1 bg-[#0a0a0f]/50 overflow-auto">
          {/* ── HTML TAB ───────────────────────────── */}
          {activeTab === "html" && (
            <pre className="text-sm text-slate-300 font-mono whitespace-pre-wrap leading-relaxed max-h-[600px] overflow-auto">
              {data.raw_html || "HTML indisponível"}
            </pre>
          )}

          {/* ── TEXTO TAB ──────────────────────────── */}
          {activeTab === "texto" && (
            <div className="space-y-4 max-w-3xl">
              {data.content && data.content.length > 0 ? (
                data.content.map((node, i) => <ContentBlock key={i} node={node} />)
              ) : (
                <div className="prose prose-invert max-w-none whitespace-pre-wrap">{data.text_content || "Texto indisponível"}</div>
              )}
            </div>
          )}

          {/* ── IMAGENS TAB ────────────────────────── */}
          {activeTab === "imagens" && (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {data.images?.map((img, i) => (
                  <div
                    key={i}
                    onClick={() => setLightbox(img)}
                    className="glass rounded-xl overflow-hidden group cursor-pointer transition-all hover:border-blue-500/30 hover:shadow-lg hover:shadow-blue-500/10"
                  >
                    <div className="aspect-video bg-black/50 flex items-center justify-center overflow-hidden p-2">
                      <img
                        src={img.absolute_url || img.url}
                        alt={img.alt_text || img.filename}
                        className="max-w-full max-h-full object-contain group-hover:scale-105 transition-transform"
                        onError={e => { e.currentTarget.style.display = "none"; e.currentTarget.parentElement!.innerHTML = `<div class="text-slate-500 text-sm p-4 text-center">${img.filename}</div>`; }}
                      />
                    </div>
                    <div className="p-3 space-y-1">
                      <p className="text-white text-sm font-medium truncate">{img.alt_text || img.filename}</p>
                      <div className="flex items-center gap-2 text-xs text-slate-500">
                        {img.width && img.height && <span>{img.width}×{img.height}</span>}
                        {img.format && <span className="uppercase">{img.format}</span>}
                        {img.section && <span className="truncate">📍 {img.section}</span>}
                      </div>
                    </div>
                  </div>
                ))}
                {(!data.images || data.images.length === 0) && (
                  <p className="text-slate-500 col-span-full text-center py-10">Nenhuma imagem encontrada.</p>
                )}
              </div>

              {/* Lightbox */}
              {lightbox && (
                <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-6" onClick={() => setLightbox(null)}>
                  <div className="glass rounded-2xl max-w-3xl w-full max-h-[80vh] overflow-auto p-6 space-y-4" onClick={e => e.stopPropagation()}>
                    <div className="flex justify-between items-start">
                      <h3 className="text-white font-bold text-lg">{lightbox.alt_text || lightbox.filename}</h3>
                      <button onClick={() => setLightbox(null)} className="text-slate-400 hover:text-white text-2xl">×</button>
                    </div>
                    <img src={lightbox.absolute_url || lightbox.url} alt={lightbox.alt_text || ""} className="w-full rounded-xl" />
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <Info label="Arquivo" value={lightbox.filename} />
                      <Info label="Alt Text" value={lightbox.alt_text} />
                      <Info label="Título" value={lightbox.title} />
                      <Info label="Legenda" value={lightbox.caption} />
                      <Info label="Seção" value={lightbox.section} />
                      <Info label="Posição" value={lightbox.position != null ? String(lightbox.position) : null} />
                      <Info label="Dimensões" value={lightbox.width && lightbox.height ? `${lightbox.width}×${lightbox.height}` : null} />
                      <Info label="Formato" value={lightbox.format} />
                      <Info label="URL" value={lightbox.absolute_url} />
                      {lightbox.ai_description && <Info label="Descrição IA" value={lightbox.ai_description} />}
                    </div>
                  </div>
                </div>
              )}
            </>
          )}

          {/* ── ESTRUTURA TAB ──────────────────────── */}
          {activeTab === "estrutura" && (
            <div className="font-mono text-sm">
              {data.structure ? (
                <TreeNode node={data.structure} depth={0} />
              ) : (
                <p className="text-slate-500">Estrutura indisponível.</p>
              )}
            </div>
          )}

          {/* ── JSON TAB ───────────────────────────── */}
          {activeTab === "json" && (
            <div className="relative">
              <button
                onClick={handleCopyJson}
                className="absolute top-2 right-2 px-3 py-1 text-xs rounded-lg bg-white/10 text-slate-300 hover:bg-white/20 transition-all z-10"
              >
                {jsonCopied ? "✓ Copiado!" : "📋 Copiar"}
              </button>
              <pre className="text-sm text-green-400 font-mono whitespace-pre-wrap max-h-[600px] overflow-auto leading-relaxed">
                {JSON.stringify(data, null, 2)}
              </pre>
            </div>
          )}

          {/* ── EXPORTAR TAB ───────────────────────── */}
          {activeTab === "exportar" && (
            <div className="flex flex-col items-center justify-center py-16 space-y-6">
              <div className="text-center space-y-3 max-w-lg">
                <h3 className="text-2xl font-bold text-white">Pacote Completo (.ZIP)</h3>
                <p className="text-slate-400 text-sm leading-relaxed">
                  Baixe um pacote estruturado contendo todas as imagens originais da página (resolução máxima), o texto e posições em Markdown detalhado, código HTML limpo, e os dados brutos (JSON).
                </p>
              </div>
              
              <button
                onClick={() => handleExport("zip")}
                disabled={exporting === "zip"}
                className="group relative px-8 py-4 bg-gradient-to-r from-blue-600 to-violet-600 rounded-xl font-bold text-white shadow-lg shadow-blue-500/20 hover:shadow-blue-500/40 hover:-translate-y-1 transition-all disabled:opacity-50 disabled:hover:translate-y-0"
              >
                <div className="flex items-center gap-3">
                  <span className="text-2xl">📦</span>
                  <span className="text-lg">{exporting === "zip" ? "Compactando Arquivos..." : "Baixar Pacote Completo"}</span>
                </div>
                {exporting !== "zip" && (
                  <div className="absolute inset-0 rounded-xl bg-white/20 opacity-0 group-hover:opacity-100 transition-opacity" />
                )}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════ */
/* SUB-COMPONENTS                                             */
/* ═══════════════════════════════════════════════════════════ */

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    complete: "bg-green-500/10 text-green-400 border-green-500/20",
    error: "bg-red-500/10 text-red-400 border-red-500/20",
    processing: "bg-blue-500/10 text-blue-400 border-blue-500/20",
    pending: "bg-yellow-500/10 text-yellow-400 border-yellow-500/20",
  };
  return (
    <span className={cn("px-3 py-1 rounded-full text-sm font-medium border", styles[status] || styles.pending)}>
      {status === "complete" ? "✓ Completo" : status === "error" ? "✗ Erro" : status === "processing" ? "⟳ Processando" : status}
    </span>
  );
}

function StatCard({ title, value, icon }: { title: string; value: number; icon: string }) {
  return (
    <div className="glass p-5 rounded-2xl relative overflow-hidden border-t border-t-blue-500/20 shadow-lg">
      <div className="absolute -right-4 -bottom-4 text-7xl opacity-5">{icon}</div>
      <div className="flex items-center gap-3 mb-2">
        <span className="text-slate-400">{icon}</span>
        <h4 className="text-sm font-medium text-slate-400">{title}</h4>
      </div>
      <div className="text-3xl font-bold text-white">{value.toLocaleString()}</div>
    </div>
  );
}

function ContentBlock({ node }: { node: ContentNode }) {
  const tagStyles: Record<string, string> = {
    h1: "text-3xl font-bold text-white mt-8 mb-4",
    h2: "text-2xl font-bold text-white mt-6 mb-3",
    h3: "text-xl font-semibold text-white mt-5 mb-2",
    h4: "text-lg font-semibold text-slate-200 mt-4 mb-2",
    h5: "text-base font-medium text-slate-200 mt-3 mb-1",
    h6: "text-sm font-medium text-slate-300 mt-2 mb-1",
    p: "text-slate-300 leading-relaxed mb-3",
    blockquote: "border-l-4 border-violet-500/50 pl-4 italic text-slate-400 mb-3",
    pre: "bg-black/30 rounded-lg p-4 font-mono text-sm text-green-400 mb-3 overflow-auto",
    ul: "text-slate-300 mb-3",
    ol: "text-slate-300 mb-3",
    table: "text-slate-300 text-sm mb-3",
  };

  if (node.children && node.children.length > 0 && (node.tag === "ul" || node.tag === "ol")) {
    return (
      <ul className={cn(tagStyles[node.tag], node.tag === "ol" ? "list-decimal pl-6" : "list-disc pl-6")}>
        {node.children.map((child, i) => (
          <li key={i} className="mb-1">{child.text}</li>
        ))}
      </ul>
    );
  }

  return (
    <div className={tagStyles[node.tag] || "text-slate-300 mb-2"}>
      {node.text}
    </div>
  );
}

function TreeNode({ node, depth }: { node: StructureNode; depth: number }) {
  const [expanded, setExpanded] = useState(depth < 2);
  const hasChildren = node.children && node.children.length > 0;

  const tagColors: Record<string, string> = {
    div: "text-blue-400", span: "text-cyan-400", p: "text-green-400",
    h1: "text-yellow-400", h2: "text-yellow-400", h3: "text-yellow-300",
    h4: "text-yellow-300", h5: "text-yellow-200", h6: "text-yellow-200",
    a: "text-violet-400", img: "text-pink-400", ul: "text-emerald-400",
    ol: "text-emerald-400", li: "text-emerald-300", section: "text-orange-400",
    article: "text-orange-300", nav: "text-red-400", header: "text-red-300",
    footer: "text-red-300", main: "text-indigo-400", form: "text-rose-400",
    table: "text-teal-400", body: "text-white", html: "text-white",
  };

  return (
    <div style={{ paddingLeft: depth * 16 }}>
      <div
        className="flex items-center gap-1 py-0.5 hover:bg-white/5 rounded cursor-pointer transition-colors"
        onClick={() => hasChildren && setExpanded(!expanded)}
      >
        <span className="w-4 text-center text-xs text-slate-500">
          {hasChildren ? (expanded ? "▼" : "▶") : "·"}
        </span>
        <span className={cn("font-mono", tagColors[node.tag] || "text-slate-400")}>&lt;{node.tag}</span>
        {node.id && <span className="text-orange-300 text-xs">#{node.id}</span>}
        {(node.classes?.length ?? 0) > 0 && <span className="text-slate-500 text-xs">.{node.classes!.slice(0, 2).join(".")}</span>}
        <span className={cn("font-mono", tagColors[node.tag] || "text-slate-400")}>&gt;</span>
        {node.text_preview && <span className="text-slate-600 text-xs truncate ml-2 max-w-[200px]">{node.text_preview}</span>}
      </div>
      {expanded && hasChildren && node.children!.map((child, i) => (
        <TreeNode key={i} node={child} depth={depth + 1} />
      ))}
    </div>
  );
}

function Info({ label, value }: { label: string; value: string | null | undefined }) {
  if (!value) return null;
  return (
    <div>
      <span className="text-slate-500 block text-xs">{label}</span>
      <span className="text-white text-sm break-all">{value}</span>
    </div>
  );
}
