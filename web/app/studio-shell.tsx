"use client";

import { useMemo, useState } from "react";

type Operation = "ideas" | "research" | "script" | "storyboard" | "visual_code" | "package" | "revise";

const tasks: { id: Operation; title: string; description: string; label: string }[] = [
  { id: "ideas", title: "Find the angle", description: "Turn a broad subject into a strong explainer concept.", label: "IDEAS" },
  { id: "research", title: "Research brief", description: "Search the web and build a cited evidence brief.", label: "RESEARCH" },
  { id: "script", title: "Write the script", description: "Build a narration-ready documentary script.", label: "SCRIPT" },
  { id: "storyboard", title: "Visual storyboard", description: "Plan diagrams, animation, motion and scenes.", label: "VISUALS" },\n  { id: "visual_code", title: "Generate motion code", description: "Create a self-contained HTML/SVG animation for local rendering.", label: "CODE" },
  { id: "package", title: "YouTube package", description: "Titles, thumbnail concepts, description and chapters.", label: "PUBLISH" },
  { id: "revise", title: "Revise material", description: "Improve existing writing without losing accuracy.", label: "REVISE" },
];

export default function StudioShell() {
  const [operation, setOperation] = useState<Operation>("research");
  const [topic, setTopic] = useState("");
  const [context, setContext] = useState("");
  const [direction, setDirection] = useState("");
  const [language, setLanguage] = useState("Hinglish (Roman script)");
  const [format, setFormat] = useState("Long-form");
  const [duration, setDuration] = useState("8–10 minutes");
  const [result, setResult] = useState("");
  const [model, setModel] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [copied, setCopied] = useState(false);

  const selected = useMemo(() => tasks.find(t => t.id === operation)!, [operation]);

  async function generate() {
    if (topic.trim().length < 3) {
      setError("Enter a topic or paste a brief first.");
      return;
    }
    setBusy(true);
    setError("");
    setCopied(false);
    try {
      const response = await fetch("/api/ai/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ operation, topic, context, direction, language, format, duration }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Generation failed.");
      setResult(data.text);
      setModel(data.model || "");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Generation failed.");
    } finally {
      setBusy(false);
    }
  }

  async function copyResult() {
    await navigator.clipboard.writeText(result);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1600);
  }

  function downloadHandoff() {
    const payload = {
      schema: "hindi-explainer-studio.handoff.v1",
      createdAt: new Date().toISOString(),
      project: { topic: topic.trim(), operation, language, format, duration },
      output: result,
      localProduction: {
        nextStep: "Save this handoff inside the local studio project folder. Keep audio recording, source assets, renderer and final video on the local computer.",
        localStudioUrl: "http://127.0.0.1:5173",
      },
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "hindi-studio-handoff.json";
    anchor.click();
    URL.revokeObjectURL(url);
  }

  async function logout() {
    await fetch("/api/auth/logout", { method: "POST" });
    window.location.reload();
  }

  return (
    <main className="studio">
      <aside className="sidebar">
        <div className="brand-row"><div className="brand-mark small">H<span>·</span>E</div><div><strong>Hindi Explainer</strong><small>STUDIO / PRIVATE</small></div></div>
        <div className="side-label">WORKSPACE</div>
        <button className="nav-item active"><span className="nav-dot" /> Production desk</button>
        <div className="side-label second">YOUR PIPELINE</div>
        {tasks.map(task => (
          <button key={task.id} className={"nav-item " + (operation === task.id ? "chosen" : "")} onClick={() => setOperation(task.id)}>
            <span className="nav-symbol">{task.label.slice(0, 1)}</span><span>{task.title}</span>
          </button>
        ))}
        <div className="sidebar-bottom">
          <div className="local-card"><span className="status-dot" /><div><b>Local production</b><p>Runs on your computer</p></div></div>
          <a className="local-link" href="http://127.0.0.1:5173" target="_blank" rel="noreferrer">Open local studio <span>↗</span></a>
          <button className="logout-button" onClick={logout}>Sign out</button>
        </div>
      </aside>

      <section className="main-panel">
        <header className="topbar">
          <div><span className="breadcrumb">WORKSPACE</span><span className="crumb-sep">/</span><b>Production desk</b></div>
          <div className="top-status"><span className="status-dot" /> AI workspace ready</div>
        </header>

        <div className="content">
          <div className="page-heading">
            <div><p className="eyebrow">IDEA → EVIDENCE → STORY → SCREEN</p><h1>Make something<br /><em>worth understanding.</em></h1><p className="intro">An AI-assisted production desk for clear, evidence-led explainers. Use the cloud for thinking; use your PC for making.</p></div>
            <div className="edition"><span>EDITION 01</span><b>DOCUMENTARY<br />EXPLAINER</b><small>HINDI / HINGLISH</small></div>
          </div>

          <div className="workspace-grid">
            <section className="composer card">
              <div className="section-head"><div><p className="eyebrow">01 / CREATE</p><h2>{selected.title}</h2></div><span className="task-tag">{selected.label}</span></div>
              <p className="task-description">{selected.description}</p>

              <label className="field-label" htmlFor="topic">Topic or creative brief</label>
              <textarea id="topic" className="topic-input" value={topic} onChange={e => setTopic(e.target.value)} placeholder="Example: UPI ke peeche actual payment network kaise kaam karta hai? Start with a chai-shop QR payment and explain every system involved." rows={5} />

              <div className="control-grid">
                <div><label className="field-label" htmlFor="language">Language</label><select id="language" value={language} onChange={e => setLanguage(e.target.value)}><option>Hinglish (Roman script)</option><option>Hindi (Devanagari)</option><option>English</option></select></div>
                <div><label className="field-label" htmlFor="format">Format</label><select id="format" value={format} onChange={e => setFormat(e.target.value)}><option>Long-form</option><option>YouTube Short</option><option>Documentary</option></select></div>
                <div><label className="field-label" htmlFor="duration">Target duration</label><select id="duration" value={duration} onChange={e => setDuration(e.target.value)}><option>30–45 seconds</option><option>60 seconds</option><option>3–5 minutes</option><option>8–10 minutes</option><option>10–12 minutes</option><option>15–20 minutes</option></select></div>
              </div>

              <details className="advanced">
                <summary>Additional context and direction <span>+</span></summary>
                <label className="field-label" htmlFor="context">Existing script, notes or source material</label>
                <textarea id="context" value={context} onChange={e => setContext(e.target.value)} rows={4} placeholder="Paste previous research, claims, references or a draft…" />
                <label className="field-label" htmlFor="direction">What should the model focus on?</label>
                <textarea id="direction" value={direction} onChange={e => setDirection(e.target.value)} rows={2} placeholder="Tone, narrative approach, audience knowledge, exclusions…" />
              </details>

              <div className="composer-footer"><span className="privacy-note"><span className="lock-icon">◆</span> Sent to OpenAI from the server</span><button className="primary-button generate" onClick={generate} disabled={busy}>{busy ? <><span className="spinner" /> Working…</> : <>Generate with GPT <span>↗</span></>}</button></div>
              {error && <p className="error-text" role="alert">{error}</p>}
            </section>

            <aside className="workflow card">
              <p className="eyebrow">02 / THE WORKFLOW</p><h3>Cloud brain.<br />Local production.</h3>
              <div className="workflow-step"><span>01</span><div><b>Research & writing</b><p>GPT drafts ideas, evidence briefs, scripts and visual plans.</p><small className="cloud-chip">CLOUD / OPENAI API</small></div></div>
              <div className="workflow-step"><span>02</span><div><b>Review & export</b><p>Review the output, then export a portable handoff file.</p><small className="cloud-chip">BROWSER / DOWNLOAD</small></div></div>
              <div className="workflow-step"><span>03</span><div><b>Build on your PC</b><p>Record voice, manage source assets, run the renderer and FFmpeg locally.</p><small className="local-chip">LOCAL / WINDOWS PC</small></div></div>
              <div className="workflow-foot">Your computer stays private. The hosted app cannot browse its folders or execute local programs.</div>
            </aside>
          </div>

          <section className="output-card card">
            <div className="section-head"><div><p className="eyebrow">03 / OUTPUT</p><h2>{result ? "Your working draft" : "The next useful thing starts here"}</h2></div>{result && <div className="output-actions"><button className="secondary-button" onClick={copyResult}>{copied ? "Copied" : "Copy"}</button><button className="secondary-button export" onClick={downloadHandoff}>{operation === "visual_code" ? "Download scene.html ↓" : "Export handoff ↓"}</button></div>}</div>
            {result ? <><div className="result-meta"><span>GENERATED WITH {model || "OPENAI"}</span><span>{selected.label} · {language}</span></div><pre className="result-text">{result}</pre></> : <div className="empty-output"><div className="empty-icon">✳</div><div><b>Waiting for your first generation</b><p>Choose a workflow, describe the topic and run GPT. Research tasks use web search and must include source URLs. Motion code is downloaded as a standalone HTML file; inspect it before running locally.</p></div></div>}
          </section>
          <footer className="page-footer"><span>HINDI EXPLAINER STUDIO</span><span>THINK WITH CARE. MAKE IT LOCALLY.</span></footer>
        </div>
      </section>
    </main>
  );
}
