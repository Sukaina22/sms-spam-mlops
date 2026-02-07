"use client";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL;


import { useEffect, useState } from "react";
import Link from "next/link";
import { getOrCreateSessionId } from "./lib/session";

type ApiResponse = {
  label: string;
  confidence: number;
  session_id: string;
};

type PredictionState =
  | {
      label: "spam" | "ham";
      confidence: number;
    }
  | null;

export default function HomePage() {
  const [message, setMessage] = useState("");
  const [prediction, setPrediction] = useState<PredictionState>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string>("");

  useEffect(() => {
    const id = getOrCreateSessionId();
    setSessionId(id);
  }, []);

  const handlePredict = async () => {
    setError(null);
    setPrediction(null);

    if (!message.trim()) {
      setError("Please enter an SMS message first.");
      return;
    }

    try {
      setLoading(true);

      const res = await fetch(`${API_BASE}/predict`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: message,
          session_id: sessionId,
        }),
      });

      if (!res.ok) {
        throw new Error("API error");
      }

      const data: ApiResponse = await res.json();

      setPrediction({
        label: data.label === "spam" ? "spam" : "ham",
        confidence: data.confidence,
      });

      if (data.session_id && data.session_id !== sessionId) {
        localStorage.setItem("sms_session_id", data.session_id);
        setSessionId(data.session_id);
      }
    } catch (err: any) {
      setError(err.message ?? "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setMessage("");
    setPrediction(null);
    setError(null);
  };

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

          {}
          <Link
            href="/history"
            className="text-xs rounded-lg bg-slate-900 border border-slate-700 px-3 py-1.5 text-slate-200 hover:bg-slate-800"
          >
            View Session History
          </Link>
        </div>
      </header>

      {}
      <div className="flex-1 flex items-center justify-center px-4">
        <div className="w-full max-w-3xl grid gap-6 md:grid-cols-[2fr,1.2fr] items-start mt-8 mb-16">
          {}
          <section className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-xl shadow-slate-950/60">
            <h1 className="text-xl font-semibold mb-1">Test an SMS</h1>
            <p className="text-sm text-slate-400 mb-4">
              Paste any SMS message below and let the model decide whether it&apos;s
              spam or not.
            </p>

            <label className="block text-xs font-medium text-slate-400 mb-1">
              SMS Content
            </label>
            <textarea
              className="w-full h-40 rounded-xl bg-slate-950 border border-slate-800 px-3 py-2 text-sm text-slate-100 outline-none focus:ring-2 focus:ring-emerald-500/60 focus:border-emerald-500/60 resize-none"
              placeholder="e.g. Congratulations! You have won a FREE ticket to..."
              value={message}
              onChange={(e) => setMessage(e.target.value)}
            />

            {error && <p className="mt-2 text-xs text-rose-400">{error}</p>}

            <div className="mt-4 flex justify-between items-center gap-3">
              <button
                onClick={handlePredict}
                disabled={loading}
                className="inline-flex items-center justify-center rounded-xl bg-emerald-500 px-4 py-2 text-sm font-medium text-slate-950 hover:bg-emerald-400 disabled:bg-emerald-700/60 disabled:cursor-not-allowed transition"
              >
                {loading ? "Analyzing..." : "Analyze SMS"}
              </button>
              <button
                type="button"
                onClick={handleClear}
                className="text-xs text-slate-400 hover:text-slate-200 underline-offset-2 hover:underline"
              >
                Clear
              </button>
            </div>
          </section>

          {}
          <section className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 flex flex-col gap-4 shadow-xl shadow-slate-950/60">
            <h2 className="text-sm font-semibold">Prediction</h2>

            {!prediction && (
              <p className="text-xs text-slate-400">
                No prediction yet. Submit an SMS to see the model&apos;s decision,
                confidence score, and spam probability.
              </p>
            )}

            {prediction && (
              <>
                <div className="flex items-center justify-between">
                  <div className="flex flex-col">
                    <span className="text-xs text-slate-400">
                      Classification
                    </span>
                    <span
                      className={`mt-1 inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-semibold ${
                        prediction.label === "spam"
                          ? "bg-rose-500/10 text-rose-300 border border-rose-500/40"
                          : "bg-emerald-500/10 text-emerald-300 border border-emerald-500/40"
                      }`}
                    >
                      <span className="inline-block h-2 w-2 rounded-full bg-current" />
                      {prediction.label === "spam" ? "Spam" : "Not Spam"}
                    </span>
                  </div>
                  <div className="text-right">
                    <span className="text-xs text-slate-400">
                      Confidence (spam)
                    </span>
                    <p className="text-lg font-semibold">
                      {(prediction.confidence * 100).toFixed(1)}%
                    </p>
                  </div>
                </div>

                <div className="border-t border-slate-800 pt-3">
                  <p className="text-xs text-slate-400 mb-1">
                    Explanation (placeholder)
                  </p>
                  <p className="text-xs text-slate-300">
                    Later you can highlight suspicious words or show model
                    explanations here. For now we only show the prediction and
                    spam probability.
                  </p>
                </div>
              </>
            )}

            <div className="mt-auto pt-2 border-t border-slate-900">
              <p className="text-[11px] text-slate-500">
                Roadmap: feedback buttons, history, user login, model
                versioning, and analytics dashboard will be added on separate
                pages.
              </p>
            </div>
          </section>
        </div>
      </div>
    </main>
  );
}
