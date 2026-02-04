// app/history/page.tsx
"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getSessionId } from "../lib/session";

const API_BASE = "http://127.0.0.1:8000";

type HistoryItem = {
  id: number;
  sms_text: string;
  label: string;
  confidence: number;
  created_at: string;
};

export default function HistoryPage() {
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [noSession, setNoSession] = useState(false);

  useEffect(() => {
    const sessionId = getSessionId();
    if (!sessionId) {
      setNoSession(true);
      setLoading(false);
      return;
    }

    fetch(`${API_BASE}/history/${sessionId}`)
      .then((res) => res.json())
      .then((data) => setItems(data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100">
      <div className="max-w-4xl mx-auto py-10 px-4">
        <header className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-semibold">Session History</h1>
            <p className="text-sm text-slate-400">
              All SMS analyses for this browser session.
            </p>
          </div>
          <Link
            href="/"
            className="rounded-md bg-slate-800 px-4 py-2 text-sm hover:bg-slate-700"
          >
            ← Back to Analyzer
          </Link>
        </header>

        {loading && <p className="text-sm text-slate-400">Loading…</p>}

        {noSession && (
          <p className="text-sm text-slate-400">
            No session found. Go back, analyze an SMS, then return here.
          </p>
        )}

        {!loading && !noSession && items.length === 0 && (
          <p className="text-sm text-slate-400">
            No history yet. Analyze some SMS messages first.
          </p>
        )}

        {items.length > 0 && (
          <div className="bg-slate-900 rounded-xl p-6">
            <table className="w-full text-sm border-collapse">
              <thead className="text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="text-left py-2 pr-3">Time</th>
                  <th className="text-left py-2 pr-3">SMS</th>
                  <th className="text-left py-2 pr-3">Label</th>
                  <th className="text-left py-2 pr-3">Confidence</th>
                </tr>
              </thead>
              <tbody>
                {items.map((item) => (
                  <tr
                    key={item.id}
                    className="border-b border-slate-800/60 align-top"
                  >
                    <td className="py-2 pr-3 text-slate-400 whitespace-nowrap">
                      {new Date(item.created_at).toLocaleString()}
                    </td>
                    <td className="py-2 pr-3 max-w-md">
                      <div className="line-clamp-3 text-slate-100">
                        {item.sms_text}
                      </div>
                    </td>
                    <td className="py-2 pr-3">
                      <span
                        className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                          item.label.toLowerCase() === "spam"
                            ? "bg-rose-500/20 text-rose-300"
                            : "bg-emerald-500/20 text-emerald-300"
                        }`}
                      >
                        {item.label}
                      </span>
                    </td>
                    <td className="py-2 pr-3 text-slate-100">
                      {(item.confidence * 100).toFixed(1)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </main>
  );
}
