import { NextRequest, NextResponse } from "next/server";
import { createSessionValue, sessionCookieName, sessionCookieOptions, verifyPassword } from "@/lib/auth";

export const runtime = "nodejs";

export async function POST(request: NextRequest) {
  const origin = request.headers.get("origin");
  if (origin && origin !== request.nextUrl.origin) {
    return NextResponse.json({ error: "Cross-origin request blocked." }, { status: 403 });
  }

  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid request." }, { status: 400 });
  }
  const password = typeof body === "object" && body !== null && "password" in body
    ? (body as { password?: unknown }).password
    : null;

  if (typeof password !== "string" || password.length < 1 || password.length > 256) {
    return NextResponse.json({ error: "Enter the studio password." }, { status: 400 });
  }

  try {
    if (!verifyPassword(password)) {
      return NextResponse.json({ error: "Incorrect password." }, { status: 401 });
    }
    const response = NextResponse.json({ ok: true });
    response.cookies.set(sessionCookieName, createSessionValue(), sessionCookieOptions());
    response.headers.set("Cache-Control", "no-store");
    return response;
  } catch (error) {
    const message = error instanceof Error ? error.message : "Authentication is not configured.";
    return NextResponse.json({ error: message }, { status: 503 });
  }
}
