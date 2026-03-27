"use client";

import { useEffect, useState } from "react";
import { listFiles, uploadFile, deleteFile, renameFile, getAuthStatus } from "@/lib/api";

type FileItem = {
  id: string;
  name: string;
  path?: string;
  size?: number | null;
  is_folder: boolean;
  modified?: string | null;
  mime_type?: string;
};

const PROVIDER_LABELS: Record<string, string> = {
  dropbox: "Dropbox",
  box: "Box",
  google: "Google Drive",
};

export default function FilesPage() {
  const [provider, setProvider] = useState("dropbox");
  const [files, setFiles] = useState<FileItem[]>([]);
  const [connected, setConnected] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [renaming, setRenaming] = useState<string | null>(null);
  const [newName, setNewName] = useState("");

  useEffect(() => {
    getAuthStatus().then((d) => setConnected(d.connected)).catch(() => {});
  }, []);

  const load = async () => {
    setLoading(true);
    setError("");
    try {
      const data = await listFiles(provider);
      setFiles(data);
    } catch (e: any) {
      setError(e.message);
      setFiles([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (connected.includes(provider)) load();
  }, [provider, connected]);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    try {
      await uploadFile(provider, formData);
      load();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleDelete = async (item: FileItem) => {
    if (!confirm(`Delete "${item.name}"?`)) return;
    try {
      const params =
        provider === "dropbox"
          ? `path=${encodeURIComponent(item.path || "")}`
          : `file_id=${encodeURIComponent(item.id)}&is_folder=${item.is_folder}`;
      await deleteFile(provider, params);
      load();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleRename = async (item: FileItem) => {
    if (!newName.trim()) return;
    try {
      let params: string;
      if (provider === "dropbox") {
        const dir = (item.path || "").split("/").slice(0, -1).join("/");
        params = `old_path=${encodeURIComponent(item.path || "")}&new_path=${encodeURIComponent(dir + "/" + newName)}`;
      } else {
        params = `file_id=${encodeURIComponent(item.id)}&new_name=${encodeURIComponent(newName)}&is_folder=${item.is_folder}`;
      }
      await renameFile(provider, params);
      setRenaming(null);
      setNewName("");
      load();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const isConnected = connected.includes(provider);

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4 flex-wrap">
        <h1 className="text-2xl font-bold">Files</h1>
        <div className="flex gap-2">
          {Object.keys(PROVIDER_LABELS).map((p) => (
            <button
              key={p}
              onClick={() => setProvider(p)}
              className={`px-3 py-1 rounded-lg text-sm font-medium ${
                provider === p
                  ? "bg-gray-900 text-white"
                  : "bg-gray-200 text-gray-700 hover:bg-gray-300"
              }`}
            >
              {PROVIDER_LABELS[p]}
            </button>
          ))}
        </div>
      </div>

      {!isConnected ? (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-sm">
          Not connected to {PROVIDER_LABELS[provider]}.{" "}
          <a href="/connections" className="text-blue-600 underline">
            Connect now
          </a>
        </div>
      ) : (
        <>
          <div className="flex items-center gap-3">
            <label className="bg-blue-600 text-white px-4 py-1.5 rounded-lg text-sm cursor-pointer hover:bg-blue-700">
              Upload File
              <input type="file" className="hidden" onChange={handleUpload} />
            </label>
            <button onClick={load} className="text-sm text-gray-500 hover:text-gray-700">
              Refresh
            </button>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-700">
              {error}
            </div>
          )}

          {loading ? (
            <p className="text-gray-500">Loading files...</p>
          ) : files.length === 0 ? (
            <p className="text-gray-500">No files found.</p>
          ) : (
            <div className="bg-white rounded-xl border divide-y">
              {files.map((item) => (
                <div key={item.id} className="flex items-center px-4 py-3 gap-3">
                  <span className="text-lg">{item.is_folder ? "\uD83D\uDCC1" : "\uD83D\uDCC4"}</span>
                  <div className="flex-1 min-w-0">
                    {renaming === item.id ? (
                      <div className="flex gap-2 items-center">
                        <input
                          value={newName}
                          onChange={(e) => setNewName(e.target.value)}
                          className="border rounded px-2 py-1 text-sm flex-1"
                          autoFocus
                          onKeyDown={(e) => e.key === "Enter" && handleRename(item)}
                        />
                        <button
                          onClick={() => handleRename(item)}
                          className="text-sm text-blue-600 hover:underline"
                        >
                          Save
                        </button>
                        <button
                          onClick={() => setRenaming(null)}
                          className="text-sm text-gray-400 hover:underline"
                        >
                          Cancel
                        </button>
                      </div>
                    ) : (
                      <p className="font-medium truncate">{item.name}</p>
                    )}
                    <p className="text-xs text-gray-400">
                      {item.path || item.id}
                      {item.size != null && ` \u00b7 ${(item.size / 1024).toFixed(1)} KB`}
                    </p>
                  </div>
                  <button
                    onClick={() => {
                      setRenaming(item.id);
                      setNewName(item.name);
                    }}
                    className="text-xs text-gray-500 hover:text-blue-600"
                  >
                    Rename
                  </button>
                  <button
                    onClick={() => handleDelete(item)}
                    className="text-xs text-gray-500 hover:text-red-600"
                  >
                    Delete
                  </button>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
