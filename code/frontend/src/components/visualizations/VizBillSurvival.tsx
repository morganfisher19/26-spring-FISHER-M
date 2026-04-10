import { useEffect, useRef, useState } from "react";
import * as d3 from "d3";

const API_BASE = "http://localhost:5000";

interface Stage {
  label: string;
  count: number;
}

export default function VizBillSurvival() {
  const svgRef = useRef<SVGSVGElement>(null);
  const [data, setData] = useState<Stage[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API_BASE}/api/visualizations/bill_funnel`)
      .then((r) => r.json())
      .then((json) => {
        setData(json.stages);
        setLoading(false);
      })
      .catch(() => {
        setError("Failed to load data.");
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    if (!data.length || !svgRef.current) return;

    const margin = { top: 20, right: 20, bottom: 60, left: 70 };
    const width = 640 - margin.left - margin.right;
    const height = 400 - margin.top - margin.bottom;

    // Clear previous render
    d3.select(svgRef.current).selectAll("*").remove();

    const svg = d3
      .select(svgRef.current)
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", `translate(${margin.left},${margin.top})`);

    const x = d3
      .scaleBand()
      .domain(data.map((d) => d.label))
      .range([0, width])
      .padding(0.3);

    const y = d3
      .scaleLinear()
      .domain([0, d3.max(data, (d) => d.count) ?? 0])
      .nice()
      .range([height, 0]);

    // Color: fade from dark blue to light as count drops
    const colorScale = d3
      .scaleSequential()
      .domain([0, data.length - 1])
      .interpolator(d3.interpolateBlues);

    // Bars
    svg
      .selectAll("rect")
      .data(data)
      .join("rect")
      .attr("x", (d) => x(d.label) ?? 0)
      .attr("y", (d) => y(d.count))
      .attr("width", x.bandwidth())
      .attr("height", (d) => height - y(d.count))
      .attr("fill", (_, i) => colorScale(data.length - 1 - i))
      .attr("rx", 3);

    // Value labels on top of bars
    svg
      .selectAll(".bar-label")
      .data(data)
      .join("text")
      .attr("class", "bar-label")
      .attr("x", (d) => (x(d.label) ?? 0) + x.bandwidth() / 2)
      .attr("y", (d) => y(d.count) - 6)
      .attr("text-anchor", "middle")
      .attr("font-size", "12px")
      .attr("fill", "#333")
      .text((d) => d.count.toLocaleString());

    // X axis
    svg
      .append("g")
      .attr("transform", `translate(0,${height})`)
      .call(d3.axisBottom(x))
      .selectAll("text")
      .attr("dy", "1.2em")
      .style("font-size", "12px");

    // Y axis
    svg
      .append("g")
      .call(d3.axisLeft(y).ticks(6).tickFormat(d3.format(",d")));

    // Y axis label
    svg
      .append("text")
      .attr("transform", "rotate(-90)")
      .attr("x", -height / 2)
      .attr("y", -55)
      .attr("text-anchor", "middle")
      .attr("font-size", "12px")
      .attr("fill", "#555")
      .text("Number of Bills");
  }, [data]);

  if (loading) return <p>Loading...</p>;
  if (error) return <p style={{ color: "red" }}>{error}</p>;

  return (
    <div>
      <svg ref={svgRef} />
    </div>
  );
}