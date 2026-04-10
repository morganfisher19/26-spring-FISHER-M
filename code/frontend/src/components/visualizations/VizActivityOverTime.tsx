import { useEffect, useRef, useState } from "react";
import * as d3 from "d3";

const API_BASE = "http://localhost:5000";

interface DataPoint {
  period: string;
  vote_count: number;
}

type Chamber = "" | "H" | "S";
type Granularity = "day" | "week" | "month";

export default function VizActivityOverTime() {
  const svgRef = useRef<SVGSVGElement>(null);
  const [data, setData] = useState<DataPoint[]>([]);
  const [policyAreas, setPolicyAreas] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [chamber, setChamber] = useState<Chamber>("");
  const [granularity, setGranularity] = useState<Granularity>("week");
  const [policyArea, setPolicyArea] = useState("");

  // Load policy areas once
  useEffect(() => {
    fetch(`${API_BASE}/api/policy_areas`)
      .then((r) => r.json())
      .then(setPolicyAreas)
      .catch(() => {});
  }, []);

  // Reload chart data when filters change
  useEffect(() => {
    setLoading(true);
    const params = new URLSearchParams({ granularity });
    if (chamber) params.set("chamber", chamber);
    if (policyArea) params.set("policy_area", policyArea);

    fetch(`${API_BASE}/api/visualizations/activity_over_time?${params}`)
      .then((r) => r.json())
      .then((json) => {
        setData(json.data);
        setLoading(false);
      })
      .catch(() => {
        setError("Failed to load data.");
        setLoading(false);
      });
  }, [chamber, granularity, policyArea]);

  // Draw / redraw chart
  useEffect(() => {
    if (!data.length || !svgRef.current) return;

    const margin = { top: 20, right: 20, bottom: 50, left: 60 };
    const width = 700 - margin.left - margin.right;
    const height = 380 - margin.top - margin.bottom;

    d3.select(svgRef.current).selectAll("*").remove();

    const svg = d3
      .select(svgRef.current)
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    const parsed = data.map((d) => ({
      period: new Date(d.period),
      vote_count: d.vote_count,
    }));

    const x = d3
      .scaleTime()
      .domain(d3.extent(parsed, (d) => d.period) as [Date, Date])
      .range([0, width]);

    const y = d3
      .scaleLinear()
      .domain([0, d3.max(parsed, (d) => d.vote_count) ?? 0])
      .nice()
      .range([height, 0]);

    // Line
    const line = d3
      .line<{ period: Date; vote_count: number }>()
      .x((d) => x(d.period))
      .y((d) => y(d.vote_count))
      .curve(d3.curveMonotoneX);

    // Area fill
    const area = d3
      .area<{ period: Date; vote_count: number }>()
      .x((d) => x(d.period))
      .y0(height)
      .y1((d) => y(d.vote_count))
      .curve(d3.curveMonotoneX);

    svg
      .append("path")
      .datum(parsed)
      .attr("fill", "#dbeafe")
      .attr("d", area);

    svg
      .append("path")
      .datum(parsed)
      .attr("fill", "none")
      .attr("stroke", "#2563eb")
      .attr("stroke-width", 2)
      .attr("d", line);

    // X axis
    const tickCount = granularity === "day" ? 8 : granularity === "week" ? 10 : 12;
    svg
      .append("g")
      .attr("transform", `translate(0,${height})`)
      .call(
        d3
          .axisBottom(x)
          .ticks(tickCount)
          .tickFormat((d) => {
            const date = d as Date;
            return granularity === "month"
              ? d3.timeFormat("%b %Y")(date)
              : d3.timeFormat("%b %d")(date);
          })
      )
      .selectAll("text")
      .attr("transform", "rotate(-35)")
      .style("text-anchor", "end")
      .style("font-size", "11px");

    // Y axis
    svg.append("g").call(d3.axisLeft(y).ticks(6).tickFormat(d3.format(",d")));

    // Y label
    svg
      .append("text")
      .attr("transform", "rotate(-90)")
      .attr("x", -height / 2)
      .attr("y", -48)
      .attr("text-anchor", "middle")
      .attr("font-size", "12px")
      .attr("fill", "#555")
      .text("Number of Votes");
  }, [data, granularity]);

  return (
    <div>
      {/* Filters */}
      <div style={{ display: "flex", gap: "1.5rem", marginBottom: "1.25rem", flexWrap: "wrap" }}>
        <div>
          <label style={labelStyle}>Chamber</label>
          <select value={chamber} onChange={(e) => setChamber(e.target.value as Chamber)} style={selectStyle}>
            <option value="">All</option>
            <option value="H">House</option>
            <option value="S">Senate</option>
          </select>
        </div>
        <div>
          <label style={labelStyle}>Granularity</label>
          <select value={granularity} onChange={(e) => setGranularity(e.target.value as Granularity)} style={selectStyle}>
            <option value="day">Day</option>
            <option value="week">Week</option>
            <option value="month">Month</option>
          </select>
        </div>
        <div>
          <label style={labelStyle}>Policy Area</label>
          <select value={policyArea} onChange={(e) => setPolicyArea(e.target.value)} style={selectStyle}>
            <option value="">All</option>
            {policyAreas.map((pa) => (
              <option key={pa} value={pa}>{pa}</option>
            ))}
          </select>
        </div>
      </div>

      {loading && <p>Loading...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      {!loading && !error && <svg ref={svgRef} />}
    </div>
  );
}

const labelStyle: React.CSSProperties = {
  display: "block",
  fontSize: "12px",
  color: "#555",
  marginBottom: "4px",
};

const selectStyle: React.CSSProperties = {
  fontSize: "13px",
  padding: "4px 8px",
  borderRadius: "4px",
  border: "1px solid #ccc",
};