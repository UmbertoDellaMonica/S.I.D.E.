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

    // Gradient per i nodi
    const defs = svg.append("defs");
    const gradient = defs
      .append("radialGradient")
      .attr("id", "node-gradient")
      .attr("fx", "50%")
      .attr("fy", "50%")
      .attr("r", "50%");
    gradient.append("stop").attr("offset", "0%").attr("stop-color", "#00bfff");
    gradient
      .append("stop")
      .attr("offset", "100%")
      .attr("stop-color", "#1e3a8a");

    // LINEE (LINK)
    const linkSel = svg
      .selectAll("line")
      .data(links)
      .join("line")
      .attr("stroke-width", 2)
      .attr("stroke", (d) => (d.highlight ? "orange" : "rgba(30,58,138,0.5)"));

    // NODI
    const nodeSel = svg
      .selectAll("circle")
      .data(nodes)
      .join("circle")
      .attr("r", 12)
      .attr("fill", "url(#node-gradient)")
      .attr("stroke", "#0f172a")
      .attr("stroke-width", 1.5)
      .attr("cx", (d) => d.x ?? 0)
      .attr("cy", (d) => d.y ?? 0)
      .call(
        d3
          .drag<SVGCircleElement, Device>()
          .on("start", function (event, d) {
            d3.select(this).raise();
          })
          .on("drag", function (event, d) {
            const x = event.x;
            const y = event.y;

            // Aggiorna nodo in tempo reale
            d3.select(this).attr("cx", x).attr("cy", y);

            // Aggiorna linee collegate in tempo reale
            linkSel
              .filter((l: any) => l.source === d.id || l.target === d.id)
              .attr("x1", (l: any) =>
                l.source === d.id ? x : nodes.find((n) => n.id === l.source)?.x
              )
              .attr("y1", (l: any) =>
                l.source === d.id ? y : nodes.find((n) => n.id === l.source)?.y
              )
              .attr("x2", (l: any) =>
                l.target === d.id ? x : nodes.find((n) => n.id === l.target)?.x
              )
              .attr("y2", (l: any) =>
                l.target === d.id ? y : nodes.find((n) => n.id === l.target)?.y
              );
          })
          .on("end", function (event, d) {
            // Salva posizione finale
            d.x = event.x;
            d.y = event.y;
          })
      );

    // LABELS
    svg
      .selectAll("text")
      .data(nodes)
      .join("text")
      .attr("font-size", 10)
      .attr("dy", -18)
      .attr("text-anchor", "middle")
      .attr("fill", "#1e3a8a")
      .attr("x", (d) => d.x ?? 0)
      .attr("y", (d) => d.y ?? 0)
      .text((d) => d.label);

    // Aggiorna link temporanei (per lampeggio)
    linkSel
      .attr("x1", (d) => nodes.find((n) => n.id === d.source)?.x ?? 0)
      .attr("y1", (d) => nodes.find((n) => n.id === d.source)?.y ?? 0)
      .attr("x2", (d) => nodes.find((n) => n.id === d.target)?.x ?? 0)
      .attr("y2", (d) => nodes.find((n) => n.id === d.target)?.y ?? 0);
  }, [nodes, links]);

  return <svg ref={svgRef} width="100%" height="100%"></svg>;
}
