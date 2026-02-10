"use client";

import { useCallback, useState, useEffect } from "react";
import { getHandbook, updateHandbook, validateHandbook } from "@/lib/api";
import type { HandbookData } from "@/lib/types";

export default function HandbookPage() {
  const [data, setData] = useState<HandbookData | null>(null);
  const [content, setContent] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [validating, setValidating] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [dirty, setDirty] = useState(false);

  const load = useCallback(async () => {
    try {
      const result = await getHandbook();
      setData(result);
      setContent(result.content);
      setDirty(false);
    } catch {
      // Backend may not have handbook yet
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function handleSave() {
    setSaving(true);
    try {
      await updateHandbook(content);
      await load();
    } finally {
      setSaving(false);
    }
  }

  async function handleValidate() {
    setValidating(true);
    try {
      const result = await validateHandbook();
      setData(result);
    } finally {
      setValidating(false);
    }
  }

  if (loading) {
    return <div className="flex items-center justify-center h-64 text-muted-foreground">Loading handbook...</div>;
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Company Handbook</h1>
          <p className="text-sm text-muted-foreground">Rules of engagement for the AI Employee</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setShowPreview(!showPreview)}
            className="px-4 py-2 text-sm rounded-lg border border-border hover:bg-muted"
          >
            {showPreview ? "Editor" : "Preview"}
          </button>
          <button
            onClick={handleValidate}
            disabled={validating}
            className="px-4 py-2 text-sm rounded-lg border border-border hover:bg-muted disabled:opacity-50"
          >
            {validating ? "Validating..." : "Validate"}
          </button>
          <button
            onClick={handleSave}
            disabled={saving || !dirty}
            className="px-4 py-2 text-sm rounded-lg bg-primary text-primary-foreground hover:opacity-90 disabled:opacity-50"
          >
            {saving ? "Saving..." : "Save"}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Editor / Preview */}
        <div className="lg:col-span-2 rounded-xl border border-border bg-card overflow-hidden">
          {showPreview ? (
            <div className="p-6 prose prose-sm max-w-none">
              <pre className="whitespace-pre-wrap text-sm font-sans">{content}</pre>
            </div>
          ) : (
            <textarea
              value={content}
              onChange={(e) => {
                setContent(e.target.value);
                setDirty(true);
              }}
              className="w-full h-[600px] p-4 text-sm font-mono bg-background resize-none focus:outline-none"
              spellCheck={false}
            />
          )}
        </div>

        {/* Validation Panel */}
        <div className="rounded-xl border border-border bg-card p-5">
          <h2 className="text-lg font-semibold mb-4">Validation Checklist</h2>
          {data?.validation ? (
            <div className="space-y-3">
              {data.validation.map((v, i) => (
                <div key={i} className="flex items-start gap-2">
                  <span className={`mt-0.5 shrink-0 ${v.present ? "text-success" : "text-destructive"}`}>
                    {v.present ? (
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    ) : (
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    )}
                  </span>
                  <div>
                    <p className="text-sm font-medium">{v.section}</p>
                    <p className="text-xs text-muted-foreground">{v.description}</p>
                  </div>
                </div>
              ))}

              <div className={`mt-4 p-3 rounded-lg text-sm font-medium ${
                data.is_complete
                  ? "bg-green-50 text-green-800 border border-green-200"
                  : "bg-amber-50 text-amber-800 border border-amber-200"
              }`}>
                {data.is_complete ? "All 8 sections present" : "Some sections are missing"}
              </div>
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">Click &quot;Validate&quot; to check handbook completeness.</p>
          )}
        </div>
      </div>
    </div>
  );
}
