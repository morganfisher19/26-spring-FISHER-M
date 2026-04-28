import { useEffect, useRef, useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import * as d3 from "d3";
import "./VizAll.css";

const API_BASE = "http://localhost:5000";

// Shape returned by /api/visualizations/top_influencers
interface RawRow {
  member_id: string;
  full_name: string;
  party: string;
  chamber: string;
  state_name: string;
  policy_area: string | null;
  bills_sponsored: number;
  laws_passed: number;
  total_cosponsors: number;
}

// One bar = one member (aggregated across policy areas after client-side filter)
interface MemberBar {
  member_id: string;
  full_name: string;
  party: string;
  chamber: string;
  state_name: string;
  score: number;
}

type Metric  = "laws_passed" | "bills_sponsored" | "total_cosponsors";
type Chamber = "" | "H" | "S";
type Party   = "" | "D" | "R";

const METRIC_LABELS: Record<Metric, string> = {
  laws_passed:      "Laws Passed",
  bills_sponsored:  "Bills Sponsored",
  total_cosponsors: "Cosponsors Attracted",
};

const PARTY_COLORS: Record<string, string> = {
  D: "#4A7FCF",
  R: "#C65A5A",
  I: "#6b7280",
};

const BROWN = "#6B3A3A";

const TOP_N = 10;

export default function VizTopInfluencers() {
  const svgRef = useRef<SVGSVGElement>(null);

  const [raw, setRaw]           = useState<RawRow[]>([]);
  const [policyAreas, setPolicyAreas] = useState<string[]>([]);
  const [loading, setLoading]   = useState(true);
  const [error, setError]       = useState<string | null>(null);

  const [metric, setMetric]         = useState<Metric>("laws_passed");
  const [chamber, setChamber]       = useState<Chamber>("");
  const [party, setParty]           = useState<Party>("");
  const [policyArea, setPolicyArea] = useState("");
  const navigate = useNavigate();

  // Fetch all data once
  useEffect(() => {
    Promise.all([
      fetch(`${API_BASE}/api/visualizations/top_influencers`).then(r => r.json()),
      fetch(`${API_BASE}/api/policy_areas`).then(r => r.json()),
    ])
      .then(([rows, areas]: [RawRow[], string[]]) => {
        setRaw(rows);
        setPolicyAreas(areas);
        setLoading(false);
      })
      .catch(() => {
        setError("Failed to load data.");
        setLoading(false);
      });
  }, []);

  // Client-side filter + aggregate + rank
  const chartData = useMemo<MemberBar[]>(() => {
    const filtered = raw.filter(r =>
      (chamber     === "" || r.chamber     === chamber) &&
      (party       === "" || r.party       === party)   &&
      (policyArea  === "" || r.policy_area === policyArea)
    );

    // Aggregate per member (multiple rows when grouping by policy_area on backend)
    const byMember = new Map<string, MemberBar>();
    for (const r of filtered) {
      const existing = byMember.get(r.member_id);
      if (existing) {
        existing.score +=
          metric === "laws_passed"      ? r.laws_passed      :
          metric === "bills_sponsored"  ? r.bills_sponsored  :
          r.total_cosponsors;
      } else {
        byMember.set(r.member_id, {
          member_id: r.member_id,
          full_name: r.full_name,
          party:     r.party,
          chamber:   r.chamber,
          state_name:r.state_name,
          score:
            metric === "laws_passed"      ? r.laws_passed      :
            metric === "bills_sponsored"  ? r.bills_sponsored  :
            r.total_cosponsors,
        });
      }
    }

    return Array.from(byMember.values())
      .filter(d => d.score > 0) 
      .sort((a, b) => b.score - a.score)
      .slice(0, TOP_N);
  }, [raw, metric, chamber, party, policyArea]);

  // D3 chart with transitions
  useEffect(() => {
    if (!svgRef.current) return;

    const margin     = { top: 16, right: 64, bottom: 48, left: 190 };
    const totalWidth = 660;
    const barHeight  = 36;
    const height     = TOP_N * barHeight;
    const width      = totalWidth - margin.left - margin.right;
    const DURATION   = 500;

    const svgEl = d3.select(svgRef.current);

    // One-time SVG setup
    if (svgEl.select("g.root").empty()) {
      svgEl
        .attr("width",  totalWidth)
        .attr("height", height + margin.top + margin.bottom);

      const root = svgEl.append("g")
        .attr("class", "root")
        .attr("transform", `translate(${margin.left},${margin.top})`);

      root.append("g").attr("class", "x-axis")
        .attr("transform", `translate(0,${height})`);
      root.append("g").attr("class", "y-axis");
      root.append("g").attr("class", "bars");
      root.append("g").attr("class", "score-labels")
      root.append("text").attr("class", "x-label")
        .attr("x", width / 2)
        .attr("y", height + 42)
        .attr("text-anchor", "middle")
        .attr("font-size", "14px")
        .attr("fill", BROWN);
    }

    const root = svgEl.select<SVGGElement>("g.root");

    // Scales
    const y = d3.scaleBand()
      .domain(chartData.map(d => d.member_id))
      .range([0, height])
      .padding(0.28);

    const x = d3.scaleLinear()
      .domain([0, d3.max(chartData, d => d.score) ?? 1])
      .nice()
      .range([0, width]);

    // X axis
    root.select<SVGGElement>(".x-axis")
      .transition().duration(DURATION)
      .call(
        d3.axisBottom(x)
          .ticks(Math.min(5, d3.max(chartData, d => d.score) ?? 1))
          .tickFormat(d3.format(",d")) as any
      )
      .call(g => {
        g.selectAll("text").attr("fill", BROWN).attr("font-size", "14px");
        g.selectAll("line, path").attr("stroke", BROWN);
      });

    // Y axis
    root.select<SVGGElement>(".y-axis")
      .transition().duration(DURATION)
      .call(
        d3.axisLeft(y).tickFormat(memberId => {
          const m = chartData.find(d => d.member_id === memberId);
          return m ? m.full_name : String(memberId);
        }) as any
      )
      .call(g => {
        g.selectAll("text").attr("fill", BROWN).attr("font-size", "14px");
        g.selectAll("line, path").attr("stroke", BROWN);
      });

    // Bars
    const bars = root.select(".bars")
      .selectAll<SVGRectElement, MemberBar>("rect")
      .data(chartData, d => d.member_id);

    bars.enter()
      .append("rect")
      .attr("y",      d => y(d.member_id) ?? 0)
      .attr("x",      0)
      .attr("height", y.bandwidth())
      .attr("width",  0)
      .attr("fill",   d => PARTY_COLORS[d.party] ?? "#6b7280")
      .attr("rx",     3)
      .style("cursor", "pointer")
      .on("click", (event, d) => navigate(`/member/${d.member_id}`))
      .on("mouseover", (event, d) => d3.select(event.currentTarget).attr("fill", d3.color(PARTY_COLORS[d.party] ?? "#6b7280")!.darker(0.6).toString()))
      .on("mouseout",  (event, d) => d3.select(event.currentTarget).attr("fill", PARTY_COLORS[d.party] ?? "#6b7280"))
      .merge(bars as any)
      .transition().duration(DURATION)
      .attr("y",      d => y(d.member_id) ?? 0)
      .attr("height", y.bandwidth())
      .attr("width",  d => x(d.score))
      .attr("fill",   d => PARTY_COLORS[d.party] ?? "#6b7280");

    bars.exit()
      .transition().duration(DURATION)
      .attr("width", 0)
      .remove();

    // Score labels
    const labels = root.select(".score-labels")
      .selectAll<SVGTextElement, MemberBar>("text")
      .data(chartData, d => d.member_id);

    labels.enter()
      .append("text")
      .attr("y",                d => (y(d.member_id) ?? 0) + y.bandwidth() / 2)
      .attr("x",                d => x(d.score) + 6)
      .attr("dominant-baseline","middle")
      .attr("font-size",        "14px")
      .attr("fill",             BROWN)
      .attr("opacity",          0)
      .text(d => d.score.toLocaleString())
      .merge(labels as any)
      .transition().duration(DURATION)
      .attr("y",       d => (y(d.member_id) ?? 0) + y.bandwidth() / 2)
      .attr("x",       d => x(d.score) + 6)
      .attr("opacity", 1)
      .text(d => d.score.toLocaleString());

    labels.exit()
      .transition().duration(DURATION)
      .attr("opacity", 0)
      .remove();

    // X axis label
    root.select(".x-label")
      .transition().duration(DURATION)
      .text(METRIC_LABELS[metric])
      .attr("font-weight", "bold");

  }, [chartData, metric, navigate]);

  return (
    <div className="influencer-container">
      {/* Metric toggle */}
      <div className="chart-toggle">
        {(Object.keys(METRIC_LABELS) as Metric[]).map(m => (
          <button
            key={m}
            onClick={() => setMetric(m)}
            className={metric === m ? "toggleBtn active" : "toggleBtn"}
          >
            {METRIC_LABELS[m]}
          </button>
        ))}
      </div>
      {/* Filters */}
      <div className='filter-container'>
        <div className='single-filter-container'>
          <label>Chamber</label>
          <select value={chamber} onChange={e => setChamber(e.target.value as Chamber)}>
            <option value="">All</option>
            <option value="H">House</option>
            <option value="S">Senate</option>
          </select>
        </div>
        <div className='single-filter-container'>
          <label>Party</label>
          <select value={party} onChange={e => setParty(e.target.value as Party)}>
            <option value="">All</option>
            <option value="D">Democrat</option>
            <option value="R">Republican</option>
          </select>
        </div>
        <div className='single-filter-container'>
          <label>Policy Area</label>
          <select value={policyArea} onChange={e => setPolicyArea(e.target.value)}>
            <option value="">All</option>
            {policyAreas.map(pa => (
              <option key={pa} value={pa}>{pa}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Legend */}
      <div className='legend'>
        {Object.entries(PARTY_COLORS).map(([p, color]) => (
          <div key={p} style={{ display: "flex", alignItems: "center", gap: "4px", fontSize: "14px", color: "BROWN" }}>
            <div style={{ width: 12, height: 12, borderRadius: 2, background: color }} />
            {p === "D" ? "Democrat" : p === "R" ? "Republican" : "Independent"}
          </div>
        ))}
      </div>
      <div className='error-handling'>
        {loading && <p>Loading...</p>}
        {error   && <p style={{ color: "red" }}>{error}</p>}
        {!loading && !error && chartData.length === 0 && <p>No results for these filters.</p>}
      </div>
      {!loading && !error && (
        <div className='chart-container'>
          <svg ref={svgRef} />
        </div>
      )}
    </div>
  );
}