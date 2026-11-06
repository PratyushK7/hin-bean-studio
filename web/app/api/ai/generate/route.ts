import OpenAI from "openai";
import { NextRequest, NextResponse } from "next/server";
import { hasValidSession } from "@/lib/auth";

export const runtime = "nodejs";
export const maxDuration = 120;

const OPERATIONS = ["ideas", "research", "script", "storyboard", "visual_code", "package", "revise"] as const;
type Operation = (typeof OPERATIONS)[number];

const OPERATION_GUIDANCE: Record<Operation, string> = {
  ideas: "Generate original video concepts. For each, state the central question, audience promise, narrative engine, surprising insight, visual potential and why it deserves a video. Rank the strongest ideas.",
  research: "Create a research brief. You MUST use web search. Separate established facts, disputed or uncertain points, and open questions. Cite source URLs next to factual claims and include publisher and publication date when available. Prefer primary sources, official datasets, peer-reviewed research and reputable reporting. Never invent citations or statistics.",
  script: "Write a narration-ready documentary explainer script. Start with a concrete scene or question, build a causal explanation, explain necessary terms, include counterpoints and uncertainty, then land a clear conclusion. Do not pad. Make spoken language natural rather than essay-like.",
  storyboard: "Turn the supplied script or brief into a scene-by-scene hybrid storyboard. Prefer original code-generated diagrams, charts, maps, timelines and mechanism animations when these clarify the idea. For every scene provide narration cue, visual, motion, on-screen text, assets/data required and approximate duration. Do not invent factual visuals.",
  visual_code: "Generate a complete, self-contained HTML motion-graphics scene as raw HTML source only (no Markdown fences and no prose outside code). Use inline CSS, SVG and vanilla JavaScript; no external libraries, CDNs, network calls, cookies, localStorage, filesystem access, subprocesses or credentials. Make it deterministic, resolution-aware and suitable for capture by a local Playwright/FFmpeg workflow. Include clear comments, a fixed-duration timeline, accessible labels where practical, and a visible fallback when animation is disabled. Use fictional/sample values unless sourced data is supplied. If the user asks for APIs from a local renderer not documented in the prompt, do not invent them; output a standalone HTML scene and state integration assumptions in HTML comments.",
  package: "Create a YouTube packaging set: title options, thumbnail concepts, description, chapter suggestions, pinned comment and search phrases. Keep claims accurate and avoid clickbait that overpromises.",
  revise: "Revise the supplied material to match the requested direction. Preserve accurate claims and useful nuance. Explain major structural changes briefly, then provide the complete revised version.",
};

function errorResponse(message: string, status: number) {
  return NextResponse.json({ error: message }, {
    status,
    headers: { "Cache-Control": "no-store" },
  });
}

export async function POST(request: NextRequest) {
  const origin = request.headers.get("origin");
  if (origin && origin !== request.nextUrl.origin) {
    return errorResponse("Cross-origin request blocked.", 403);
  }
  if (!(await hasValidSession())) {
    return errorResponse("Your studio session has expired. Sign in again.", 401);
  }

  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) return errorResponse("OPENAI_API_KEY is not configured on the deployment.", 503);

  let body: Record<string, unknown>;
  try {
    body = await request.json() as Record<string, unknown>;
  } catch {
    return errorResponse("Request body must be valid JSON.", 400);
  }

  const operation = body.operation;
  const topic = typeof body.topic === "string" ? body.topic.trim() : "";
  const context = typeof body.context === "string" ? body.context.trim() : "";
  const language = typeof body.language === "string" ? body.language : "Hinglish (Roman script)";
  const format = typeof body.format === "string" ? body.format : "Long-form";
  const duration = typeof body.duration === "string" ? body.duration : "8–10 minutes";
  const userDirection = typeof body.direction === "string" ? body.direction.trim() : "";

  if (!OPERATIONS.includes(operation as Operation)) return errorResponse("Unknown production task.", 400);
  if (topic.length < 3 || topic.length > 12000) return errorResponse("Topic or brief must be between 3 and 12,000 characters.", 400);
  if (context.length > 16000 || userDirection.length > 4000) return errorResponse("Additional context is too long.", 400);

  const task = operation as Operation;
  const input = [
    "Production task: " + task,
    "Channel language: " + language + ". If Hinglish is selected, write in natural spoken Hindi using Roman script. Do not switch to Devanagari unless explicitly requested.",
    "Video format: " + format,
    "Target duration: " + duration,
    "Topic / brief:\n<topic>\n" + topic + "\n</topic>",
    context ? "Existing material / source notes:\n<context>\n" + context + "\n</context>" : "",
    userDirection ? "Additional direction:\n" + userDirection : "",
    "Maintain a serious, evidence-led documentary tone. Be precise, avoid fabricated facts, and clearly mark assumptions. Use headings and structured output that can be saved into a production project.",
  ].filter(Boolean).join("\n\n");

  try {
    const client = new OpenAI({ apiKey });
    const requiresSearch = task === "research";
    const response = await client.responses.create({
      model: process.env.OPENAI_MODEL || "gpt-6-astra",
      instructions: [
        "You are the editorial and production assistant for a serious Hindi explainer/documentary channel.",
        "Your work should be clear, rigorous, narratively engaging and production-ready.",
        "Never fabricate sources, quotes, datasets, dates, statistics or research findings.",
        "For web research, distinguish source-backed facts from interpretation and uncertainty. Provide direct URLs.",
        "For scripts, write narration that sounds natural when spoken aloud. Respect the selected language and script.",
        "For storyboards, use the hybrid visual approach: documentary storytelling plus code-generated motion graphics and explanatory diagrams.",
        "For generated visual code, do not assume access to the local machine. Return a self-contained and inspectable browser scene. Never include code that accesses the network, credentials, filesystem, shell, or operating system.",
        OPERATION_GUIDANCE[task],
      ].join("\n\n"),
      input,
      max_output_tokens: task === "research" || task === "script" ? 7000 : 5000,
      ...(requiresSearch ? {
        tools: [{ type: "web_search" as const }],
        tool_choice: "required" as const,
      } : {}),
    });

    const output = response.output_text?.trim();
    if (!output) return errorResponse("The model returned no text. Try again with a narrower brief.", 502);

    return NextResponse.json({
      ok: true,
      operation: task,
      model: response.model,
      text: output,
      responseId: response.id,
    }, { headers: { "Cache-Control": "no-store" } });
  } catch (error) {
    const status = typeof error === "object" && error !== null && "status" in error
      ? Number((error as { status?: unknown }).status)
      : 0;
    if (status === 429) return errorResponse("The OpenAI API rate limit or project quota was reached. Check API billing and limits.", 429);
    if (status === 401) return errorResponse("OpenAI rejected the API key. Check OPENAI_API_KEY in your deployment settings.", 502);
    return errorResponse("The OpenAI request failed. Check the deployment logs and model access, then try again.", 502);
  }
}
