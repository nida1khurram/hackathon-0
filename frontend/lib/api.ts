import type {
  VaultStatus,
  ActionItem,
  ProcessResult,
  Approval,
  DashboardMetrics,
  HandbookData,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchAPI<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const error = await res.text();
    throw new Error(error || res.statusText);
  }
  return res.json();
}

// Health
export const checkHealth = () => fetchAPI<{ status: string }>("/api/health");

// Vault
export const getVaultStatus = () => fetchAPI<VaultStatus>("/api/vault/status");
export const initVault = (owner: string, business: string) =>
  fetchAPI<{ message: string }>("/api/vault/init", {
    method: "POST",
    body: JSON.stringify({ owner, business }),
  });

// Needs Action
export const getNeedsAction = () =>
  fetchAPI<ActionItem[]>("/api/needs-action");
export const processItem = (filename: string) =>
  fetchAPI<{ action: string }>("/api/needs-action/process", {
    method: "POST",
    body: JSON.stringify({ filename }),
  });
export const processAll = () =>
  fetchAPI<ProcessResult>("/api/needs-action/process-all", {
    method: "POST",
  });

// Approvals
export const getApprovals = () => fetchAPI<Approval[]>("/api/approvals");
export const approveItem = (id: string) =>
  fetchAPI<{ message: string }>(`/api/approvals/${id}/approve`, {
    method: "POST",
  });
export const rejectItem = (id: string) =>
  fetchAPI<{ message: string }>(`/api/approvals/${id}/reject`, {
    method: "POST",
  });

// Dashboard
export const getDashboard = () =>
  fetchAPI<DashboardMetrics>("/api/dashboard");
export const refreshDashboard = () =>
  fetchAPI<{ message: string }>("/api/dashboard/refresh", { method: "POST" });

// Handbook
export const getHandbook = () => fetchAPI<HandbookData>("/api/handbook");
export const updateHandbook = (content: string) =>
  fetchAPI<{ message: string }>("/api/handbook", {
    method: "PUT",
    body: JSON.stringify({ content }),
  });
export const validateHandbook = () =>
  fetchAPI<HandbookData>("/api/handbook/validate", { method: "POST" });

// Simulate
export const simulateEmail = (data: {
  sender: string;
  subject: string;
  body: string;
  type?: string;
  priority?: string;
}) =>
  fetchAPI<{ message: string; filename: string }>("/api/simulate/email", {
    method: "POST",
    body: JSON.stringify(data),
  });
export const simulateBatch = (count = 5) =>
  fetchAPI<{ message: string; count: number; files: string[] }>(
    "/api/simulate/batch",
    { method: "POST", body: JSON.stringify({ count }) }
  );
