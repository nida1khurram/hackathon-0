interface StatusCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  color?: "blue" | "amber" | "green" | "purple" | "red";
}

const COLOR_MAP = {
  blue: "border-l-primary bg-blue-50/50",
  amber: "border-l-warning bg-amber-50/50",
  green: "border-l-success bg-green-50/50",
  purple: "border-l-accent bg-purple-50/50",
  red: "border-l-destructive bg-red-50/50",
};

export function StatusCard({ title, value, subtitle, color = "blue" }: StatusCardProps) {
  return (
    <div className={`rounded-xl border border-border border-l-4 ${COLOR_MAP[color]} p-5`}>
      <p className="text-sm text-muted-foreground font-medium">{title}</p>
      <p className="text-3xl font-bold mt-1">{value}</p>
      {subtitle && <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>}
    </div>
  );
}
