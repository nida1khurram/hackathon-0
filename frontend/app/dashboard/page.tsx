"use client";

import { useCallback, useState } from "react";
import { getDashboard, refreshDashboard } from "@/lib/api";
import { usePolling } from "@/hooks/usePolling";
import { StatusCard } from "@/components/StatusCard";
import { AlertBanner } from "@/components/AlertBanner";
import { ActivityFeed } from "@/components/ActivityFeed";
import { SimulateEmailDialog } from "@/components/SimulateEmailDialog";

export default function DashboardPage() {
  const fetcher = useCallback(() => getDashboard(), []);
  const { data, loading, refresh } = usePolling(fetcher, 5000);
  const [showSimulate, setShowSimulate] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  async function handleRefresh() {
    setRefreshing(true);
    try {
      await refreshDashboard();
      refresh();
    } finally {
      setRefreshing(false);
    }
  }

  if (loading && !data) {
    return <div className="flex items-center justify-center h-64 text-muted-foreground">Loading dashboard...</div>;
  }

  if (!data) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-4">
        <p className="text-muted-foreground">Unable to load dashboard. Is the backend running?</p>
        <button onClick={refresh} className="px-4 py-2 text-sm bg-primary text-primary-foreground rounded-lg">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-sm text-muted-foreground">Real-time AI Employee activity overview</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setShowSimulate(true)}
            className="px-4 py-2 text-sm rounded-lg border border-border hover:bg-muted"
          >
            Simulate Email
          </button>
          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="px-4 py-2 text-sm rounded-lg bg-primary text-primary-foreground hover:opacity-90 disabled:opacity-50"
          >
            {refreshing ? "Refreshing..." : "Refresh"}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatusCard title="Needs Action" value={data.needs_action} color="amber" subtitle="Items awaiting processing" />
        <StatusCard title="Awaiting Approval" value={data.pending_approval} color="blue" subtitle="Pending your review" />
        <StatusCard title="Done Today" value={data.done_today} color="green" subtitle="Completed items" />
        <StatusCard title="Active Plans" value={data.active_plans} color="purple" subtitle="Plans in progress" />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="rounded-xl border border-border p-5 bg-card">
          <p className="text-sm text-muted-foreground font-medium">MTD Revenue</p>
          <p className="text-2xl font-bold mt-1">{data.mtd_revenue}</p>
        </div>
        <div className="rounded-xl border border-border p-5 bg-card">
          <p className="text-sm text-muted-foreground font-medium">Monthly Target</p>
          <p className="text-2xl font-bold mt-1">{data.monthly_target}</p>
        </div>
      </div>

      <div className="rounded-xl border border-border p-5 bg-card">
        <h2 className="text-lg font-semibold mb-3">Alerts</h2>
        <AlertBanner alerts={data.alerts} />
      </div>

      <div className="rounded-xl border border-border p-5 bg-card">
        <h2 className="text-lg font-semibold mb-3">Recent Activity</h2>
        <ActivityFeed items={data.recent_activity} />
      </div>

      <div className="rounded-xl border border-border p-5 bg-card flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">Agent Health</h2>
          <p className="text-sm text-muted-foreground">System status</p>
        </div>
        <span className="flex items-center gap-2 text-sm font-medium text-success">
          <span className="w-3 h-3 rounded-full bg-success animate-pulse" />
          {data.agent_health}
        </span>
      </div>

      <SimulateEmailDialog
        open={showSimulate}
        onClose={() => setShowSimulate(false)}
        onComplete={refresh}
      />
    </div>
  );
}
