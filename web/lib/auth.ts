import { createHmac, randomBytes, timingSafeEqual } from "node:crypto";
import { cookies } from "next/headers";

const COOKIE_NAME = "hindi_studio_session";
const SESSION_SECONDS = 60 * 60 * 24 * 7;

function secret(): string {
  const value = process.env.SESSION_SECRET;
  if (!value || value.length < 32) {
    throw new Error("SESSION_SECRET must contain at least 32 characters.");
  }
  return value;
}

function sign(value: string): string {
  return createHmac("sha256", secret()).update(value).digest("hex");
}

export function verifyPassword(candidate: string): boolean {
  const expected = process.env.STUDIO_ACCESS_PASSWORD;
  if (!expected) throw new Error("STUDIO_ACCESS_PASSWORD is not configured.");
  const a = Buffer.from(candidate, "utf8");
  const b = Buffer.from(expected, "utf8");
  return a.length === b.length && timingSafeEqual(a, b);
}

export function createSessionValue(): string {
  const expires = String(Date.now() + SESSION_SECONDS * 1000);
  const nonce = randomBytes(16).toString("hex");
  const payload = expires + "." + nonce;
  return payload + "." + sign(payload);
}

export function sessionCookieOptions() {
  return {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax" as const,
    path: "/",
    maxAge: SESSION_SECONDS,
  };
}

export async function hasValidSession(): Promise<boolean> {
  try {
    const jar = await cookies();
    const value = jar.get(COOKIE_NAME)?.value;
    if (!value) return false;
    const parts = value.split(".");
    if (parts.length !== 3) return false;
    const expires = parts[0];
    const nonce = parts[1];
    const signature = parts[2];
    const payload = expires + "." + nonce;
    if (!/^[0-9]+$/.test(expires) || Number(expires) <= Date.now()) return false;
    const expected = sign(payload);
    const a = Buffer.from(signature, "hex");
    const b = Buffer.from(expected, "hex");
    return a.length === b.length && timingSafeEqual(a, b);
  } catch {
    return false;
  }
}

export const sessionCookieName = COOKIE_NAME;
