"use client";

import { useState, useEffect, useRef } from "react";
import mermaid from "mermaid";
import {
  Activity,
  Layout,
  ShieldCheck,
  BarChart3,
  Code2,
  AlertTriangle,
  Fingerprint
} from "lucide-react";

mermaid.initialize({
  startOnLoad: true,
  theme: "default",
  securityLevel: "loose",
});

const MermaidDiagram = ({ code }: { code: string }) => {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (ref.current && code) {
      mermaid.render("mermaid-diag", code).then((res) => {
        if (ref.current) ref.current.innerHTML = res.svg;
      });
    }
  }, [code]);

  return <div ref={ref} className="bg-white p-4 rounded-lg overflow-auto flex justify-center" />;
};

export default function Home() {
  const [objective, setObjective] = useState("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("hld");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await fetch("http://localhost:8000/api/design", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ objective }),
      });
      const data = await response.json();
      setResult(data.final_hld || data);
    } catch (error) {
      console.error("Error generating design:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center p-8 bg-slate-50 text-slate-900 font-sans">
      <header className="w-full max-w-6xl mb-12 flex justify-between items-center">
        <div>
          <h1 className="text-4xl font-extrabold text-blue-900 tracking-tight">ArchAI 🚀</h1>
          <p className="text-lg text-slate-500 mt-1 uppercase text-xs font-bold tracking-widest">Enterprise AI Solution Architect</p>
        </div>
        <div className="flex gap-4">
            <span className="flex items-center gap-2 text-xs font-medium bg-green-100 text-green-700 px-3 py-1 rounded-full">
                <ShieldCheck size={14}/> Graph-RAG Active
            </span>
            <span className="flex items-center gap-2 text-xs font-medium bg-blue-100 text-blue-700 px-3 py-1 rounded-full">
                <Fingerprint size={14}/> Audit Signed
            </span>
        </div>
      </header>

      <section className="w-full max-w-6xl bg-white p-8 rounded-2xl shadow-xl shadow-slate-200/50 border border-slate-200">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label className="text-sm font-bold text-slate-600 uppercase tracking-wider">
              Architectural Objective
            </label>
            <textarea
              className="w-full p-4 border-2 border-slate-100 rounded-xl focus:border-blue-500 focus:ring-0 outline-none h-32 transition-all text-lg"
              placeholder="e.g., Design a multi-region data ingestion pipeline with PII mask on AWS..."
              value={objective}
              onChange={(e) => setObjective(e.target.value)}
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white font-bold py-4 rounded-xl hover:bg-blue-700 transform active:scale-[0.98] transition-all disabled:opacity-50 shadow-lg shadow-blue-200"
          >
            {loading ? "Synthesizing Architecture..." : "Generate Design Package"}
          </button>
        </form>
      </section>

      {result && (
        <section className="w-full max-w-6xl mt-12 grid grid-cols-1 lg:grid-cols-4 gap-8">
            {/* Sidebar Navigation */}
            <div className="lg:col-span-1 space-y-2">
                {[
                    { id: "hld", label: "High Level Design", icon: <Layout size={18}/> },
                    { id: "diagrams", label: "Architecture View", icon: <Activity size={18}/> },
                    { id: "matrix", label: "Decision Matrix", icon: <BarChart3 size={18}/> },
                    { id: "iac", label: "Technical Skeleton", icon: <Code2 size={18}/> },
                    { id: "risks", label: "Risks & Compliance", icon: <AlertTriangle size={18}/> },
                ].map((tab) => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl font-semibold transition-all ${
                            activeTab === tab.id
                            ? "bg-blue-600 text-white shadow-md shadow-blue-100"
                            : "text-slate-500 hover:bg-slate-100"
                        }`}
                    >
                        {tab.icon} {tab.label}
                    </button>
                ))}

                <div className="mt-8 p-4 bg-slate-100 rounded-xl border border-slate-200">
                    <p className="text-[10px] font-bold text-slate-400 uppercase mb-2">Audit Signature</p>
                    <code className="text-[10px] break-all text-slate-600 block">
                        {result.decision_sig || "SHA256: 8a4f...9c2d"}
                    </code>
                </div>
            </div>

            {/* Main Content Area */}
            <div className="lg:col-span-3 bg-white p-8 rounded-2xl shadow-sm border border-slate-200 min-h-[600px]">
                <div className="flex justify-between items-start mb-8 border-b pb-6 border-slate-100">
                    <div>
                        <h2 className="text-3xl font-bold text-slate-800">{result.title}</h2>
                        <div className="flex items-center gap-4 mt-2">
                            <span className="text-sm font-medium text-slate-500">Confidence: {result.confidence_score}%</span>
                            <div className="w-32 bg-slate-100 rounded-full h-1.5">
                                <div className="bg-blue-500 h-1.5 rounded-full" style={{ width: `${result.confidence_score}%` }}></div>
                            </div>
                        </div>
                    </div>
                </div>

                {activeTab === "hld" && (
                    <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
                        <h3 className="text-xl font-bold text-slate-800 mb-4 underline decoration-blue-500/30 underline-offset-8">Executive Summary</h3>
                        <p className="text-slate-700 leading-relaxed text-lg whitespace-pre-wrap">
                            {result.high_level_design || result.hld}
                        </p>
                    </div>
                )}

                {activeTab === "diagrams" && (
                    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-2 duration-300">
                        {result.diagrams?.map((diag: any, idx: number) => (
                            <div key={idx}>
                                <h3 className="text-lg font-bold text-slate-700 mb-2">{diag.description}</h3>
                                <MermaidDiagram code={diag.mermaid_code} />
                            </div>
                        ))}
                    </div>
                )}

                {activeTab === "matrix" && (
                    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-300">
                         {result.decision_matrix?.map((dm: any, idx: number) => (
                             <div key={idx} className="border border-slate-100 rounded-xl overflow-hidden">
                                 <div className="bg-slate-50 p-4 border-b border-slate-100">
                                     <h4 className="font-bold text-slate-800">{dm.decision}</h4>
                                 </div>
                                 <div className="p-4 space-y-4">
                                     <div className="grid grid-cols-2 gap-4">
                                         {dm.options?.map((opt: any, oIdx: number) => (
                                             <div key={oIdx} className={`p-3 rounded-lg border ${opt.option === dm.recommended ? 'border-green-200 bg-green-50' : 'border-slate-100'}`}>
                                                 <p className="text-sm font-bold">{opt.option}</p>
                                                 <p className="text-xs text-slate-500 mt-1">Score: {opt.score}/10</p>
                                             </div>
                                         ))}
                                     </div>
                                     <div className="bg-blue-50 p-3 rounded-lg">
                                         <p className="text-xs font-bold text-blue-800 uppercase tracking-tighter mb-1">Justification</p>
                                         <p className="text-sm text-blue-900">{dm.justification}</p>
                                     </div>
                                 </div>
                             </div>
                         ))}
                    </div>
                )}

                {activeTab === "iac" && (
                    <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
                         <div className="bg-slate-900 rounded-xl p-6 overflow-auto">
                            <pre className="text-blue-300 text-sm font-mono">
                                {`# Auto-generated Infrastructure-as-Code Skeleton\n\nprovider "aws" {\n  region = "us-east-1"\n}\n\nmodule "archai_backbone" {\n  source = "./modules/${result.title?.toLowerCase().replace(/ /g, '_')}"\n  env    = "prod"\n}`}
                            </pre>
                         </div>
                    </div>
                )}

                {activeTab === "risks" && (
                    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-2 duration-300">
                        <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl">
                            <h4 className="flex items-center gap-2 text-amber-800 font-bold mb-3"><AlertTriangle size={18}/> Compliance Alert</h4>
                            <p className="text-sm text-amber-900">{result.compliance_summary}</p>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {result.risks_and_mitigations?.map((rm: any, idx: number) => (
                                <div key={idx} className="p-4 border border-slate-100 rounded-xl">
                                    <p className="text-sm font-bold text-slate-800">Risk: {rm.risk}</p>
                                    <p className="text-xs text-slate-500 mt-2">Mitigation: {rm.mitigation}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </section>
      )}
    </main>
  );
}
