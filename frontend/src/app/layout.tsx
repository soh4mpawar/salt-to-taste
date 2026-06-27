import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

import { Providers } from "@/components/Providers";
import { BottomNav } from "@/components/BottomNav";

export const metadata: Metadata = {
  title: "Salt to Taste",
  description: "AI-powered precise salt measurements for any recipe",
  manifest: "/manifest.json",
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "Salt to Taste",
  },
};

export const viewport: Viewport = {
  themeColor: "#ff9500",
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
      suppressHydrationWarning
    >
      <body className="min-h-full flex flex-col bg-salt-50 pb-20" suppressHydrationWarning>
        <Providers>
          <main className="max-w-md w-full mx-auto min-h-screen bg-white shadow-xl relative">
            {children}
          </main>
        </Providers>
        <BottomNav />
      </body>
    </html>
  );
}
