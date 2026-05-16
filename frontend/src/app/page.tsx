"use client";

import { useState } from "react";

export default function Home() {
  const [objective, setObjective] = useState("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

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
      setResult(data);
    } catch (error) {
      console.error("Error generating design:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center p-8 bg-gray-50">
      <header className="w-full max-w-4xl mb-12 text-center">
        <h1 className="text-4xl font-bold text-blue-900">ArchAI 🚀</h1>
        <p className="text-lg text-gray-600 mt-2">Enterprise AI Solution Architect</p>
      </header>

      <section className="w-full max-w-4xl bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        <form onSubmit={handleSubmit} className="space-y-4">
          <label className="block text-sm font-medium text-gray-700">
            What is your architectural objective?
          </label>
          <textarea
            className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none h-32"
            placeholder="e.g., Integrate our CRM with a new data lake for real-time analytics..."
            value={objective}
            onChange={(e) => setObjective(e.target.value)}
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
          >
            {loading ? "Designing..." : "Generate Design"}
          </button>
        </form>
      </section>

      {result && (
        <section className="w-full max-w-4xl mt-8 bg-white p-6 rounded-xl shadow-sm border border-gray-200">
          <h2 className="text-2xl font-bold mb-4">{result.title}</h2>
          <div className="prose max-w-none">
            <h3 className="text-lg font-semibold">High Level Design</h3>
            <p className="text-gray-700 mb-4">{result.high_level_design}</p>

            <h3 className="text-lg font-semibold">Compliance</h3>
            <p className="text-green-700 mb-4">{result.compliance_summary}</p>

            <h3 className="text-lg font-semibold">Confidence Score</h3>
            <div className="w-full bg-gray-200 rounded-full h-2.5 mb-6">
              <div
                className="bg-blue-600 h-2.5 rounded-full"
                style={{ width: `${result.confidence_score}%` }}
              ></div>
            </div>
          </div>
        </section>
      )}
    </main>
  );
}
