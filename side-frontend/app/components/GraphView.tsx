"use client";
import { useEffect, useRef } from "react";
import * as d3 from "d3";

export default function GraphView({ graph }: { graph: any }) {
  const svgRef = useRef<SVGSVGElement | null>(null);

  useEffect(() => {
    if (!graph || !svgRef.current) return;

    const width = svgRef.current.clientWidth;
    const height = svgRef.current.clientHeight;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const simulation = d3
      .forceSimulation(graph.nodes)
      .force(
        "link",
        d3
          .forceLink(graph.links)
          .id((d: any) => d.id)
          .distance(100)
      )
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2));

    const defs = svg.append("defs");
    defs
      .append("filter")
      .attr("id", "glow")
      .append("feGaussianBlur")
      .attr("stdDeviation", "3.5")
      .attr("result", "coloredBlur");

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

    const link = svg
      .append("g")
      .attr("stroke", "rgba(30,58,138,0.5)")
      .attr("stroke-width", 1.5)
      .selectAll("line")
      .data(graph.links)
      .join("line");

    const node = svg
      .append("g")
      .selectAll("circle")
      .data(graph.nodes)
      .join("circle")
      .attr("r", 12)
      .attr("fill", "url(#node-gradient)")
      .attr("stroke", "#1e3a8a")
      .attr("stroke-width", 1.5)
      .style("cursor", "pointer")
      .on("mouseover", (event, d) =>
        d3.select(event.currentTarget).transition().duration(200).attr("r", 18)
      )
      .on("mouseout", (event, d) =>
        d3.select(event.currentTarget).transition().duration(200).attr("r", 12)
      )
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

    const labels = svg
      .append("g")
      .selectAll("text")
      .data(graph.nodes)
      .join("text")
      .text((d) => d.label || d.ip || d.id)
      .attr("font-size", 10)
      .attr("dy", -15)
      .attr("text-anchor", "middle")
      .attr("fill", "#1e3a8a");

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

  return <svg ref={svgRef} width="100%" height="100%"></svg>;
}
