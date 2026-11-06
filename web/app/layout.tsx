import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Hindi Explainer Studio",
  description: "A private AI-assisted workspace for research, scripts and visual planning.",
  robots: { index: false, follow: false },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
