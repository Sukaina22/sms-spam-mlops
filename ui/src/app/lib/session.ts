export const SESSION_KEY = "sms_session_id";

export function getOrCreateSessionId(): string {
  if (typeof window === "undefined") return "";

  let s = window.localStorage.getItem(SESSION_KEY);
  if (!s) {
    s = crypto.randomUUID();
    window.localStorage.setItem(SESSION_KEY, s);
  }
  return s;
}

export function getSessionId(): string {
  if (typeof window === "undefined") return "";
  return window.localStorage.getItem(SESSION_KEY) ?? "";
}
