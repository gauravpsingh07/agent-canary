export function PageHeader({
  title,
  eyebrow,
  action
}: {
  title: string;
  eyebrow?: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
      <div>
        {eyebrow ? <div className="mb-1 text-xs font-semibold uppercase text-primary">{eyebrow}</div> : null}
        <h1 className="text-2xl font-semibold tracking-normal">{title}</h1>
      </div>
      {action}
    </div>
  );
}
