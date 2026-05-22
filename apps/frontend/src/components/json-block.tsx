export function JsonBlock({ value }: { value: unknown }) {
  return (
    <pre className="max-h-72 overflow-auto rounded-md border border-border bg-muted p-3 font-mono text-xs leading-relaxed">
      {JSON.stringify(value ?? {}, null, 2)}
    </pre>
  );
}
