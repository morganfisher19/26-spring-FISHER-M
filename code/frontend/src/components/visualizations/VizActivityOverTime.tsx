import { useEffect, useRef, useState } from "react";
import * as d3 from "d3";
import "./VizAll.css";

const API_BASE = "http://localhost:5000";

interface RawVote {
  vote_id: string;
  vote_date: string;
  chamber: string;
  policy_area: string | null;
}

interface DataPoint {
  period: Date;
  vote_count: number;
}

type Chamber = "" | "H" | "S";
type Granularity = "day" | "week" | "month";

// Use local-time dates to avoid UTC midnight vs local midnight mismatches with D3
const SESSION_START = new Date(2025, 0, 3); // 119th Congress, Friday Jan 3 2025
const FIRST_MONDAY  = new Date(2025, 0, 6); // First Monday after session start

// ── build the fixed period domain anchored to SESSION_START ─────────────────
function buildDomain(gran: Granularity, maxDate: Date): Date[] {
  const periods: Date[] = [];

  if (gran === "day") {
    // Every calendar day from Jan 3 to maxDate
    let cur = d3.timeDay.floor(SESSION_START);
    const end = d3.timeDay.floor(maxDate);
    while (cur <= end) {
      periods.push(new Date(cur));
      cur = new Date(d3.timeDay.offset(cur, 1));
    }

  } else if (gran === "week") {
    // Weeks starting on the session start day (Friday Jan 3),
    // then rolling over to Monday-Sunday from Jan 6 onward.
    // Week 1: Jan 3–5 (partial). Week 2: Jan 6–12. Week 3: Jan 13–19 …
    // We represent each week by its Monday (or Jan 3 for week 1).
    const end = d3.timeDay.floor(maxDate);
    // First partial week starts on SESSION_START
    periods.push(new Date(SESSION_START));
    let cur = new Date(FIRST_MONDAY);
    while (cur <= end) {
      periods.push(new Date(cur));
      cur = new Date(d3.timeDay.offset(cur, 7));
    }

  } else {
    // Calendar months: Jan 2025, Feb 2025, …
    let cur = d3.timeMonth.floor(SESSION_START);
    const end = d3.timeMonth.floor(maxDate);
    while (cur <= end) {
      periods.push(new Date(cur));
      cur = new Date(d3.timeMonth.offset(cur, 1));
    }
  }

  return periods;
}

// ── map a vote date to its period start ─────────────────────────────────────
function bucketDate(isoDate: string, gran: Granularity): Date {
  const d = new Date(isoDate);

  if (gran === "day") return d3.timeDay.floor(d);

  if (gran === "week") {
    const day = d3.timeDay.floor(d);
    // Anything before the first Monday belongs to the partial week (Jan 3)
    const firstMonday = FIRST_MONDAY;
    if (day < firstMonday) return new Date(SESSION_START);
    // Otherwise find the Monday on or before this day
    return d3.timeMonday.floor(day);
  }

  return d3.timeMonth.floor(d);
}

// ── aggregate raw votes into DataPoints ─────────────────────────────────────
function aggregate(
  raw: RawVote[],
  chamber: Chamber,
  policyArea: string,
  gran: Granularity
): DataPoint[] {
  const filtered = raw.filter((v) => {
    if (chamber && v.chamber !== chamber) return false;
    if (policyArea && v.policy_area !== policyArea) return false;
    return true;
  });

  const counts = new Map<number, number>();
  for (const v of filtered) {
    const key = bucketDate(v.vote_date, gran).getTime();
    counts.set(key, (counts.get(key) ?? 0) + 1);
  }

  // Use the fixed domain so every period is represented (zero-filled)
  const maxDate = raw.reduce((max, v) => {
    const d = new Date(v.vote_date);
    return d > max ? d : max;
  }, SESSION_START);

  return buildDomain(gran, maxDate).map((period) => ({
    period,
    vote_count: counts.get(period.getTime()) ?? 0,
  }));
}

// ── D3 chart setup (runs once) ───────────────────────────────────────────────
const MARGIN = { top: 20, right: 20, bottom: 80, left: 60 };
const W = 700 - MARGIN.left - MARGIN.right;
const H = 380 - MARGIN.top - MARGIN.bottom;
const DURATION = 500;

function initChart(svgEl: SVGSVGElement) {
  const root = d3
    .select(svgEl)
    .attr("width",  W + MARGIN.left + MARGIN.right)
    .attr("height", H + MARGIN.top  + MARGIN.bottom);

  const g = root
    .append("g")
    .attr("transform", `translate(${MARGIN.left},${MARGIN.top})`);

  // clip path so bars don't overflow during transition
  g.append("defs")
    .append("clipPath")
    .attr("id", "chart-clip")
    .append("rect")
    .attr("width", W)
    .attr("height", H);

  const chartArea = g.append("g").attr("clip-path", "url(#chart-clip)");
  chartArea.append("g").attr("class", "bars-group");

  g.append("g").attr("class", "x-axis").attr("transform", `translate(0,${H})`);
  g.append("g").attr("class", "y-axis");

  // Y label (static)
  g.append("text")
    .attr("class", "y-title")
    .attr("transform", "rotate(-90)")
    .attr("x", -H / 2)
    .attr("y", -48)
    .attr("text-anchor", "middle")
    .attr("font-size", "14px")
    .attr("font-weight", "bold")
    .attr("fill", "#6B3A3A")
    .text("Number of Votes");

  return root;
}

// ── D3 chart update (runs on every filter change) ────────────────────────────
function updateChart(
  svgEl: SVGSVGElement,
  data: DataPoint[],
  gran: Granularity
) {
  const root = d3.select(svgEl);
  const g    = root.select<SVGGElement>("g");

  const padding = gran === "day" ? 0.1 : gran === "week" ? 0.15 : 0.2;

  const x = d3.scaleBand<Date>()
    .domain(data.map((d) => d.period))
    .range([0, W])
    .padding(padding);

  const maxCount = d3.max(data, (d) => d.vote_count) ?? 0;

  const y = d3.scaleLinear()
    .domain([0, maxCount])
    .nice()
    .range([H, 0]);

  const t = d3.transition().duration(DURATION).ease(d3.easeCubicInOut);

  // bars (join pattern)
  const bars = g.select<SVGGElement>(".bars-group")
    .selectAll<SVGRectElement, DataPoint>("rect")
    .data(data, (d) => d.period.getTime());

  bars.exit().transition(t).attr("y", H).attr("height", 0).remove();

  bars.enter()
    .append("rect")
    .attr("fill", "#E6677F")
    .attr("x",      (d) => x(d.period) ?? 0)
    .attr("width",  x.bandwidth())
    .attr("y",      H)
    .attr("height", 0)
    .merge(bars as any)
    .transition(t)
    .attr("x",      (d) => x(d.period) ?? 0)
    .attr("width",  x.bandwidth())
    .attr("y",      (d) => d.vote_count === 0 ? H : y(d.vote_count))
    .attr("height", (d) => d.vote_count === 0 ? 0 : H - y(d.vote_count));

  // axes
  const xFmt = gran === "month" ? d3.timeFormat("%b %Y") : d3.timeFormat("%b %d '%y");

  // For days, tick every 7 bars (weekly); for weeks every 4; months every 1
  const tickData = gran === "month"
  ? data
  : gran === "day"
  ? data.filter((d) => d.period.getDate() === 1)
  : data.filter((_, i) => i % 5 === 0);

  g.select<SVGGElement>(".x-axis")
    .call(
      d3.axisBottom(
        d3.scaleOrdinal<Date, number>()
          .domain(tickData.map((d) => d.period))
          .range(tickData.map((d) => (x(d.period) ?? 0) + x.bandwidth() / 2))
      ).tickValues(tickData.map((d) => d.period))
       .tickFormat((d) => xFmt(d as Date)) as any
    )
    .selectAll("text")
    .attr("transform", "rotate(-35)")
    .style("text-anchor", "end")
    .style("font-size", "14px")
    .style("fill", "#6B3A3A");

  // Extend domain line to full width and apply axis colors
  g.select<SVGGElement>(".x-axis")
    .select(".domain")
    .attr("d", `M0,0H${W}`);

  g.select<SVGGElement>(".x-axis")
    .selectAll<SVGLineElement | SVGPathElement, unknown>("line, path")
    .style("stroke", "#6B3A3A");

  g.select<SVGGElement>(".y-axis")
    .transition(t)
    .call(
      d3.axisLeft(y)
        .ticks(Math.min(6, maxCount))
        .tickFormat(d3.format(",d")) as any
    );

  g.select<SVGGElement>(".y-axis")
    .selectAll("text")
    .style("font-size", "14px")
    .style("fill", "#6B3A3A");

  g.select<SVGGElement>(".y-axis")
    .selectAll<SVGLineElement | SVGPathElement, unknown>("line, path")
    .style("stroke", "#6B3A3A");
}

// ── Component ────────────────────────────────────────────────────────────────
export default function VizActivityOverTime() {
  const svgRef       = useRef<SVGSVGElement>(null);
  const chartReady   = useRef(false);

  const [rawVotes,   setRawVotes]   = useState<RawVote[]>([]);
  const [policyAreas, setPolicyAreas] = useState<string[]>([]);
  const [loading,    setLoading]    = useState(true);
  const [error,      setError]      = useState<string | null>(null);

  // filter state — default: all
  const [chamber,    setChamber]    = useState<Chamber>("");
  const [granularity, setGranularity] = useState<Granularity>("week");
  const [policyArea, setPolicyArea] = useState("");

  // fetch raw votes once
  useEffect(() => {
    fetch(`${API_BASE}/api/visualizations/activity_over_time`)
      .then((r) => r.json())
      .then((json: RawVote[]) => {
        setRawVotes(json);
        setLoading(false);
      })
      .catch(() => {
        setError("Failed to load data.");
        setLoading(false);
      });
  }, []);

  // fetch policy areas once
  useEffect(() => {
    fetch(`${API_BASE}/api/policy_areas`)
      .then((r) => r.json())
      .then(setPolicyAreas)
      .catch(() => {});
  }, []);

  // init chart once data arrives
  useEffect(() => {
    if (!svgRef.current || !rawVotes.length || chartReady.current) return;
    initChart(svgRef.current);
    chartReady.current = true;
  }, [rawVotes]);

  // update chart whenever filters or raw data change
  useEffect(() => {
    if (!svgRef.current || !chartReady.current || !rawVotes.length) return;
    const data = aggregate(rawVotes, chamber, policyArea, granularity);
    updateChart(svgRef.current, data, granularity);
  }, [rawVotes, chamber, granularity, policyArea]);

  return (
    <div className='activity-container'>
      <div className="filter-container">
        <div className='single-filter-container'>
          <label>Chamber:</label>
          <select value={chamber} onChange={(e) => setChamber(e.target.value as Chamber)} className="viz-filter-select">
            <option value="">Both</option>
            <option value="H">House</option>
            <option value="S">Senate</option>
          </select>
        </div>
        <div className='single-filter-container'>
          <label>Time Period:</label>
          <select value={granularity} onChange={(e) => setGranularity(e.target.value as Granularity)} className="viz-filter-select">
            <option value="day">Day</option>
            <option value="week">Week</option>
            <option value="month">Month</option>
          </select>
        </div>
        <div className='single-filter-container'>
          <label>Policy Area:</label>
          <select value={policyArea} onChange={(e) => setPolicyArea(e.target.value)} className="viz-filter-select">
            <option value="">All</option>
            {policyAreas.map((pa) => (
              <option key={pa} value={pa}>{pa}</option>
            ))}
          </select>
        </div>
      </div>
      <div className='error-handling'>
        {loading && <p>Loading...</p>}
        {error   && <p>{error}</p>}
      </div>
      {!loading && !error && (
        <div className='chart-container'>
          <svg ref={svgRef} />
        </div>
      )}
    </div>
  );
}

