import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "NyayBot — Legal Docs in Your Language",
  description: "Understand any legal document in your language in 60 seconds.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen" style={{ background: "#0A0F1E" }}>
        {children}
      </body>
    </html>
  );
}
