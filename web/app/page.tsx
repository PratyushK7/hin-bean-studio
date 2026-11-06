import { hasValidSession } from "@/lib/auth";
import StudioShell from "./studio-shell";
import LoginForm from "./login-form";

export const dynamic = "force-dynamic";

export default async function HomePage() {
  const authenticated = await hasValidSession();
  return authenticated ? <StudioShell /> : <LoginForm />;
}
