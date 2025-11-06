"use client";

import { useEffect, useRef, useState } from "react";
import { DraggableButton } from "./RefetchButton";
import GraphView from "./GraphView";

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

export default function GraphContainer({
  className = "",
  wsUrl = "ws://localhost:5005/ws/network",
}) {
  const [nodes, setNodes] = useState<Device[]>([]);
  const [tempLinks, setTempLinks] = useState<Link[]>([]);
  const containerRef = useRef<HTMLDivElement>(null);

  const width = 800;
  const height = 600;
  const minDist = 50; // distanza minima tra nodi

  // funzione per generare posizione libera
  const generatePosition = (existingNodes: Device[]) => {
    let x, y, valid;
    do {
      x = Math.random() * (width - minDist * 2) + minDist;
      y = Math.random() * (height - minDist * 2) + minDist;
      valid = existingNodes.every(
        (n) => Math.hypot((n.x ?? 0) - x, (n.y ?? 0) - y) >= minDist
      );
    } while (!valid);
    return { x, y };
  };

  // Aggiorna le posizioni dei nodi esistenti
  const refreshNodes = () => {
    setNodes((prev) =>
      prev.map((n) => {
        // rigenera posizione casuale evitando sovrapposizioni
        const newPos = generatePosition(prev.filter((x) => x.id !== n.id));
        return { ...n, ...newPos };
      })
    );
  };

  useEffect(() => {
    const ws = new WebSocket(wsUrl);

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data) as { type: string; event: any };
      const { src_ip, src_port, dst_ip, dst_port } = msg.event;

      const srcId = `${src_ip}:${src_port}`;
      const dstId = `${dst_ip}:${dst_port}`;

      setNodes((prev) => {
        const newNodes = [...prev];

        if (!newNodes.find((n) => n.id === srcId)) {
          const pos = generatePosition(newNodes);
          newNodes.push({ id: srcId, label: srcId, ...pos });
        }
        if (!newNodes.find((n) => n.id === dstId)) {
          const pos = generatePosition(newNodes);
          newNodes.push({ id: dstId, label: dstId, ...pos });
        }

        return newNodes;
      });

      // link lampeggiante
      const link: Link = {
        source: srcId,
        target: dstId,
        relation: msg.type,
        highlight: true,
      };
      setTempLinks([link]);

      setTimeout(() => setTempLinks([]), 500);
    };

    return () => ws.close();
  }, [wsUrl]);

  return (
    <div
      ref={containerRef}
      className={`relative flex flex-col w-full h-full bg-white p-2 rounded-lg shadow ${className}`}
    >
      <DraggableButton containerRef={containerRef} onClick={refreshNodes}>
        Aggiorna Grafo
      </DraggableButton>
      <div className="flex-1 w-full h-full overflow-auto">
        <GraphView nodes={nodes} links={tempLinks} />
      </div>
    </div>
  );
}
