"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  AlertTriangle,
  Bot,
  CheckSquare,
  Database,
  FileSearch,
  Flame,
  Gauge,
  Hammer,
  Home,
  LayoutDashboard,
  ListChecks,
  ScrollText,
  ShieldCheck,
  Siren,
  Wrench
} from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/", label: "Home", icon: Home, exact: true },
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/projects", label: "Projects", icon: Bot },
  { href: "/test-suites", label: "Test Suites", icon: ListChecks },
  { href: "/test-runs", label: "Test Runs", icon: Activity },
  { href: "/failure-reports", label: "Failure Reports", icon: AlertTriangle },
  { href: "/policy-rules", label: "Policy Rules", icon: ShieldCheck },
  { href: "/tools", label: "Tool Registry", icon: Wrench },
  { href: "/approvals", label: "Approvals", icon: CheckSquare },
  { href: "/audit-logs", label: "Audit Logs", icon: ScrollText },
  { href: "/rag-documents", label: "RAG Documents", icon: Database },
  { href: "/rag-documents/ingestion-jobs", label: "Ingestion Jobs", icon: Flame },
  { href: "/retrieval-results", label: "Retrieval", icon: FileSearch },
  { href: "/metrics", label: "Metrics", icon: Gauge }
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen">
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-border bg-card lg:block">
        <div className="flex h-16 items-center gap-2 border-b border-border px-5">
          <Siren className="h-6 w-6 text-primary" />
          <div>
            <div className="text-sm font-semibold">Agent Canary</div>
            <div className="text-xs text-muted-foreground">Evaluation Control</div>
          </div>
        </div>
        <nav className="space-y-1 p-3">
          {navItems.map((item) => {
            const active = item.exact ? pathname === item.href : pathname.startsWith(item.href);
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex h-10 items-center gap-3 rounded-md px-3 text-sm font-medium",
                  active ? "bg-muted text-primary" : "text-muted-foreground hover:bg-muted"
                )}
              >
                <Icon className="h-4 w-4" />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </aside>
      <div className="lg:pl-64">
        <header className="sticky top-0 z-10 flex h-16 items-center border-b border-border bg-background/95 px-4 lg:px-8">
          <div className="flex items-center gap-2 lg:hidden">
            <Siren className="h-5 w-5 text-primary" />
            <span className="font-semibold">Agent Canary</span>
          </div>
          <div className="ml-auto flex items-center gap-2 text-xs text-muted-foreground">
            <Hammer className="h-4 w-4" />
            API: localhost:8000
          </div>
        </header>
        <main className="p-4 lg:p-8">{children}</main>
      </div>
    </div>
  );
}
