import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import JobCompareTray from "@/components/JobCompareTray";
import "./globals.css";

const inter = Inter({
  subsets: ["latin", "vietnamese"],
  display: "swap",
  variable: "--font-inter",
});

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
};

const siteUrl = "https://doantrunghuy.github.io/c_data";
const isGh = process.env.GITHUB_PAGES === "true";
const basePath = isGh ? "/c_data" : "";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: "VịnhViệc - Việc Làm IT Hạ Long & Cơ Hội Nghề Nghiệp Vùng Vịnh",
  description:
    "VịnhViệc — Cổng việc làm và tuyển dụng thông minh hàng đầu TP. Hạ Long, Quảng Ninh. Cơ hội vàng bên Vịnh Di sản. Quét sâu thời gian thực, cam kết Zero-404, 100% tin đang tuyển dụng thực tế.",
  keywords: [
    "vịnhviệc",
    "vịnh việc",
    "vinhjob",
    "việc làm it hạ long",
    "việc làm cntt quảng ninh",
    "it support bãi cháy",
    "kỹ sư cntt cái lân",
    "lập trình viên hạ long",
    "việc làm hạ long",
    "việc làm quảng ninh",
    "tuyển dụng hạ long",
  ],
  authors: [{ name: "VịnhViệc Team" }],
  manifest: `${basePath}/manifest.json`,
  openGraph: {
    title: "VịnhViệc - Việc Làm Thông Minh TP. Hạ Long & Quảng Ninh",
    description:
      "Quét sâu thời gian thực, cam kết Zero-404, cập nhật liên tục mọi cơ hội việc làm tại TP. Hạ Long, Quảng Ninh.",
    url: siteUrl,
    siteName: "VịnhViệc",
    images: [
      {
        url: `${siteUrl}/og-image.png`,
        width: 1200,
        height: 630,
        alt: "VịnhViệc - Việc Làm Thông Minh Hạ Long & Quảng Ninh",
      },
    ],
    locale: "vi_VN",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "VịnhViệc - Việc Làm Thông Minh TP. Hạ Long & Quảng Ninh",
    description:
      "Quét sâu thời gian thực, cam kết Zero-404, cập nhật liên tục mọi cơ hội việc làm tại TP. Hạ Long, Quảng Ninh.",
    images: [`${siteUrl}/og-image.png`],
  },
  icons: {
    icon: [
      { url: `${basePath}/favicon.ico?v=20261016`, sizes: "any" },
      { url: `${basePath}/icon.svg?v=20261016`, type: "image/svg+xml" },
      { url: `${basePath}/icon-32.png?v=20261016`, type: "image/png", sizes: "32x32" },
      { url: `${basePath}/icon.png?v=20261016`, type: "image/png", sizes: "512x512" },
    ],
    shortcut: `${basePath}/favicon.ico?v=20261016`,
    apple: `${basePath}/apple-touch-icon.png?v=20261016`,
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="vi" className={inter.variable}>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0" />
        <link rel="icon" href={`${basePath}/favicon.ico?v=20261016`} sizes="any" />
        <link rel="icon" href={`${basePath}/icon.svg?v=20261016`} type="image/svg+xml" />
        <link rel="icon" href={`${basePath}/icon-32.png?v=20261016`} type="image/png" sizes="32x32" />
        <link rel="apple-touch-icon" href={`${basePath}/apple-touch-icon.png?v=20261016`} />
        <meta name="theme-color" content="#09090B" />
      </head>
      <body className="min-h-screen flex flex-col font-sans bg-white text-black selection:bg-black selection:text-white">
        <Header />
        <main className="flex-1">{children}</main>
        <Footer />
        <JobCompareTray />
      </body>
    </html>
  );
}
