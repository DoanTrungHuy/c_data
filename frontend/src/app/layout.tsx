import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import "./globals.css";

const inter = Inter({
  subsets: ["latin", "vietnamese"],
  display: "swap",
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "C_Data - Nền tảng Tìm Việc Làm & Tổng Hợp Tin Tuyển Dụng Việt Nam",
  description:
    "C_Data - Nền tảng việc làm thông minh, tổng hợp hàng nghìn cơ hội việc làm mới mỗi ngày từ TopCV, VietnamWorks, ITviec, CareerViet trên khắp 63 tỉnh thành Việt Nam hoàn toàn miễn phí.",
  keywords: [
    "việc làm",
    "tìm việc làm",
    "tuyển dụng",
    "việc làm việt nam",
    "việc làm hạ long",
    "việc làm quảng ninh",
    "việc làm hà nội",
    "việc làm tphcm",
    "topcv",
    "vietnamworks",
    "c_data",
  ],
  authors: [{ name: "C_Data Team" }],
  viewport: "width=device-width, initial-scale=1",
  openGraph: {
    title: "C_Data - Nền tảng Tìm Việc Làm & Tổng Hợp Tuyển Dụng Việt Nam",
    description:
      "Tổng hợp việc làm từ mọi nguồn uy tín trên khắp 63 tỉnh thành Việt Nam. Tra cứu mức lương, ứng tuyển trực tiếp.",
    url: "https://cdata.vn",
    siteName: "C_Data",
    locale: "vi_VN",
    type: "website",
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
      <body className="min-h-screen flex flex-col font-sans bg-slate-50 text-slate-900 selection:bg-primary-500 selection:text-white">
        <Header />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
