import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { StatusBadge } from "@/components/status-badge";

describe("StatusBadge", () => {
  it("renders 'passed' for true", () => {
    render(<StatusBadge value={true} />);
    expect(screen.getByText("passed")).toBeInTheDocument();
  });

  it("renders 'failed' for false", () => {
    render(<StatusBadge value={false} />);
    expect(screen.getByText("failed")).toBeInTheDocument();
  });

  it("renders raw string for arbitrary values", () => {
    render(<StatusBadge value="pending" />);
    expect(screen.getByText("pending")).toBeInTheDocument();
  });

  it("renders 'unknown' when value is missing", () => {
    render(<StatusBadge value={null} />);
    expect(screen.getByText("unknown")).toBeInTheDocument();
  });
});
