import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Test App — Unified File Manager",
  description:
    "Manage files across Dropbox, Box, and Google Drive. Parse documents. Manage calendar events.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gray-50 text-gray-900 min-h-screen">
        <nav className="bg-white border-b border-gray-200 px-6 py-3 flex items-center gap-6">
          <a href="/" className="font-bold text-lg">
            Test App
          </a>
          <a href="/files" className="hover:text-blue-600">
            Files
          </a>
          <a href="/documents" className="hover:text-blue-600">
            Documents
          </a>
          <a href="/calendar" className="hover:text-blue-600">
            Calendar
          </a>
          <a href="/connections" className="hover:text-blue-600">
            Connections
          </a>
        </nav>
        <main className="max-w-6xl mx-auto p-6">{children}</main>
      </body>
    </html>
  );
}
