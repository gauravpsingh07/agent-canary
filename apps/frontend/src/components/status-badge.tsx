import { Badge } from "@/components/ui/badge";

export function StatusBadge({ value }: { value?: string | boolean | null }) {
  const text = value === true ? "passed" : value === false ? "failed" : String(value ?? "unknown");
  const normalized = text.toLowerCase();
  const variant =
    normalized.includes("pass") || normalized.includes("complete") || normalized.includes("approved")
      ? "pass"
      : normalized.includes("fail") ||
          normalized.includes("blocked") ||
          normalized.includes("rejected") ||
          normalized.includes("critical")
        ? "fail"
        : normalized.includes("pending") || normalized.includes("medium") || normalized.includes("high")
          ? "warn"
          : "default";

  return <Badge variant={variant}>{text}</Badge>;
}
