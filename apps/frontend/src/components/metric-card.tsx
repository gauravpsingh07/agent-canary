import type { LucideIcon } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

const tones = {
  default: "bg-primary/10 text-primary",
  green: "bg-emerald-100 text-emerald-800",
  amber: "bg-amber-100 text-amber-900",
  red: "bg-red-100 text-red-800",
  blue: "bg-cyan-100 text-cyan-800"
};

export function MetricCard({
  label,
  value,
  helper,
  icon: Icon,
  tone = "default"
}: {
  label: string;
  value: string | number;
  helper?: string;
  icon: LucideIcon;
  tone?: keyof typeof tones;
}) {
  return (
    <Card>
      <CardContent className="flex min-h-28 items-start justify-between gap-4">
        <div className="min-w-0">
          <div className="text-sm font-medium text-muted-foreground">{label}</div>
          <div className="mt-2 text-2xl font-semibold">{value}</div>
          {helper ? <div className="mt-2 text-xs text-muted-foreground">{helper}</div> : null}
        </div>
        <div className={cn("rounded-md p-2", tones[tone])}>
          <Icon className="h-5 w-5" />
        </div>
      </CardContent>
    </Card>
  );
}
