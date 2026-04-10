import { useEffect, useRef, useState } from "react";
import * as d3 from "d3";

const API_BASE = "http://localhost:5000";

interface Member {
  member_id: string;
  full_name: string;
  party: string;
  chamber: string;
  state_name: string;
  score: number;
}

type Metric = "laws" | "sponsored" | "cosponsors";
type Chamber = "" | "H" | "S";
type Party = "" | "D" | "R";

const METRIC_LABELS: Record<Metric, string> = {
  laws: "Laws Passed",
  sponsored: "Bills Sponsored",
  cosponsors: "Cosponsors Attracted",
};

const PARTY_COLORS: Record<string, string> = {
  D: "#2563eb",
  R: "#dc2626",
  I: "#6b7280",
};

export default function VizTopInfluencers() {
  const svgRef = useRef<SVGSVGElement>(null);
  const [data, setData] = useState<Member[]>([]);
  const [policyAreas, setPolicyAreas] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [metric, setMetric] = useState<Metric>("laws");
  const [chamber, setChamber] = useState<Chamber>("");
  const [party, setParty] = useState<Party>("");
  const [policyArea, setPolicyArea] = useState("");

  // Load policy areas once
  useEffect(() => {
    fetch(`${API_BASE}/api/policy_areas`)
      .then((r) => r.json())
      .then(setPolicyAreas)
      .catch(() => {});
  }, []);

  // Reload when filters change
  useEffect(() => {
    setLoading(true);
    const params = new URLSearchParams({ metric, limit: "10" });
    if (chamber) params.set("chamber", chamber);
    if (party) params.set("party", party);
    if (policyArea) params.set("policy_area", policyArea);

    fetch(`${API_BASE}/api/visualizations/top_influencers?${params}`)
      .then((r) => r.json())
      .then((json) => {
        setData(json.data);
        setLoading(false);
      })
      .catch(() => {
        setError("Failed to load data.");
        setLoading(false);
      });
  }, [metric, chamber, party, policyArea]);

  // Draw chart
  useEffect(() => {
    if (!data.length || !svgRef.current) return;

    const margin = { top: 10, right: 60, bottom: 40, left: 180 };
    const width = 640 - margin.left - margin.right;
    const barHeight = 32;
    const height = data.length * barHeight;

    d3.select(svgRef.current).selectAll("*").remove();

    const svg = d3
      .select(svgRef.current)
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Sorted descending — top member at top
    const sorted = [...data].sort((a, b) => b.score - a.score);

    const y = d3
      .scaleBand()
      .domain(sorted.map((d) => d.member_id))
      .range([0, height])
      .padding(0.25);

    const x = d3
      .scaleLinear()
      .domain([0, d3.max(sorted, (d) => d.score) ?? 0])
      .nice()
      .range([0, width]);

    // Bars
    svg
      .selectAll("rect")
      .data(sorted)
      .join("rect")
      .attr("y", (d) => y(d.member_id) ?? 0)
      .attr("x", 0)
      .attr("height", y.bandwidth())
      .attr("width", (d) => x(d.score))
      .attr("fill", (d) => PARTY_COLORS[d.party] ?? "#6b7280")
      .attr("rx", 3);

    // Score labels
    svg
      .selectAll(".score-label")
      .data(sorted)
      .join("text")
      .attr("class", "score-label")
      .attr("y", (d) => (y(d.member_id) ?? 0) + y.bandwidth() / 2)
      .attr("x", (d) => x(d.score) + 6)
      .attr("dominant-baseline", "middle")
      .attr("font-size", "12px")
      .attr("fill", "#333")
      .text((d) => d.score.toLocaleString());

    // Y axis — member names
    const yAxis = d3
      .axisLeft(y)
      .tickFormat((memberId) => {
        const m = sorted.find((d) => d.member_id === memberId);
        return m ? m.full_name : memberId;
      });

    svg
      .append("g")
      .call(yAxis)
      .selectAll("text")
      .style("font-size", "12px");

    // X axis
    svg
      .append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(x).ticks(5).tickFormat(d3.format(",d")));

    // X label
    svg
      .append("text")
      .attr("x", width / 2)
      .attr("y", height + 36)
      .attr("text-anchor", "middle")
      .attr("font-size", "12px")
      .attr("fill", "#555")
      .text(METRIC_LABELS[metric]);
  }, [data, metric]);

  return (
    <div>
      {/* Metric toggle */}
      <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem" }}>
        {(["laws", "sponsored", "cosponsors"] as Metric[]).map((m) => (
          <button
            key={m}
            onClick={() => setMetric(m)}
            style={{
              ...btnStyle,
              background: metric === m ? "#1e40af" : "#e5e7eb",
              color: metric === m ? "#fff" : "#333",
            }}
          >
            {METRIC_LABELS[m]}
          </button>
        ))}
      </div>

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
          <label style={labelStyle}>Party</label>
          <select value={party} onChange={(e) => setParty(e.target.value as Party)} style={selectStyle}>
            <option value="">All</option>
            <option value="D">Democrat</option>
            <option value="R">Republican</option>
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

      {/* Legend */}
      <div style={{ display: "flex", gap: "1rem", marginBottom: "0.75rem" }}>
        {Object.entries(PARTY_COLORS).map(([p, color]) => (
          <div key={p} style={{ display: "flex", alignItems: "center", gap: "4px", fontSize: "12px" }}>
            <div style={{ width: 12, height: 12, borderRadius: 2, background: color }} />
            {p === "D" ? "Democrat" : p === "R" ? "Republican" : "Independent"}
          </div>
        ))}
      </div>

      {loading && <p>Loading...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      {!loading && !error && data.length === 0 && <p>No results for these filters.</p>}
      {!loading && !error && data.length > 0 && <svg ref={svgRef} />}
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

const btnStyle: React.CSSProperties = {
  fontSize: "13px",
  padding: "5px 12px",
  borderRadius: "4px",
  border: "none",
  cursor: "pointer",
};