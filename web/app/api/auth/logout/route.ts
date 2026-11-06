import { NextRequest, NextResponse } from "next/server";
import { sessionCookieName, sessionCookieOptions } from "@/lib/auth";

export async function POST(request: NextRequest) {
  const origin = request.headers.get("origin");
  if (origin && origin !== request.nextUrl.origin) {
    return NextResponse.json({ error: "Cross-origin request blocked." }, { status: 403 });
  }
  const response = NextResponse.json({ ok: true });
  response.cookies.set(sessionCookieName, "", { ...sessionCookieOptions(), maxAge: 0 });
  return response;
}
