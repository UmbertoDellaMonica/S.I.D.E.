"use client";

import { useEffect, useRef } from "react";
import * as d3 from "d3";
import { useDevices } from "./services/side.device.service";

export default function Home() {
  const svgRef = useRef<SVGSVGElement | null>(null);

  // 🔹 Uso TanStack Query (fetch una volta)
  const { data: graph, refetch } = useDevices({ staleTime: Infinity });

  // 🔹 Disegno grafo con D3
  useEffect(() => {
    if (!graph || !svgRef.current) return;

    const width = 1000;
    const height = 1000;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove(); // reset

    const simulation = d3
      .forceSimulation(graph.nodes)
      .force(
        "link",
        d3
          .forceLink(graph.links)
          .id((d: any) => d.id)
          .distance(180)
      )
      .force("charge", d3.forceManyBody().strength(-500))
      .force("center", d3.forceCenter(width / 2, height / 2));

    const defs = svg.append("defs");

    // Glow filter
    defs
      .append("filter")
      .attr("id", "glow")
      .append("feGaussianBlur")
      .attr("stdDeviation", "3.5")
      .attr("result", "coloredBlur");

    // Gradiente per i nodi
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

    // Links
    const link = svg
      .append("g")
      .attr("stroke", "rgba(30,58,138,0.6)")
      .attr("stroke-width", 2)
      .selectAll("line")
      .data(graph.links)
      .join("line");

    // Nodes
    const node = svg
      .append("g")
      .selectAll("circle")
      .data(graph.nodes)
      .join("circle")
      .attr("r", 22)
      .attr("fill", "url(#node-gradient)")
      .attr("stroke", "#1e3a8a")
      .attr("stroke-width", 2)
      .style("cursor", "pointer")
      .on("mouseover", function () {
        d3.select(this).transition().duration(200).attr("r", 30);
      })
      .on("mouseout", function () {
        d3.select(this).transition().duration(200).attr("r", 22);
      })
      .call(
        d3
          .drag<SVGCircleElement, any>()
          .on("start", (event, d) => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
          })
          .on("drag", (event, d) => {
            d.fx = event.x;
            d.fy = event.y;
          })
          .on("end", (event, d) => {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
          })
      );

    // Labels
    const labels = svg
      .append("g")
      .selectAll("text")
      .data(graph.nodes)
      .join("text")
      .text((d) => d.label || d.ip || d.id)
      .attr("font-size", 14)
      .attr("dy", -30)
      .attr("text-anchor", "middle")
      .attr("fill", "#1e3a8a")
      .style("font-weight", "600");

    simulation.on("tick", () => {
      link
        .attr("x1", (d: any) => d.source.x)
        .attr("y1", (d: any) => d.source.y)
        .attr("x2", (d: any) => d.target.x)
        .attr("y2", (d: any) => d.target.y);

      node.attr("cx", (d: any) => d.x).attr("cy", (d: any) => d.y);

      labels.attr("x", (d: any) => d.x).attr("y", (d: any) => d.y);
    });
  }, [graph]);

  return (
    <div className="flex flex-col h-screen w-screen bg-white p-6">
      {/* Titolo */}
      <h1 className="text-6xl md:text-6xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-500 to-cyan-400 drop-shadow-lg">
        SCADA Analyzer Topology
      </h1>

      {/* Bottone ricarica */}
      <div className="mt-4">
        <button
          onClick={() => refetch()}
          className="relative px-6 py-2 rounded-lg bg-gradient-to-r from-cyan-400 to-blue-500 text-white font-bold shadow-lg hover:scale-105 transition-transform"
        >
          Ricarica Grafo
          <span className="absolute -top-8 left-1/2 -translate-x-1/2 text-sm bg-black text-white rounded px-2 py-1 opacity-0 group-hover:opacity-100 transition-opacity">
            Ricarica il grafico per eventuali aggiornamenti
          </span>
        </button>
      </div>

      {/* Grafo */}
      <div className="flex-grow w-full h-full flex justify-center items-center mt-10">
        <svg ref={svgRef} width="100%" height="100%"></svg>
      </div>
    </div>
  );
}
