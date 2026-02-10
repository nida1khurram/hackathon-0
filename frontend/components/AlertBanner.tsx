interface AlertBannerProps {
  alerts: string[];
}

export function AlertBanner({ alerts }: AlertBannerProps) {
  const hasRealAlerts = alerts.some((a) => !a.includes("All clear"));

  if (!hasRealAlerts) {
    return (
      <div className="rounded-lg bg-green-50 border border-green-200 p-4 text-sm text-green-800">
        All clear - no alerts at this time.
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {alerts.map((alert, i) => (
        <div
          key={i}
          className="rounded-lg bg-amber-50 border border-amber-200 p-4 text-sm text-amber-800 flex items-start gap-2"
        >
          <svg className="w-5 h-5 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
          {alert}
        </div>
      ))}
    </div>
  );
}
