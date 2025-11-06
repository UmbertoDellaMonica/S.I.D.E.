"use client";

import { useEffect, useRef } from "react";
import * as d3 from "d3";

interface Device {
  id: string;
  label?: string;
  x?: number;
  y?: number;
}

interface Link {
  source: string;
  target: string;
  relation: string;
  highlight?: boolean;
}

interface GraphViewProps {
  nodes: Device[];
  links: Link[];
}

export default function GraphView({ nodes, links }: GraphViewProps) {
  const svgRef = useRef<SVGSVGElement | null>(null);

  useEffect(() => {
    if (!svgRef.current) return;

    const width = svgRef.current.clientWidth;
    const height = svgRef.current.clientHeight;
    const svg = d3.select(svgRef.current);

    svg.selectAll("*").remove(); // reset SVG

    // LINK
    svg
      .selectAll("line")
      .data(links)
      .join("line")
      .attr("stroke-width", 2)
      .attr("stroke", (d) => (d.highlight ? "orange" : "#888"))
      .attr("x1", (d) => nodes.find((n) => n.id === d.source)?.x ?? 0)
      .attr("y1", (d) => nodes.find((n) => n.id === d.source)?.y ?? 0)
      .attr("x2", (d) => nodes.find((n) => n.id === d.target)?.x ?? 0)
      .attr("y2", (d) => nodes.find((n) => n.id === d.target)?.y ?? 0);

    // NODI
    svg
      .selectAll("circle")
      .data(nodes)
      .join("circle")
      .attr("r", 10)
      .attr("fill", "#1e3a8a")
      .attr("stroke", "#0f172a")
      .attr("stroke-width", 1.5)
      .attr("cx", (d) => d.x ?? 0)
      .attr("cy", (d) => d.y ?? 0);

    // LABEL
    svg
      .selectAll("text")
      .data(nodes)
      .join("text")
      .attr("x", (d) => d.x ?? 0)
      .attr("y", (d) => (d.y ?? 0) - 14)
      .attr("text-anchor", "middle")
      .attr("font-size", 10)
      .attr("fill", "#1e3a8a")
      .text((d) => d.label);
  }, [nodes, links]);

  return <svg ref={svgRef} width="100%" height="100%" />;
}
