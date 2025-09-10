import { useQuery } from "@tanstack/react-query";

export type Device = {
  id: string;
  label?: string;
  role?: string;
  ip?: string;
  port?: number;
  first_seen?: string;
  last_seen?: string;
};

export type Link = {
  source: string;
  target: string;
  relation: string;
};

export type GraphResponse = {
  nodes: Device[];
  links: Link[];
};

async function fetchDevices(): Promise<GraphResponse> {
  const res = await fetch("http://localhost:5005/api/devices");
  if (!res.ok) throw new Error("Errore nel recupero dei device");
  return res.json();
}

export function useDevices() {
  return useQuery<GraphResponse>({
    queryKey: ["devices"],
    queryFn: fetchDevices,
  });
}
