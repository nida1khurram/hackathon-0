interface ActivityFeedProps {
  items: string[];
}

export function ActivityFeed({ items }: ActivityFeedProps) {
  if (!items.length || (items.length === 1 && items[0].includes("No activity"))) {
    return <p className="text-sm text-muted-foreground">No recent activity.</p>;
  }

  return (
    <ul className="space-y-2">
      {items.map((item, i) => (
        <li key={i} className="flex items-start gap-2 text-sm">
          <span className="w-1.5 h-1.5 rounded-full bg-primary mt-2 shrink-0" />
          <span className="text-muted-foreground">{item}</span>
        </li>
      ))}
    </ul>
  );
}
