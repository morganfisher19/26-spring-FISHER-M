import { useEffect, useRef, useState } from "react";
import * as d3 from "d3";
import "./VizAll.css";
import { W, H, MARGIN, FONT_SIZE } from "./VizConfig";

interface Stage { label: string; count: number; }
type FunnelData = Record<string, Stage[]>;

const API_URL = import.meta.env.VITE_API_URL;
const margin = {
  ...MARGIN,
  bottom: W < 500 ? 150 : MARGIN.bottom,
};

export default function VizBillSurvival() {
  const svgRef    = useRef<SVGSVGElement>(null);
  const allData   = useRef<FunnelData>({});       // cache — never triggers re-render
  const [keys, setKeys]       = useState<string[]>([]);
  const [selected, setSelected] = useState("All");
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState<string | null>(null);

  // ── 1. Fetch everything ONCE ──────────────────────────────────
  useEffect(() => {
    fetch(`${API_URL}/api/visualizations/bill_funnel`)
      .then((r) => r.json())
      .then((json: FunnelData) => {
        allData.current = json;
        setKeys(Object.keys(json));   // triggers dropdown render
        setLoading(false);
      })
      .catch(() => { setError("Failed to load data."); setLoading(false); });
  }, []);

  // ── 2. Build chart skeleton once data arrives ─────────────────
  useEffect(() => {
    if (!keys.length || !svgRef.current) return;

    const svg = d3.select(svgRef.current)
      .attr("width",  W + margin.left + margin.right)
      .attr("height", H + margin.top  + margin.bottom);

    const g = svg.append("g")
      .attr("class", "chart-root")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    // Static axes groups (content filled on each update)
    g.append("g").attr("class", "x-axis").attr("transform", `translate(0,${H})`);
    g.append("g").attr("class", "y-axis");
    g.append("text")
      .attr("class", "y-label")
      .attr("transform", "rotate(-90)")
      .attr("x", -H / 2).attr("y", -65)
      .attr("text-anchor", "middle")
      .attr("font-size", FONT_SIZE)
      .attr("font-weight", "bold")
      .attr("fill", "#6B3A3A")
      .text("Number of Bills");

    // Trigger first render with "All"
    updateChart("All");
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [keys]);

  // ── 3. Pure D3 update (no React state touched) ────────────────
  function updateChart(key: string) {
    const data = allData.current[key];
    if (!data || !svgRef.current) return;

    const g = d3.select(svgRef.current).select<SVGGElement>("g.chart-root");

    const x = d3.scaleBand()
      .domain(data.map((d) => d.label))
      .range([0, W]).padding(0.3);

    const y = d3.scaleLinear()
      .domain([0, d3.max(data, (d) => d.count) ?? 0])
      .nice().range([H, 0]);

    const color = d3.scaleSequential()
      .domain([0, data.length - 1])
      .interpolator(d3.interpolateRgb("#FFB3C1", "#E6677F"));

    // Axes
    g.select<SVGGElement>(".x-axis")
      .transition().duration(400)
      .call(d3.axisBottom(x))
      .selectAll("text")

      .attr("transform", W < 500 ? "rotate(-90)" : null)
      .attr("x",         W < 500 ? -9            : null)
      .attr("dy",        W < 500 ? "-0.4em"      : "1.2em")
      .style("text-anchor", W < 500 ? "end"      : "middle")

      .style("font-size", FONT_SIZE)
      .style("fill", "#6B3A3A");
    g.select<SVGGElement>(".x-axis")
      .selectAll("line, path")
      .style("stroke", "#6B3A3A");

    g.select<SVGGElement>(".y-axis")
      .transition().duration(400)
      .call(d3.axisLeft(y).ticks(6).tickFormat(d3.format(",d")))
      .selectAll("text")
      .style("font-size", FONT_SIZE)
      .style("fill", "#6B3A3A");
    g.select<SVGGElement>(".y-axis")
      .selectAll("line, path")
      .style("stroke", "#6B3A3A");

    // Bars
    g.selectAll<SVGRectElement, Stage>("rect.bar")
      .data(data, (d) => d.label)
      .join(
        (enter) => enter.append("rect").attr("class", "bar")
          .attr("rx", 3)
          .attr("x", (d) => x(d.label) ?? 0)
          .attr("width", x.bandwidth())
          .attr("y", H).attr("height", 0),   // animate up from baseline
        (update) => update,
        (exit)   => exit.transition().duration(300)
          .attr("y", H).attr("height", 0).remove()
      )
      .attr("fill", (_, i) => color(data.length - 1 - i))
      .transition().duration(600).ease(d3.easeCubicOut)
        .attr("x", (d) => x(d.label) ?? 0)
        .attr("width", x.bandwidth())
        .attr("y", (d) => y(d.count))
        .attr("height", (d) => H - y(d.count));

    // Value labels
    g.selectAll<SVGTextElement, Stage>("text.bar-label")
      .data(data, (d) => d.label)
      .join(
        (enter) => enter.append("text").attr("class", "bar-label")
          .attr("text-anchor", "middle")
          .attr("font-size", FONT_SIZE).attr("fill", "#6B3A3A")
          .attr("x", (d) => (x(d.label) ?? 0) + x.bandwidth() / 2)
          .attr("y", H - 6).text("0"),
        (update) => update,
        (exit)   => exit.remove()
      )
      .transition().duration(600).ease(d3.easeCubicOut)
        .attr("x", (d) => (x(d.label) ?? 0) + x.bandwidth() / 2)
        .attr("y", (d) => y(d.count) - 6)
        .tween("text", function (d) {
          const prev = parseInt(this.textContent?.replace(/,/g, "") || "0", 10);
          const interp = d3.interpolateNumber(prev, d.count);
          return (t) => { this.textContent = Math.round(interp(t)).toLocaleString(); };
        });
  }

  // ── 4. On dropdown change — D3 only, zero React re-renders ───
  function handleSelect(e: React.ChangeEvent<HTMLSelectElement>) {
    const key = e.target.value;
    setSelected(key);   // only to keep <select> controlled
    updateChart(key);
  }

  if (error)   return <div className='error-handling'><p>{error}</p></div>;
  if (loading) return <div className='error-handling'><p>Loading…</p></div>;

  return (
    <div className='funnel-container'>
      <div className='filter-container'>
        <label htmlFor="policy-select">
          Policy Area:
        </label>
        <select
          id="policy-select"
          value={selected}
          onChange={handleSelect}
        >
          {keys.map((k) => <option key={k} value={k}>{k}</option>)}
        </select>
      </div>
      <div className="chart-container">
        <svg ref={svgRef} />
      </div>
    </div>
  );
}