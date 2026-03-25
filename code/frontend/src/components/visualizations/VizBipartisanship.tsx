import { useEffect, useRef, useState } from "react";
import * as d3 from "d3";

interface PartyTotal {
  party: string;
  yes_count: number;
  no_count: number;
  yes_pct: number;
}

interface VoteData {
  vote_id: string;
  vote_date: string;
  question: string;
  result: string;
  chamber: string;
  policy_area: string | null;
  party_totals: PartyTotal[];
}

interface BarData {
  label: string;
  count: number;
  color: string;
}

const AGREEMENT_THRESHOLD = 0.5; // both parties > 50% yes = agreement

function classifyVotes(votes: VoteData[]): BarData[] {
  let agree = 0;
  let disagree = 0;

  for (const vote of votes) {
    const d = vote.party_totals.find((p) => p.party === "D");
    const r = vote.party_totals.find((p) => p.party === "R");
    if (!d || !r) continue;

    const bothYes = d.yes_pct > AGREEMENT_THRESHOLD && r.yes_pct > AGREEMENT_THRESHOLD;
    const bothNo = d.yes_pct <= AGREEMENT_THRESHOLD && r.yes_pct <= AGREEMENT_THRESHOLD;

    if (bothYes || bothNo) agree++;
    else disagree++;
  }

  return [
    { label: "Bipartisan", count: agree, color: "#6baed6" },
    { label: "Partisan", count: disagree, color: "#fc8d59" },
  ];
}

export default function VizBipartisanship() {
  const svgRef = useRef<SVGSVGElement>(null);
  const [votes, setVotes] = useState<VoteData[]>([]);
  const [chamber, setChamber] = useState("H");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch data when chamber changes
  useEffect(() => {
    setLoading(true);
    setError(null);
    fetch(`/api/visualizations/bipartisanship?chamber=${chamber}`)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((data: VoteData[]) => {
        setVotes(data);
        setLoading(false);
      })
      .catch((e) => {
        setError(e.message);
        setLoading(false);
      });
  }, [chamber]);

  // Draw chart when data changes
  useEffect(() => {
    if (!votes.length || !svgRef.current) return;

    const data = classifyVotes(votes);
    const total = data.reduce((s, d) => s + d.count, 0);

    const margin = { top: 40, right: 30, bottom: 60, left: 70 };
    const width = 500 - margin.left - margin.right;
    const height = 360 - margin.top - margin.bottom;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    svg
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom);

    const g = svg
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Scales
    const x = d3
      .scaleBand()
      .domain(data.map((d) => d.label))
      .range([0, width])
      .padding(0.4);

    const y = d3
      .scaleLinear()
      .domain([0, d3.max(data, (d) => d.count) as number])
      .nice()
      .range([height, 0]);

    // Axes
    g.append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(x))
      .selectAll("text")
      .style("font-size", "14px");

    g.append("g").call(d3.axisLeft(y).ticks(6));

    // Y-axis label
    g.append("text")
      .attr("transform", "rotate(-90)")
      .attr("x", -height / 2)
      .attr("y", -50)
      .attr("text-anchor", "middle")
      .style("font-size", "12px")
      .style("fill", "#555")
      .text("Number of Votes");

    // Bars
    g.selectAll("rect")
      .data(data)
      .join("rect")
      .attr("x", (d) => x(d.label) as number)
      .attr("y", (d) => y(d.count))
      .attr("width", x.bandwidth())
      .attr("height", (d) => height - y(d.count))
      .attr("fill", (d) => d.color)
      .attr("rx", 4);

    // Count labels on bars
    g.selectAll(".bar-label")
      .data(data)
      .join("text")
      .attr("class", "bar-label")
      .attr("x", (d) => (x(d.label) as number) + x.bandwidth() / 2)
      .attr("y", (d) => y(d.count) - 8)
      .attr("text-anchor", "middle")
      .style("font-size", "14px")
      .style("font-weight", "bold")
      .style("fill", "#333")
      .text((d) => `${d.count} (${((d.count / total) * 100).toFixed(1)}%)`);

  }, [votes]);

  return (
    <div>
      {/* Filter */}
      <div style={{ marginBottom: "1rem", display: "flex", alignItems: "center", gap: "0.75rem" }}>
        <label style={{ fontWeight: 500 }}>Chamber:</label>
        <select
          value={chamber}
          onChange={(e) => setChamber(e.target.value)}
          style={{ padding: "0.25rem 0.5rem", fontSize: "14px" }}
        >
          <option value="H">House</option>
          <option value="S">Senate</option>
        </select>
      </div>

      {/* Chart area */}
      {loading && <p style={{ color: "#888" }}>Loading...</p>}
      {error && <p style={{ color: "red" }}>Error: {error}</p>}
      {!loading && !error && (
        <div>
          <p style={{ fontSize: "13px", color: "#666", marginBottom: "0.5rem" }}>
            A vote is "bipartisan" when both parties voted the same way (both majority yes or both majority no).
          </p>
          <svg ref={svgRef} />
        </div>
      )}
    </div>
  );
}