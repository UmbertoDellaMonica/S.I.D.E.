import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import QueryProvider from "./provider/QueryProvider";
import { ToastContainer } from "react-toastify";
import { ThemeProvider } from "./lib/theme-change";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "S.I.D.E.",
  description:
    "S.I.D.E. (SCADA Intrusion Detection Engine) is an advanced IDS designed for industrial control systems. It identifies and monitors SCADA devices, detects network anomalies, and provides real-time alerts, enhancing security for critical infrastructure and ensuring operational integrity.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="it"
      className="bg-white dark:bg-gray-950 scheme-light dark:scheme-dark"
    >
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <ThemeProvider>
          <QueryProvider>
            {children}
            <ToastContainer position="top-center" theme="colored" />
          </QueryProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
