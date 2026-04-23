import { useEffect, useRef, useState } from "react";
import * as d3 from "d3";
import "./VizAll.css";

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
const MARGIN = { top: 40, right: 40, bottom: 60, left: 80 };

function classifyVotes(votes: VoteData[]): BarData[] {
  let agree = 0, disagree = 0;

  for (const vote of votes) {
    const d = vote.party_totals.find((p) => p.party === "D");
    const r = vote.party_totals.find((p) => p.party === "R");
    if (!d || !r) continue;

    const bothYes = d.yes_pct > AGREEMENT_THRESHOLD && r.yes_pct > AGREEMENT_THRESHOLD;
    const bothNo  = d.yes_pct <= AGREEMENT_THRESHOLD && r.yes_pct <= AGREEMENT_THRESHOLD;

    if (bothYes || bothNo) agree++;
    else disagree++;
  }

  return [
    { label: "Bipartisan", count: agree,    color: "#A8C3A0" },
    { label: "Partisan",   count: disagree, color: "#E6677F" },
  ];
}

export default function VizBipartisanship() {
  const svgRef      = useRef<SVGSVGElement>(null);
  const containerRef  = useRef<HTMLDivElement>(null);
  const [containerWidth, setContainerWidth] = useState(800);

  const [allVotes,   setAllVotes]   = useState<VoteData[]>([]);
  const [policyAreas, setPolicyAreas] = useState<string[]>([]);
  const [chamber,    setChamber]    = useState("all");
  const [policyArea, setPolicyArea] = useState("all");
  const [loading,    setLoading]    = useState(true);
  const [error,      setError]      = useState<string | null>(null);

  // ── ResizeObserver ────────────────────────────────────────────
  useEffect(() => {
    if (!containerRef.current) return;
    const observer = new ResizeObserver(([entry]) => {
      setContainerWidth(Math.min(entry.contentRect.width, 800));
    });
    observer.observe(containerRef.current);
    return () => observer.disconnect();
  }, [loading]);

  // Fetch all data once on mount
  useEffect(() => {
    setLoading(true);
    Promise.all([
      fetch("/api/visualizations/bipartisanship").then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json() as Promise<VoteData[]>;
      }),
      fetch("/api/policy_areas").then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json() as Promise<string[]>;
      }),
    ])
      .then(([votes, areas]) => {
        setAllVotes(votes);
        setPolicyAreas(areas);
        setLoading(false);
      })
      .catch((e) => {
        setError(e.message);
        setLoading(false);
      });
  }, []);

  // Draw / update chart whenever data or filters change
  useEffect(() => {
    if (!allVotes.length || !svgRef.current) return;

    const WIDTH = containerWidth - MARGIN.left - MARGIN.right;
    const HEIGHT = WIDTH * 5 / 8;

    // Apply filters client-side
    const filtered = allVotes.filter((v) => {
      const chamberMatch = chamber === "all" || v.chamber === chamber;
      const areaMatch    = policyArea === "all" || v.policy_area === policyArea;
      return chamberMatch && areaMatch;
    });

    const data  = classifyVotes(filtered);
    const total = data.reduce((s, d) => s + d.count, 0);
    const t     = d3.transition().duration(500).ease(d3.easeCubicInOut);

    const svg = d3.select(svgRef.current);

    // Initialize SVG structure if not already done
    if (svg.select("#chart-root").empty()) {
      svg
        .attr("width",  WIDTH  + MARGIN.left + MARGIN.right)
        .attr("height", HEIGHT + MARGIN.top  + MARGIN.bottom);

      const g = svg.append("g")
        .attr("id", "chart-root")
        .attr("transform", `translate(${MARGIN.left},${MARGIN.top})`);

      g.append("g").attr("id", "x-axis").attr("transform", `translate(0,${HEIGHT})`);
      g.append("g").attr("id", "y-axis");

      g.append("text")
        .attr("transform", "rotate(-90)")
        .attr("x", -HEIGHT / 2)
        .attr("y", -50)
        .attr("text-anchor", "middle")
        .style("font-size", "14px")
        .style("font-weight", "bold")
        .style("fill", "#6B3A3A")
        .text("Number of Votes");

      g.append("g").attr("id", "bars");
      g.append("g").attr("id", "bar-labels");
    }

    const g = svg.select<SVGGElement>("#chart-root");

    // Scales
    const x = d3.scaleBand()
      .domain(data.map((d) => d.label))
      .range([0, WIDTH])
      .padding(0.4);

    const y = d3.scaleLinear()
      .domain([0, Math.max(1, d3.max(data, (d) => d.count) ?? 0)])
      .nice()
      .range([HEIGHT, 0]);

    // Axes
    g.select<SVGGElement>("#x-axis")
      .transition(t)
      .call(d3.axisBottom(x))
      .selectAll("text")
      .style("font-size", "14px")
      .style("fill", "#6B3A3A")
      .style("font-weight", "normal");
    
    g.select<SVGGElement>("#x-axis")
      .selectAll("line, path")
      .style("stroke", "#6B3A3A");

    g.select<SVGGElement>("#y-axis")
      .transition(t)
      .call(
        d3.axisLeft(y)
          .ticks(Math.min(6, d3.max(data, (d) => d.count) ?? 0))
          .tickFormat(d3.format("d"))  // integers only
      )
      .selectAll("text")
      .style("font-size", "14px")
      .style("fill", "#6B3A3A")
      .style("font-weight", "normal");

    g.select<SVGGElement>("#y-axis")
      .selectAll("line, path")
      .style("stroke", "#6B3A3A");

    // Bars
    g.select("#bars")
      .selectAll<SVGRectElement, BarData>("rect")
      .data(data, (d) => d.label)
      .join(
        (enter) =>
          enter.append("rect")
            .attr("x",      (d) => x(d.label) ?? 0)
            .attr("y",      HEIGHT)
            .attr("width",  x.bandwidth())
            .attr("height", 0)
            .attr("fill",   (d) => d.color)
            .attr("rx", 4)
            .call((e) =>
              e.transition(t)
                .attr("y",      (d) => y(d.count))
                .attr("height", (d) => HEIGHT - y(d.count))
            ),
        (update) =>
          update.call((u) =>
            u.transition(t)
              .attr("x",      (d) => x(d.label) ?? 0)
              .attr("y",      (d) => y(d.count))
              .attr("width",  x.bandwidth())
              .attr("height", (d) => HEIGHT - y(d.count))
              .attr("fill",   (d) => d.color)
          ),
        (exit) =>
          exit.call((e) =>
            e.transition(t)
              .attr("y",      HEIGHT)
              .attr("height", 0)
              .remove()
          )
      );

    // Bar labels
    g.select("#bar-labels")
      .selectAll<SVGTextElement, BarData>("text")
      .data(data, (d) => d.label)
      .join(
        (enter) =>
          enter.append("text")
            .attr("x",            (d) => (x(d.label) ?? 0) + x.bandwidth() / 2)
            .attr("y",            HEIGHT)
            .attr("text-anchor",  "middle")
            .style("font-size",   "14px")
            .style("font-weight", "bold")
            .style("fill",        "#6B3A3A")
            .text((d) => `${d.count} (${total ? ((d.count / total) * 100).toFixed(1) : 0}%)`)
            .call((e) => e.transition(t).attr("y", (d) => y(d.count) - 8)),
        (update) =>
          update.call((u) =>
            u.transition(t)
              .attr("x", (d) => (x(d.label) ?? 0) + x.bandwidth() / 2)
              .attr("y", (d) => y(d.count) - 8)
              .tween("text", function (d) {
                const el     = this as SVGTextElement;
                const prev   = parseFloat(el.textContent ?? "0") || d.count;
                const interp = d3.interpolateNumber(prev, d.count);
                return (t) => {
                  const v = Math.round(interp(t));
                  el.textContent = `${v} (${total ? ((v / total) * 100).toFixed(1) : 0}%)`;
                };
              })
          ),
        (exit) =>
          exit.call((e) =>
            e.transition(t)
              .attr("y", HEIGHT)
              .style("opacity", 0)
              .remove()
          )
      );
  }, [allVotes, chamber, policyArea, containerWidth]);


  return (
    <div className='bipartisan-container' ref={containerRef}>
      {/* Filters */}
      <div className='filter-container'>
        <div className='single-filter-container'>
          <label>Chamber:</label>
          <select
            value={chamber}
            onChange={(e) => setChamber(e.target.value)}
          >
            <option value="all">Both</option>
            <option value="H">House</option>
            <option value="S">Senate</option>
          </select>
        </div>
        <div className='single-filter-container'>
          <label>Policy Area:</label>
          <select
            value={policyArea}
            onChange={(e) => setPolicyArea(e.target.value)}
          >
            <option value="all">All</option>
            {policyAreas.map((a) => (
              <option key={a} value={a}>{a}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Chart area */}
      <div className='error-handling'>
        {loading && <p>Loading...</p>}
        {error   && <p>Error: {error}</p>}
      </div>
      {!loading && !error && (
        <div className='chart-container'>
          <svg ref={svgRef} />
        </div>
      )}
      <div className='text-container'>
        <p>A vote is "bipartisan" when both parties voted the same way (both majority yes or both majority no).</p>
      </div>
    </div>
  );
}