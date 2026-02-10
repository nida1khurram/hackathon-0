"use client";

import { useCallback, useState } from "react";
import { getVaultStatus, initVault } from "@/lib/api";
import { usePolling } from "@/hooks/usePolling";

export default function VaultPage() {
  const fetcher = useCallback(() => getVaultStatus(), []);
  const { data, loading, refresh } = usePolling(fetcher, 10000);
  const [initializing, setInitializing] = useState(false);
  const [owner, setOwner] = useState("AI Employee");
  const [business, setBusiness] = useState("My Business");

  async function handleInit() {
    setInitializing(true);
    try {
      await initVault(owner, business);
      refresh();
    } finally {
      setInitializing(false);
    }
  }

  if (loading && !data) {
    return <div className="flex items-center justify-center h-64 text-muted-foreground">Loading vault status...</div>;
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Vault Status</h1>
          <p className="text-sm text-muted-foreground">Obsidian vault folder structure and core files</p>
        </div>
        <span className={`px-3 py-1 rounded-full text-sm font-medium ${
          data?.initialized
            ? "bg-green-100 text-green-800"
            : "bg-red-100 text-red-800"
        }`}>
          {data?.initialized ? "Initialized" : "Not Initialized"}
        </span>
      </div>

      {!data?.initialized && (
        <div className="rounded-xl border border-border bg-card p-6">
          <h2 className="text-lg font-semibold mb-4">Initialize Vault</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium mb-1">Owner Name</label>
              <input
                value={owner}
                onChange={(e) => setOwner(e.target.value)}
                className="w-full border border-border rounded-lg px-3 py-2 text-sm bg-background"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Business Name</label>
              <input
                value={business}
                onChange={(e) => setBusiness(e.target.value)}
                className="w-full border border-border rounded-lg px-3 py-2 text-sm bg-background"
              />
            </div>
          </div>
          <button
            onClick={handleInit}
            disabled={initializing}
            className="px-6 py-2 text-sm rounded-lg bg-primary text-primary-foreground hover:opacity-90 disabled:opacity-50"
          >
            {initializing ? "Initializing..." : "Initialize Vault"}
          </button>
        </div>
      )}

      <div>
        <h2 className="text-lg font-semibold mb-3">Folders</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
          {data?.folders.map((folder) => (
            <div key={folder.name} className="rounded-xl border border-border bg-card p-4 text-center">
              <div className="text-2xl font-bold">{folder.count}</div>
              <div className="text-xs text-muted-foreground mt-1">{folder.name.replace(/_/g, " ")}</div>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h2 className="text-lg font-semibold mb-3">Core Files</h2>
        <div className="rounded-xl border border-border bg-card divide-y divide-border">
          {data?.core_files.map((file) => (
            <div key={file.name} className="flex items-center justify-between px-5 py-3">
              <span className="text-sm font-medium">{file.name}</span>
              <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                file.exists ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
              }`}>
                {file.exists ? "Exists" : "Missing"}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
