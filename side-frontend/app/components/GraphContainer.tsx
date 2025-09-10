"use client";

import { useRef } from "react";
import { DraggableButton } from "../dashboard/components/RefetchButton";
import { useDevices } from "../services/side.device.service";
import GraphView from "./GraphView";

interface GraphContainerProps {
  className?: string;
}

export default function GraphContainer({
  className = "",
}: GraphContainerProps) {
  const { data: graph, refetch, isLoading, isError } = useDevices();
  const containerRef = useRef<HTMLDivElement>(
    null
  ) as React.RefObject<HTMLDivElement>;

  if (isLoading)
    return <p className="text-sm text-gray-500">Caricamento grafico...</p>;
  if (isError)
    return <p className="text-sm text-red-500">Errore nel caricamento</p>;
  if (!graph)
    return <p className="text-sm text-gray-400">Nessun dato disponibile</p>;

  return (
    <div
      ref={containerRef}
      className={`relative flex flex-col w-full h-full bg-white p-2 rounded-lg shadow ${className}`}
    >
      <DraggableButton containerRef={containerRef} onClick={() => refetch()}>
        Ricarica Grafo
      </DraggableButton>

      <div className="flex-1 w-full h-full overflow-auto">
        <GraphView graph={graph} />
      </div>
    </div>
  );
}
