"use client";

import { FormEvent, useState } from "react";

export default function LoginForm() {
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Sign in failed.");
      window.location.reload();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not sign in.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="login-wrap">
      <div className="login-card">
        <div className="brand-mark">H<span>·</span>E</div>
        <p className="eyebrow">PRIVATE WORKSPACE</p>
        <h1>Hindi Explainer<br />Studio</h1>
        <p className="muted">Research, story development and production planning, in one place.</p>
        <form onSubmit={submit} className="login-form">
          <label htmlFor="password">Studio password</label>
          <input id="password" type="password" autoComplete="current-password" value={password} onChange={e => setPassword(e.target.value)} required placeholder="Enter your access password" />
          <button className="primary-button" disabled={busy}>{busy ? "Signing in…" : "Open studio"} <span>→</span></button>
        </form>
        {error && <p className="error-text" role="alert">{error}</p>}
        <p className="tiny-note">Single-owner access · Your OpenAI key stays on the server</p>
      </div>
    </main>
  );
}
