"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL;

type StatsResponse = {
  total_predictions: number;
  spam_count: number;
  ham_count: number;
  spam_rate: number;
  last_24h_predictions: number;
  unique_sessions: number;
  with_user_label: number;
  user_model_agreement: number;
  user_model_disagreement: number;
};

export default function DashboardPage() {
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch(`${API_BASE}/stats`);
        if (!res.ok) throw new Error("Failed to load stats");
        const data: StatsResponse = await res.json();
        setStats(data);
      } catch (err: any) {
        setError(err.message ?? "Something went wrong");
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  const spamPercentage = stats ? (stats.spam_rate * 100).toFixed(1) : "0.0";
  const hamPercentage = stats
    ? (100 - stats.spam_rate * 100).toFixed(1)
    : "0.0";

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {}
      <header className="w-full border-b border-slate-800 bg-slate-950/90 backdrop-blur sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-xl bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-300 font-bold text-sm">
              SMS
            </div>
            <div>
              <p className="font-semibold text-sm">Spam Guardian</p>
              <p className="text-xs text-slate-400">
                ML-powered SMS spam detector
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Link
              href="/"
              className="text-xs rounded-lg bg-slate-900 border border-slate-700 px-3 py-1.5 text-slate-200 hover:bg-slate-800"
            >
              Test SMS
            </Link>
            <Link
              href="/history"
              className="text-xs rounded-lg bg-slate-900 border border-slate-700 px-3 py-1.5 text-slate-200 hover:bg-slate-800"
            >
              Session History
            </Link>
          </div>
        </div>
      </header>

      <div className="flex-1 px-4">
        <div className="max-w-5xl mx-auto mt-8 mb-16">
          <h1 className="text-xl font-semibold mb-1">
            Overview &amp; Statistics
          </h1>
          <p className="text-sm text-slate-400 mb-6">
            High-level view of how the SMS spam detector is being used.
          </p>

          {loading && (
            <p className="text-sm text-slate-400">Loading statistics…</p>
          )}
          {error && (
            <p className="text-sm text-rose-400 mb-4">
              Failed to load stats: {error}
            </p>
          )}

          {stats && (
            <>
              {}
              <div className="grid gap-4 md:grid-cols-4 mb-6">
                <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4">
                  <p className="text-[11px] text-slate-400 mb-1">
                    Total predictions
                  </p>
                  <p className="text-2xl font-semibold">
                    {stats.total_predictions}
                  </p>
                  <p className="text-[11px] text-slate-500 mt-1">
                    All SMS analyzed so far.
                  </p>
                </div>

                <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4">
                  <p className="text-[11px] text-slate-400 mb-1">
                    Unique users
                  </p>
                  <p className="text-2xl font-semibold">
                    {stats.unique_sessions}
                  </p>
                  <p className="text-[11px] text-slate-500 mt-1">
                    Number of user so far.
                  </p>
                </div>

                <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4">
                  <p className="text-[11px] text-slate-400 mb-1">
                    Last 24 hours
                  </p>
                  <p className="text-2xl font-semibold">
                    {stats.last_24h_predictions}
                  </p>
                  <p className="text-[11px] text-slate-500 mt-1">
                    New predictions in the past day.
                  </p>
                </div>

                <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4">
                  <p className="text-[11px] text-slate-400 mb-1">
                    Feedback collected
                  </p>
                  <p className="text-2xl font-semibold">
                    {stats.with_user_label}
                  </p>
                  <p className="text-[11px] text-slate-500 mt-1">
                    Predictions where users made a guess.
                  </p>
                </div>
              </div>

              {}
              <div className="grid gap-4 md:grid-cols-[2fr,1.3fr] mb-6">
                <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4">
                  <p className="text-sm font-semibold mb-2">
                    Spam vs. Not Spam distribution
                  </p>

                  <div className="flex justify-between text-xs text-slate-400 mb-2">
                    <span>Spam ({spamPercentage}%)</span>
                    <span>Not Spam ({hamPercentage}%)</span>
                  </div>

                  {}
                  <div className="w-full h-3 rounded-full bg-slate-800 overflow-hidden">
                    <div
                      className="h-full bg-rose-500/80"
                      style={{ width: `${stats.spam_rate * 100}%` }}
                    ></div>
                  </div>

                  <div className="flex justify-between text-[11px] text-slate-500 mt-2">
                    <span>{stats.spam_count} spam messages</span>
                    <span>{stats.ham_count} not spam</span>
                  </div>
                </div>

                {}
                <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4">
                  <p className="text-sm font-semibold mb-2">
                    User vs model agreement
                  </p>

                  {stats.with_user_label === 0 ? (
                    <p className="text-xs text-slate-400">
                      No user guesses recorded yet. Ask users to make guesses to
                      see how often they agree with the model.
                    </p>
                  ) : (
                    <>
                      <p className="text-2xl font-semibold mb-1">
                        {stats.user_model_agreement} /
                        {stats.with_user_label}
                      </p>
                      <p className="text-xs text-slate-400 mb-3">
                        predictions where the user guess matched the model.
                      </p>

                      <div className="w-full h-3 rounded-full bg-slate-800 overflow-hidden mb-2">
                        <div
                          className="h-full bg-emerald-500/80"
                          style={{
                            width: `${
                              (stats.user_model_agreement /
                                Math.max(stats.with_user_label, 1)) *
                              100
                            }%`,
                          }}
                        ></div>
                      </div>

                      <p className="text-[11px] text-slate-500">
                        Disagreements: {stats.user_model_disagreement}
                      </p>
                    </>
                  )}
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </main>
  );
}
