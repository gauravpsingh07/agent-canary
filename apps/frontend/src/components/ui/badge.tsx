import { cn } from "@/lib/utils";

const variants = {
  default: "border-border bg-muted text-foreground",
  pass: "border-emerald-200 bg-emerald-50 text-emerald-800",
  fail: "border-red-200 bg-red-50 text-red-800",
  warn: "border-amber-200 bg-amber-50 text-amber-900"
};

export function Badge({
  children,
  variant = "default"
}: {
  children: React.ReactNode;
  variant?: keyof typeof variants;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-md border px-2 py-0.5 text-xs font-medium",
        variants[variant]
      )}
    >
      {children}
    </span>
  );
}
