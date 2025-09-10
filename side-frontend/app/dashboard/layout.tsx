import { SidebarLayout } from "@/shared/sidebar-layout";
import type { Metadata } from "next";
import { SideBarScada } from "../components/SideBarScadaComponent";

export const metadata: Metadata = {
  title: "S.I.D.E.",
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <>
      <SidebarLayout navbar={null} sidebar={<SideBarScada />}>
        {children}
      </SidebarLayout>
    </>
  );
}
