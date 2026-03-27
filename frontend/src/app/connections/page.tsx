"use client";

import { useEffect, useState } from "react";
import { getAuthStatus } from "@/lib/api";

const PROVIDERS = [
  {
    id: "dropbox",
    name: "Dropbox",
    color: "bg-blue-500",
    authUrl: "/api/auth/dropbox",
  },
  {
    id: "box",
    name: "Box",
    color: "bg-blue-700",
    authUrl: "/api/auth/box",
  },
  {
    id: "google",
    name: "Google (Drive + Calendar)",
    color: "bg-red-500",
    authUrl: "/api/auth/google",
  },
];

export default function ConnectionsPage() {
  const [connected, setConnected] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAuthStatus()
      .then((data) => setConnected(data.connected))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const disconnect = async (provider: string) => {
    await fetch(`/api/auth/disconnect/${provider}`, {
      method: "POST",
      credentials: "include",
    });
    setConnected((prev) => prev.filter((p) => p !== provider));
  };

  if (loading) return <p className="py-10 text-center text-gray-500">Loading...</p>;

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Connections</h1>
      <div className="grid gap-4 sm:grid-cols-3">
        {PROVIDERS.map((p) => {
          const isConnected = connected.includes(p.id);
          return (
            <div key={p.id} className="bg-white rounded-xl border p-5 space-y-3">
              <div className="flex items-center gap-2">
                <span className={`w-3 h-3 rounded-full ${p.color}`} />
                <h2 className="font-semibold">{p.name}</h2>
              </div>
              {isConnected ? (
                <div className="flex items-center gap-2">
                  <span className="text-green-600 text-sm font-medium">Connected</span>
                  <button
                    onClick={() => disconnect(p.id)}
                    className="ml-auto text-sm text-red-500 hover:underline"
                  >
                    Disconnect
                  </button>
                </div>
              ) : (
                <a
                  href={p.authUrl}
                  className="inline-block text-sm bg-gray-900 text-white px-4 py-1.5 rounded-lg hover:bg-gray-800"
                >
                  Connect
                </a>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
