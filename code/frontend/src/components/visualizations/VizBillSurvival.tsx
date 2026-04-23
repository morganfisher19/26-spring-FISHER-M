import { useEffect, useRef, useState } from "react";
import * as d3 from "d3";
import "./VizAll.css";


const API_BASE = "http://localhost:5000";

interface Stage { label: string; count: number; }
type FunnelData = Record<string, Stage[]>;

const MARGIN = { top: 40, right: 40, bottom: 60, left: 80 };

export default function VizBillSurvival() {
  const svgRef    = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const allData   = useRef<FunnelData>({});       // cache — never triggers re-render
  const [keys, setKeys]       = useState<string[]>([]);
  const [selected, setSelected] = useState("All");
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState<string | null>(null);
  const [containerWidth, setContainerWidth] = useState(800);

  // ── ResizeObserver ────────────────────────────────────────────
  useEffect(() => {
    if (!containerRef.current) return;
    const observer = new ResizeObserver(([entry]) => {
      setContainerWidth(Math.min(entry.contentRect.width, 800));
    });
    observer.observe(containerRef.current);
    return () => observer.disconnect();
  }, [loading]);



  // ── 1. Fetch everything ONCE ──────────────────────────────────
  useEffect(() => {
    fetch(`${API_BASE}/api/visualizations/bill_funnel`)
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

    d3.select(svgRef.current).selectAll("*").remove();

    const W = containerWidth - MARGIN.left - MARGIN.right;
    const H = W * 5 / 8;

    const svg = d3.select(svgRef.current)
      .attr("width",  containerWidth)
      .attr("height", H + MARGIN.top  + MARGIN.bottom);

    const g = svg.append("g")
      .attr("class", "chart-root")
      .attr("transform", `translate(${MARGIN.left},${MARGIN.top})`);

    // Static axes groups (content filled on each update)
    g.append("g").attr("class", "x-axis").attr("transform", `translate(0,${H})`);
    g.append("g").attr("class", "y-axis");
    g.append("text")
      .attr("class", "y-label")
      .attr("transform", "rotate(-90)")
      .attr("x", -H / 2).attr("y", -65)
      .attr("text-anchor", "middle")
      .attr("font-size", "14px")
      .attr("font-weight", "bold")
      .attr("fill", "#6B3A3A")
      .text("Number of Bills");

    updateChart(selected, containerWidth);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [keys, containerWidth]);

  // ── 3. Pure D3 update (no React state touched) ────────────────
  function updateChart(key: string, width = containerWidth) {
    const data = allData.current[key];
    if (!data || !svgRef.current) return;

    const W = width - MARGIN.left - MARGIN.right;
    const H = W * 5 / 8;

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
    const fontSize = containerWidth < 500 ? "10px" : "14px";
    
    const xAxis = g.select<SVGGElement>(".x-axis");
    xAxis.transition().duration(400)
      .call(d3.axisBottom(x))
      .on("end", () => {
        xAxis.selectAll("text")
          .attr("dy", "1.2em")
          .style("font-size", fontSize)
          .style("fill", "#6B3A3A")
          .style("text-anchor","middle")
          .attr("transform", "rotate(0)");
        xAxis.selectAll("line, path").style("stroke", "#6B3A3A");

        if (width < 650) wrapAxisLabels(g, width);
       });

    g.select<SVGGElement>(".y-axis")
      .transition().duration(400)
      .call(d3.axisLeft(y).ticks(6).tickFormat(d3.format(",d")))
      .selectAll("text")
      .style("font-size", fontSize)
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
          .attr("font-size", "14px").attr("fill", "#6B3A3A")
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
    setSelected(key);
    updateChart(key);
  }

  // Resize axis labels
  function wrapAxisLabels(g: d3.Selection<SVGGElement, unknown, null, undefined>, width: number) {
    g.selectAll<SVGTextElement, unknown>(".x-axis text").each(function () {
      const el = d3.select(this);
      const words = (el.text() || "").split(" ");
      if (words.length < 2) return;

      el.text(null);

      words.forEach((word, i) => {
        el.append("tspan")
          .attr("x", 0)
          .attr("dy", i === 0 ? "0.5em" : "1.1em") // push first line down so both lines sit below the axis
          .text(word);
      });
    });
  }

  if (error)   return <div className='error-handling'><p>{error}</p></div>;
  if (loading) return <div className='error-handling'><p>Loading…</p></div>;

  return (
    <div className='funnel-container' ref={containerRef}>
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