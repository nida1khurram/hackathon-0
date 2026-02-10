"use client";

import { useCallback, useState } from "react";
import { getNeedsAction, processItem, processAll } from "@/lib/api";
import { usePolling } from "@/hooks/usePolling";
import { SimulateEmailDialog } from "@/components/SimulateEmailDialog";
import type { ActionItem } from "@/lib/types";

const PRIORITY_COLORS: Record<string, string> = {
  high: "bg-red-100 text-red-800",
  normal: "bg-blue-100 text-blue-800",
  medium: "bg-yellow-100 text-yellow-800",
  low: "bg-gray-100 text-gray-800",
};

export default function NeedsActionPage() {
  const fetcher = useCallback(() => getNeedsAction(), []);
  const { data: items, loading, refresh } = usePolling(fetcher, 5000);
  const [processing, setProcessing] = useState<string | null>(null);
  const [processingAll, setProcessingAll] = useState(false);
  const [showSimulate, setShowSimulate] = useState(false);

  async function handleProcess(item: ActionItem) {
    setProcessing(item.filename);
    try {
      await processItem(item.filename);
      refresh();
    } finally {
      setProcessing(null);
    }
  }

  async function handleProcessAll() {
    setProcessingAll(true);
    try {
      await processAll();
      refresh();
    } finally {
      setProcessingAll(false);
    }
  }

  if (loading && !items) {
    return <div className="flex items-center justify-center h-64 text-muted-foreground">Loading...</div>;
  }

  const list = items || [];

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Needs Action</h1>
          <p className="text-sm text-muted-foreground">{list.length} item{list.length !== 1 ? "s" : ""} awaiting processing</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setShowSimulate(true)}
            className="px-4 py-2 text-sm rounded-lg border border-border hover:bg-muted"
          >
            Simulate Email
          </button>
          {list.length > 0 && (
            <button
              onClick={handleProcessAll}
              disabled={processingAll}
              className="px-4 py-2 text-sm rounded-lg bg-primary text-primary-foreground hover:opacity-90 disabled:opacity-50"
            >
              {processingAll ? "Processing..." : `Process All (${list.length})`}
            </button>
          )}
        </div>
      </div>

      {list.length === 0 ? (
        <div className="rounded-xl border border-border p-12 bg-card text-center">
          <p className="text-muted-foreground">No items need action.</p>
          <button
            onClick={() => setShowSimulate(true)}
            className="mt-4 px-4 py-2 text-sm rounded-lg bg-primary text-primary-foreground"
          >
            Simulate Emails to Get Started
          </button>
        </div>
      ) : (
        <div className="rounded-xl border border-border bg-card overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-muted/50">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-muted-foreground">Priority</th>
                <th className="text-left px-4 py-3 font-medium text-muted-foreground">Subject</th>
                <th className="text-left px-4 py-3 font-medium text-muted-foreground">From</th>
                <th className="text-left px-4 py-3 font-medium text-muted-foreground">Type</th>
                <th className="text-left px-4 py-3 font-medium text-muted-foreground">Received</th>
                <th className="text-right px-4 py-3 font-medium text-muted-foreground">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {list.map((item) => (
                <tr key={item.id} className="hover:bg-muted/30">
                  <td className="px-4 py-3">
                    <span className={`inline-block px-2 py-0.5 rounded-full text-xs font-medium ${PRIORITY_COLORS[item.priority] || PRIORITY_COLORS.normal}`}>
                      {item.priority}
                    </span>
                  </td>
                  <td className="px-4 py-3 font-medium max-w-xs truncate">{item.subject}</td>
                  <td className="px-4 py-3 text-muted-foreground max-w-[200px] truncate">{item.sender}</td>
                  <td className="px-4 py-3 text-muted-foreground">{item.type}</td>
                  <td className="px-4 py-3 text-muted-foreground text-xs">{item.received}</td>
                  <td className="px-4 py-3 text-right">
                    <button
                      onClick={() => handleProcess(item)}
                      disabled={processing === item.filename}
                      className="px-3 py-1.5 text-xs rounded-lg bg-primary text-primary-foreground hover:opacity-90 disabled:opacity-50"
                    >
                      {processing === item.filename ? "..." : "Process"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <SimulateEmailDialog
        open={showSimulate}
        onClose={() => setShowSimulate(false)}
        onComplete={refresh}
      />
    </div>
  );
}
