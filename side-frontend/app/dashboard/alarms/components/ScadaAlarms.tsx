"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import {
  AlertTriangle,
  Activity,
  Server,
  Clock,
  XCircle,
  ChevronDown,
  ChevronUp,
} from "lucide-react";

// Tipizzazione completa
interface DeviceInfo {
  ip: string;
  role: string;
  display_name: string;
}

interface Alert {
  id: string;
  timestamp: string;
  type: string;
  protocol?: string;
  details?: string | Record<string, any>;
  device?: DeviceInfo;
}

// Fetch alerts
async function fetchAlerts(): Promise<Alert[]> {
  const res = await fetch("http://localhost:5005/api/alerts");
  if (!res.ok) throw new Error("Errore durante il recupero degli alert");
  const data = await res.json();
  return data.alerts || [];
}

export default function AlertsPage() {
  const [typeFilter, setTypeFilter] = useState<string>("all");
  const [expandedRows, setExpandedRows] = useState<Record<string, boolean>>({});
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  const {
    data: alerts = [],
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery({
    queryKey: ["alerts"],
    queryFn: fetchAlerts,
    refetchInterval: 5000,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-zinc-950 text-zinc-400">
        <Activity className="animate-spin mr-2" size={24} />
        <span>Caricamento log in corso...</span>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex flex-col items-center justify-center h-screen bg-zinc-950 text-red-400">
        <XCircle size={40} className="mb-3" />
        <p className="text-lg font-semibold">Errore nel caricamento dei log</p>
        <p className="text-sm text-zinc-500 mt-2">
          {(error as Error).message || "Errore sconosciuto"}
        </p>
        <button
          onClick={() => refetch()}
          className="mt-4 bg-zinc-800 hover:bg-zinc-700 text-zinc-100 px-4 py-2 rounded-lg transition-colors"
        >
          Riprova
        </button>
      </div>
    );
  }

  // Filtraggio per tipo
  const filteredAlerts =
    typeFilter === "all" ? alerts : alerts.filter((a) => a.type === typeFilter);

  // Paginazione
  const totalPages = Math.ceil(filteredAlerts.length / itemsPerPage);
  const startIdx = (currentPage - 1) * itemsPerPage;
  const visibleAlerts = filteredAlerts.slice(startIdx, startIdx + itemsPerPage);

  // Colori per tipo evento
  const getColorByType = (type: string) => {
    switch (type) {
      case "CONFIRMED_ANOMALY_ML":
        return "text-red-400";
      case "EARLY_WARNING_ZSCORE":
        return "text-yellow-400";
      case "NORMAL_ACTIVITY":
        return "text-green-400";
      default:
        return "text-zinc-300";
    }
  };

  // Tipi statici per il filtro
  const eventTypes = [
    { value: "all", label: "Tutti" },
    { value: "NORMAL_ACTIVITY", label: "Normal Activity" },
    { value: "EARLY_WARNING_ZSCORE", label: "Early Warning" },
    { value: "CONFIRMED_ANOMALY_ML", label: "Anomalia Confermata" },
  ];

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 p-8">
      <header className="flex items-center justify-between mb-8 border-b border-zinc-800 pb-4">
        <div className="flex items-center space-x-3">
          <AlertTriangle className="text-amber-400" size={28} />
          <h1 className="text-3xl font-bold tracking-tight">
            Security Event Monitor
          </h1>
        </div>
        <span className="text-sm text-zinc-500">
          Ultimo aggiornamento: {new Date().toLocaleString("it-IT")}
        </span>
      </header>

      {/* Filtro per tipo */}
      <div className="mb-6 flex items-center space-x-3">
        <label className="text-sm text-zinc-400">Filtra per tipo:</label>
        <select
          title="Seleziona il Tipo di Evento"
          className="bg-zinc-900 border border-zinc-700 rounded-lg px-3 py-2 text-zinc-100"
          value={typeFilter}
          onChange={(e) => {
            setTypeFilter(e.target.value);
            setCurrentPage(1);
          }}
        >
          {eventTypes.map((t) => (
            <option key={t.value} value={t.value}>
              {t.label}
            </option>
          ))}
        </select>
      </div>

      {/* Lista eventi */}
      <div className="space-y-4">
        {visibleAlerts.length === 0 ? (
          <div className="text-center text-zinc-500 py-20 border border-zinc-800 rounded-2xl">
            Nessun evento registrato.
          </div>
        ) : (
          visibleAlerts.map((a) => {
            const isExpanded = expandedRows[a.id];
            const colorClass = getColorByType(a.type);

            let parsedDetails: any = {};
            try {
              parsedDetails =
                typeof a.details === "string"
                  ? JSON.parse(a.details)
                  : a.details || {};
            } catch {
              parsedDetails = { raw: a.details };
            }

            return (
              <div
                key={a.id}
                className="border border-zinc-800 bg-zinc-900/50 rounded-2xl shadow-md overflow-hidden"
              >
                <div
                  onClick={() =>
                    setExpandedRows((prev) => ({
                      ...prev,
                      [a.id]: !prev[a.id],
                    }))
                  }
                  className="flex justify-between items-center px-5 py-4 cursor-pointer hover:bg-zinc-900 transition-colors"
                >
                  <div>
                    <div className={`font-semibold ${colorClass}`}>
                      {a.type}
                    </div>
                    <div className="text-sm text-zinc-400 flex items-center space-x-2 mt-1">
                      <Clock size={14} className="text-zinc-500" />
                      <span>
                        {new Date(a.timestamp).toLocaleString("it-IT")}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="text-sm text-zinc-400 flex items-center space-x-2">
                      <Server size={14} className="text-zinc-500" />
                      <span>{a.device?.ip || "N/A"}</span>
                    </div>
                    {isExpanded ? (
                      <ChevronUp size={20} className="text-zinc-400" />
                    ) : (
                      <ChevronDown size={20} className="text-zinc-400" />
                    )}
                  </div>
                </div>

                {isExpanded && (
                  <div className="px-6 py-4 border-t border-zinc-800 bg-zinc-900">
                    <div className="grid grid-cols-2 gap-3 text-sm text-zinc-300 mb-3">
                      <p>
                        <span className="text-zinc-500">Device:</span>{" "}
                        {a.device?.display_name || a.device?.ip}
                      </p>
                      <p>
                        <span className="text-zinc-500">Ruolo:</span>{" "}
                        {a.device?.role || "Sconosciuto"}
                      </p>
                      <p>
                        <span className="text-zinc-500">Protocollo:</span>{" "}
                        {a.protocol || "-"}
                      </p>
                    </div>

                    <pre className="text-sm text-zinc-300 bg-zinc-950 rounded-lg p-3 overflow-auto max-h-64 whitespace-pre-wrap">
                      {JSON.stringify(parsedDetails, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>

      {/* Paginazione */}
      {filteredAlerts.length > 0 && (
        <div className="flex justify-between items-center mt-6">
          <button
            disabled={currentPage === 1}
            onClick={() => setCurrentPage((p) => p - 1)}
            className={`px-4 py-2 rounded-lg text-sm border ${
              currentPage === 1
                ? "text-zinc-600 border-zinc-700 cursor-not-allowed"
                : "text-zinc-200 border-zinc-600 hover:bg-zinc-800"
            }`}
          >
            ← Precedente
          </button>

          <span className="text-zinc-400 text-sm">
            Pagina {currentPage} di {totalPages}
          </span>

          <button
            disabled={currentPage === totalPages}
            onClick={() => setCurrentPage((p) => p + 1)}
            className={`px-4 py-2 rounded-lg text-sm border ${
              currentPage === totalPages
                ? "text-zinc-600 border-zinc-700 cursor-not-allowed"
                : "text-zinc-200 border-zinc-600 hover:bg-zinc-800"
            }`}
          >
            Successiva →
          </button>
        </div>
      )}
    </div>
  );
}
