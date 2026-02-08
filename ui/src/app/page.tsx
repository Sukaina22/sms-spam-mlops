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
  const [userGuess, setUserGuess] = useState<"spam" | "ham" | null>(null); 
  const isCorrectGuess = prediction && userGuess && prediction.label === userGuess;

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
          user_label: userGuess, 
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
    setUserGuess(null);
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
          <div className="flex items-center gap-2">
            <Link
              href="/dashboard"
              className="text-xs rounded-lg bg-slate-900 border border-slate-700 px-3 py-1.5 text-slate-200 hover:bg-slate-800"
            >
              Overview
            </Link>

            <Link
              href="/history"
              className="text-xs rounded-lg bg-slate-900 border border-slate-700 px-3 py-1.5 text-slate-200 hover:bg-slate-800"
            >
              View Session History
            </Link>
          </div>

        </div>
      </header>

      {}
      <div className="flex-1 flex items-center justify-center px-4">
        <div className="w-full max-w-3xl grid gap-6 md:grid-cols-[2fr,1.2fr] items-start mt-8 mb-16">
          {}
          <section className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-xl shadow-slate-950/60">
            <h1 className="text-xl font-semibold mb-1">TRY IT NOW!</h1>
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

            {}
            <div className="mt-4 p-3 rounded-xl border border-slate-800 bg-slate-950/70">
              <p className="text-xs font-medium text-center mb-2">
                🧠 Make a guess before you get the answer!
              </p>
              <p className="text-[11px] text-slate-400 text-center mb-3">
                Do you think this SMS is spam or not? Your guess will be saved to help improve the model.
              </p>

              <div className="flex justify-center gap-3">
                <button
                  type="button"
                  onClick={() => setUserGuess("spam")}
                  className={`px-4 py-2 rounded-lg text-xs font-semibold border transition ${
                    userGuess === "spam"
                      ? "bg-rose-500 text-slate-950 border-rose-400"
                      : "bg-slate-900 text-rose-300 border-rose-500/60 hover:bg-slate-800"
                  }`}
                >
                  🚫 Spam
                </button>
                <button
                  type="button"
                  onClick={() => setUserGuess("ham")}
                  className={`px-4 py-2 rounded-lg text-xs font-semibold border transition ${
                    userGuess === "ham"
                      ? "bg-emerald-500 text-slate-950 border-emerald-400"
                      : "bg-slate-900 text-emerald-300 border-emerald-500/60 hover:bg-slate-800"
                  }`}
                >
                  ✅ Not Spam
                </button>
              </div>

              {userGuess && (
                <p className="mt-2 text-[11px] text-center text-slate-400">
                  You&apos;ve guessed:{" "}
                  <span className="font-semibold">
                    {userGuess === "spam" ? "Spam" : "Not Spam"}
                  </span>
                </p>
              )}
            </div>

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
          {}
          <div className="flex items-center justify-between gap-4">
            <div className="flex flex-col">
              <span className="text-xs text-slate-400">Model prediction</span>
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
              <span className="text-xs text-slate-400">Confidence (spam)</span>
              <p className="text-lg font-semibold">
                {(prediction.confidence * 100).toFixed(1)}%
              </p>
              <p className="text-[11px] text-slate-500">
                Higher = model is more sure it&apos;s spam.
              </p>
            </div>
          </div>

          {}
          {userGuess && (
            <div className="mt-4 rounded-xl border border-slate-800 bg-slate-950/70 p-3">
              <div className="flex items-center justify-between gap-3">
                <div className="text-xs">
                  <p className="text-slate-400 mb-1">Your guess</p>
                  <span
                    className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-[11px] font-semibold border ${
                      userGuess === "spam"
                        ? "bg-rose-500/10 text-rose-300 border-rose-500/50"
                        : "bg-emerald-500/10 text-emerald-300 border-emerald-500/50"
                    }`}
                  >
                    {userGuess === "spam" ? "🚫 Spam" : "✅ Not Spam"}
                  </span>
                </div>

                <div className="text-right text-xs">
                  {isCorrectGuess ? (
                    <p className="text-emerald-400 font-medium">
                      🎉 You guessed it right!
                    </p>
                  ) : (
                    <p className="text-rose-300 font-medium">
                      🤖 The model disagreed with your guess.
                    </p>
                  )}
                  <p className="text-[11px] text-slate-500 mt-1">
                    We store both to analyze where humans and the model differ.
                  </p>
                </div>
              </div>
            </div>
          )}

          {}
          <div className="border-t border-slate-800 pt-3 mt-3">
            <p className="text-xs text-slate-400 mb-1">What this means</p>
            <p className="text-xs text-slate-300">
              The model was trained on real SMS messages and outputs whether a message
              looks like spam or not, along with how confident it is that the message
              is spam. Your guess helps us understand how humans perceive the same
              SMS.
            </p>
          </div>
        </>
      )}
          </section>
        </div>
      </div>
    </main>
  );
}
