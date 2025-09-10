import GraphContainer from "../components/GraphContainer";

export default function DashboardOverview() {
  return (
    <div className="flex flex-col w-full h-screen p-4 bg-gray-50">
      {/* Titolo fuori dal GraphContainer */}
      <h1 className="text-3xl font-bold text-left text-blue-700 mb-4">
        SCADA Analyzer
      </h1>
      {/* Container principale del grafo */}
      <div className="relative flex-1 w-full h-full">
        {/* GraphContainer */}
        <GraphContainer className="w-full h-full" />
      </div>
    </div>
  );
}
