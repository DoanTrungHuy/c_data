import type { Metadata } from "next";
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

export const viewport = {
  width: "device-width",
  initialScale: 1,
};

const isGh = process.env.GITHUB_PAGES === "true";
const basePath = isGh ? "/c_data" : "";

export const metadata: Metadata = {
  title: "C_Data - Việc Làm IT Hạ Long & Nền Tảng Tuyển Dụng Việt Nam",
  description:
    "C_Data - Nền tảng tuyển dụng thông minh, quét sâu và đối soát thời gian thực việc làm CNTT tại TP. Hạ Long, Quảng Ninh và 63 tỉnh thành Việt Nam. Cam kết Zero-404, 100% tin đang tuyển dụng thực tế.",
  keywords: [
    "việc làm it hạ long",
    "việc làm cntt quảng ninh",
    "it support bãi cháy",
    "kỹ sư cntt cái lân",
    "lập trình viên hạ long",
    "việc làm hạ long",
    "việc làm quảng ninh",
    "tìm việc làm",
    "tuyển dụng",
    "c_data",
  ],
  authors: [{ name: "C_Data Team" }],
  manifest: `${basePath}/manifest.json`,
  openGraph: {
    title: "C_Data - Việc Làm IT TP. Hạ Long & Toàn Quốc",
    description:
      "Quét sâu thời gian thực, đối soát Zero-404, cập nhật liên tục mọi cơ hội việc làm CNTT tại TP. Hạ Long, Quảng Ninh.",
    url: "https://doantrunghuy.github.io/c_data/",
    siteName: "C_Data",
    locale: "vi_VN",
    type: "website",
  },
  icons: {
    icon: [
      { url: `${basePath}/favicon.ico`, sizes: "any" },
      { url: `${basePath}/icon.png`, type: "image/png", sizes: "32x32" },
      { url: `${basePath}/favicon.svg`, type: "image/svg+xml" },
    ],
    shortcut: `${basePath}/favicon.ico`,
    apple: `${basePath}/apple-touch-icon.png`,
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
        <link rel="icon" href={`${basePath}/favicon.ico`} sizes="any" />
        <link rel="icon" href={`${basePath}/icon.png`} type="image/png" sizes="32x32" />
        <link rel="icon" href={`${basePath}/favicon.svg`} type="image/svg+xml" />
        <link rel="apple-touch-icon" href={`${basePath}/apple-touch-icon.png`} />
        <meta name="theme-color" content="#0B0F19" />
      </head>
      <body className="min-h-screen flex flex-col font-sans bg-slate-50 text-slate-900 selection:bg-primary-500 selection:text-white">
        <Header />
        <main className="flex-1">{children}</main>
        <Footer />
        <JobCompareTray />
      </body>
    </html>
  );
}
