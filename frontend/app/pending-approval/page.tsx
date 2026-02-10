"use client";

import { useCallback, useState } from "react";
import { getApprovals, approveItem, rejectItem } from "@/lib/api";
import { usePolling } from "@/hooks/usePolling";
import type { Approval } from "@/lib/types";

const PRIORITY_COLORS: Record<string, string> = {
  high: "border-l-destructive",
  normal: "border-l-primary",
  medium: "border-l-warning",
  low: "border-l-muted-foreground",
};

export default function PendingApprovalPage() {
  const fetcher = useCallback(() => getApprovals(), []);
  const { data: approvals, loading, refresh } = usePolling(fetcher, 5000);
  const [acting, setActing] = useState<string | null>(null);

  async function handleApprove(approval: Approval) {
    setActing(approval.id);
    try {
      await approveItem(approval.id);
      refresh();
    } finally {
      setActing(null);
    }
  }

  async function handleReject(approval: Approval) {
    setActing(approval.id);
    try {
      await rejectItem(approval.id);
      refresh();
    } finally {
      setActing(null);
    }
  }

  if (loading && !approvals) {
    return <div className="flex items-center justify-center h-64 text-muted-foreground">Loading...</div>;
  }

  const list = approvals || [];

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Pending Approval</h1>
        <p className="text-sm text-muted-foreground">{list.length} item{list.length !== 1 ? "s" : ""} awaiting your review</p>
      </div>

      {list.length === 0 ? (
        <div className="rounded-xl border border-border p-12 bg-card text-center">
          <p className="text-muted-foreground">No items pending approval.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {list.map((approval) => (
            <div
              key={approval.id}
              className={`rounded-xl border border-border border-l-4 ${PRIORITY_COLORS[approval.priority] || PRIORITY_COLORS.normal} bg-card p-5`}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold truncate">{approval.subject}</h3>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    {approval.action} &middot; {approval.priority} priority
                  </p>
                </div>
                <span className={`shrink-0 ml-2 px-2 py-0.5 rounded-full text-xs font-medium ${
                  approval.priority === "high" ? "bg-red-100 text-red-800" : "bg-blue-100 text-blue-800"
                }`}>
                  {approval.priority}
                </span>
              </div>

              <div className="text-sm text-muted-foreground space-y-1 mb-4">
                <p><span className="font-medium text-foreground">Source:</span> {approval.source_file}</p>
                <p><span className="font-medium text-foreground">Reason:</span> {approval.reason}</p>
                <p><span className="font-medium text-foreground">Created:</span> {approval.created}</p>
                <p><span className="font-medium text-foreground">Expires:</span> {approval.expires}</p>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={() => handleApprove(approval)}
                  disabled={acting === approval.id}
                  className="flex-1 px-4 py-2 text-sm rounded-lg bg-success text-white hover:opacity-90 disabled:opacity-50 font-medium"
                >
                  {acting === approval.id ? "..." : "Approve"}
                </button>
                <button
                  onClick={() => handleReject(approval)}
                  disabled={acting === approval.id}
                  className="flex-1 px-4 py-2 text-sm rounded-lg bg-destructive text-white hover:opacity-90 disabled:opacity-50 font-medium"
                >
                  {acting === approval.id ? "..." : "Reject"}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
