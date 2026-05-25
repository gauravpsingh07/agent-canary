import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { Gauge } from "lucide-react";
import { MetricCard } from "@/components/metric-card";

describe("MetricCard", () => {
  it("renders label, value, and optional helper", () => {
    render(<MetricCard label="Pass Rate" value="42.0%" helper="of total runs" icon={Gauge} />);
    expect(screen.getByText("Pass Rate")).toBeInTheDocument();
    expect(screen.getByText("42.0%")).toBeInTheDocument();
    expect(screen.getByText("of total runs")).toBeInTheDocument();
  });

  it("accepts numeric values", () => {
    render(<MetricCard label="Runs" value={7} icon={Gauge} />);
    expect(screen.getByText("7")).toBeInTheDocument();
  });
});
