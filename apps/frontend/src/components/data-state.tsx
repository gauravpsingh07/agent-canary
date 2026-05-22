import { AlertTriangle, Loader2 } from "lucide-react";

export function LoadingState() {
  return (
    <div className="flex h-28 items-center justify-center text-sm text-muted-foreground">
      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
      Loading
    </div>
  );
}

export function ErrorState({ message }: { message: string }) {
  return (
    <div className="flex min-h-24 items-center gap-2 rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-800">
      <AlertTriangle className="h-4 w-4" />
      {message}
    </div>
  );
}
