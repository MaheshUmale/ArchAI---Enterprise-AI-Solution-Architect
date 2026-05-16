import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ArchAI - Enterprise AI Solution Architect",
  description: "AI-powered Solution Architect",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
