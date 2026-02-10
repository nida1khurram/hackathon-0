"use client";

import { useState } from "react";
import { simulateEmail, simulateBatch } from "@/lib/api";

interface SimulateEmailDialogProps {
  open: boolean;
  onClose: () => void;
  onComplete: () => void;
}

export function SimulateEmailDialog({ open, onClose, onComplete }: SimulateEmailDialogProps) {
  const [mode, setMode] = useState<"single" | "batch">("batch");
  const [count, setCount] = useState(5);
  const [sender, setSender] = useState("");
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [loading, setLoading] = useState(false);

  if (!open) return null;

  async function handleSubmit() {
    setLoading(true);
    try {
      if (mode === "batch") {
        await simulateBatch(count);
      } else {
        await simulateEmail({
          sender: sender || "demo@example.com",
          subject: subject || "Test Email",
          body: body || "This is a test email for demonstration.",
        });
      }
      onComplete();
      onClose();
    } catch {
      alert("Failed to simulate emails");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="bg-card rounded-xl border border-border shadow-xl w-full max-w-md p-6">
        <h2 className="text-lg font-semibold mb-4">Simulate Incoming Email</h2>

        <div className="flex gap-2 mb-4">
          <button
            onClick={() => setMode("batch")}
            className={`px-3 py-1.5 text-sm rounded-lg ${mode === "batch" ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"}`}
          >
            Random Batch
          </button>
          <button
            onClick={() => setMode("single")}
            className={`px-3 py-1.5 text-sm rounded-lg ${mode === "single" ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"}`}
          >
            Custom Email
          </button>
        </div>

        {mode === "batch" ? (
          <div>
            <label className="block text-sm font-medium mb-1">Number of emails</label>
            <input
              type="number"
              min={1}
              max={20}
              value={count}
              onChange={(e) => setCount(Number(e.target.value))}
              className="w-full border border-border rounded-lg px-3 py-2 text-sm bg-background"
            />
            <p className="text-xs text-muted-foreground mt-1">
              Generates random realistic emails (invoices, complaints, inquiries, etc.)
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium mb-1">From</label>
              <input
                value={sender}
                onChange={(e) => setSender(e.target.value)}
                placeholder="sender@example.com"
                className="w-full border border-border rounded-lg px-3 py-2 text-sm bg-background"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Subject</label>
              <input
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                placeholder="Email subject"
                className="w-full border border-border rounded-lg px-3 py-2 text-sm bg-background"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Body</label>
              <textarea
                value={body}
                onChange={(e) => setBody(e.target.value)}
                placeholder="Email body content..."
                rows={3}
                className="w-full border border-border rounded-lg px-3 py-2 text-sm bg-background resize-none"
              />
            </div>
          </div>
        )}

        <div className="flex justify-end gap-2 mt-6">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm rounded-lg border border-border hover:bg-muted"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={loading}
            className="px-4 py-2 text-sm rounded-lg bg-primary text-primary-foreground hover:opacity-90 disabled:opacity-50"
          >
            {loading ? "Sending..." : mode === "batch" ? `Generate ${count} Emails` : "Send Email"}
          </button>
        </div>
      </div>
    </div>
  );
}
