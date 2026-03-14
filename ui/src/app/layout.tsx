import type { Metadata } from "next";
import { Crimson_Pro, Space_Mono } from "next/font/google";
import "./globals.css";

const crimsonPro = Crimson_Pro({
  variable: "--font-crimson",
  subsets: ["latin"],
  weight: ["400", "600"],
});

const spaceMono = Space_Mono({
  variable: "--font-space-mono",
  subsets: ["latin"],
  weight: ["400", "700"],
});

export const metadata: Metadata = {
  title: "Country Intelligence",
  description: "Ask anything about any country in the world.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${crimsonPro.variable} ${spaceMono.variable}`}>
        {children}
      </body>
    </html>
  );
}
