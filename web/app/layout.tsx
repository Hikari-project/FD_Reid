import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Toaster } from "sonner";
import { CircleAlert, CircleCheck, CircleDashed, CircleX, Info } from "lucide-react";
const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "方度客流分析系统",
  description: "方度客流分析系统",
};

const TOAST_ICON = {
  success: <CircleCheck className="text-green-500 size-4" />,
  error: <CircleX className="text-red-500 size-4" />,
  loading: <CircleDashed className="text-yellow-500 size-4" />,
  info: <Info className="text-blue-500 size-4" />,
  warning: <CircleAlert className="text-orange-500 size-4" />,
}

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <Toaster position="top-center" icons={TOAST_ICON} />
        {children}
      </body>
    </html>
  );
}
