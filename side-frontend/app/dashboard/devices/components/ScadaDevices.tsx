"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { useQuery } from "@tanstack/react-query";

type Device = {
  id: string;
  ip: string;
  port: number;
  protocol: string;
  status: "active" | "inactive";
  role?: "client" | "slave";
};

// 🔹 Servizio per il fetch
async function fetchDevices(protocol: string): Promise<Device[]> {
  const res = await fetch(
    `http://localhost:5005/api/devices/filter?protocol=${protocol}`
  );
  if (!res.ok) throw new Error("Errore nel recupero dei dispositivi");
  const data = await res.json();
  return data.devices.map((d: Device) => ({
    ...d,
    role: d.port === 502 ? "slave" : "client", // euristica per il ruolo
  }));
}

export default function ScadaDevicesPage() {
  const [protocol, setProtocol] = useState("Modbus");

  // 🔹 TanStack Query gestisce loading/error/caching
  const {
    data: devices = [],
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery({
    queryKey: ["devices", protocol],
    queryFn: () => fetchDevices(protocol),
    refetchInterval: 5000, // ogni 5s aggiorna automaticamente
  });

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-screen bg-gray-900 text-gray-200">
        <p className="text-lg animate-pulse">Loading SCADA devices...</p>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="flex justify-center items-center h-screen bg-gray-900 text-red-400">
        <p className="text-lg">Errore: {(error as Error).message}</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 p-8">
      <div className="max-w-7xl mx-auto">
        {/* HEADER */}
        <div className="flex justify-between items-center mb-10">
          <h1 className="text-4xl font-extrabold tracking-tight text-blue-400 drop-shadow-md">
            🛰️ SCADA Network Dashboard
          </h1>
          <div className="flex items-center space-x-4">
            <label className="font-semibold text-gray-300">
              Filter Protocol:
            </label>
            <select
              title="Seleziona il Protocollo"
              value={protocol}
              onChange={(e) => {
                setProtocol(e.target.value);
                refetch(); // 🔹 forza refetch al cambio protocollo
              }}
              className="bg-gray-800 text-gray-200 border border-gray-700 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 outline-none"
            >
              <option value="Modbus">Modbus</option>
              <option value="OPC-UA">OPC-UA</option>
              <option value="S7">S7</option>
            </select>
          </div>
        </div>

        {/* INFO BAR */}
        <div className="mb-6 text-gray-400 italic">
          Showing devices for protocol{" "}
          <strong className="text-blue-400">{protocol}</strong> —{" "}
          {devices.length > 0 ? (
            <span>{devices.length} devices detected</span>
          ) : (
            <span>No active devices found</span>
          )}
        </div>

        {/* GRID */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {devices.map((device) => (
            <motion.div
              key={device.id}
              whileHover={{ scale: 1.05 }}
              className="bg-gray-900 border border-gray-700 rounded-2xl shadow-lg p-5 transition-all duration-200"
            >
              <div className="flex justify-between items-center mb-3">
                <span
                  className={`text-sm font-bold px-3 py-1 rounded-full ${
                    device.status === "active"
                      ? "bg-green-600/70 text-white"
                      : "bg-red-600/70 text-white"
                  }`}
                >
                  {device.status.toUpperCase()}
                </span>
                <span
                  className={`text-xs font-semibold px-3 py-1 rounded-full ${
                    device.role === "slave"
                      ? "bg-purple-600/70 text-white"
                      : "bg-cyan-600/70 text-white"
                  }`}
                >
                  {device.role?.toUpperCase() ?? "UNKNOWN"}
                </span>
              </div>

              <div className="text-xl font-semibold text-blue-300">
                {device.ip}:{device.port}
              </div>

              <div className="mt-2 text-gray-400">
                Protocol: <span className="font-mono">{device.protocol}</span>
              </div>

              <div className="mt-4 h-2 w-full bg-gray-700 rounded-full overflow-hidden">
                <div
                  className={`h-full ${
                    device.status === "active" ? "bg-green-500" : "bg-red-500"
                  } transition-all`}
                  style={{
                    width: device.status === "active" ? "100%" : "40%",
                  }}
                ></div>
              </div>
            </motion.div>
          ))}
        </div>

        {devices.length === 0 && (
          <div className="mt-10 text-center text-gray-400">
            <p>
              No devices found for protocol{" "}
              <strong className="text-blue-400">{protocol}</strong>.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
