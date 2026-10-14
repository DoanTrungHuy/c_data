import React from "react";
import Link from "next/link";
import {
  BriefcaseIcon,
  EnvelopeIcon,
  MapPinIcon,
  HeartIcon,
} from "@heroicons/react/24/outline";
import CDataLogo from "@/components/CDataLogo";

export default function Footer() {
  const popularProvinces = [
    { name: "Hà Nội", href: "/jobs?province=Hà Nội" },
    { name: "Hồ Chí Minh", href: "/jobs?province=Hồ Chí Minh" },
    { name: "Đà Nẵng", href: "/jobs?province=Đà Nẵng" },
    { name: "Quảng Ninh (Hạ Long)", href: "/jobs?province=Quảng Ninh" },
    { name: "Hải Phòng", href: "/jobs?province=Hải Phòng" },
    { name: "Bình Dương", href: "/jobs?province=Bình Dương" },
    { name: "Đồng Nai", href: "/jobs?province=Đồng Nai" },
    { name: "Cần Thơ", href: "/jobs?province=Cần Thơ" },
  ];

  const popularCategories = [
    { name: "Công nghệ thông tin / IT", href: "/jobs?category=Công nghệ thông tin" },
    { name: "Kinh doanh / Bán hàng", href: "/jobs?category=Kinh doanh" },
    { name: "Marketing / Truyền thông", href: "/jobs?category=Marketing" },
    { name: "Kế toán / Kiểm toán", href: "/jobs?category=Kế toán" },
    { name: "Hành chính & Nhân sự", href: "/jobs?category=Nhân sự" },
    { name: "Du lịch & Khách sạn", href: "/jobs?category=Du lịch" },
    { name: "Kỹ thuật / Sản xuất", href: "/jobs?category=Kỹ thuật" },
  ];

  return (
    <footer className="border-t border-slate-200 bg-slate-900 text-slate-300">
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8 lg:py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 lg:gap-12">
          {/* Brand & Mission */}
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <CDataLogo size="md" showTagline={false} theme="dark" />
            </div>
            <p className="text-sm text-slate-400 leading-relaxed">
              VịnhViệc — Cổng thông tin việc làm và tuyển dụng thông minh hàng đầu TP. Hạ Long, Quảng Ninh. Khởi nghiệp vững vàng bên Vịnh Di sản.
            </p>
            <div className="pt-2 text-xs text-slate-400 space-y-1.5">
              <div className="flex items-center gap-2">
                <MapPinIcon className="h-4 w-4 text-accent-400 shrink-0" />
                <span>Khởi nguồn từ Hạ Long, Quảng Ninh, Việt Nam</span>
              </div>
              <div className="flex items-center gap-2">
                <EnvelopeIcon className="h-4 w-4 text-primary-400 shrink-0" />
                <span>contact@vinhviec.vn</span>
              </div>
            </div>
          </div>

          {/* Popular Provinces */}
          <div>
            <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">
              Việc làm theo khu vực
            </h3>
            <ul className="space-y-2.5 text-sm">
              {popularProvinces.map((prov) => (
                <li key={prov.name}>
                  <Link
                    href={prov.href}
                    className="text-slate-400 hover:text-white transition-colors duration-150 inline-block hover:translate-x-1 transition-transform"
                  >
                    Việc làm tại {prov.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Popular Categories */}
          <div>
            <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">
              Ngành nghề nổi bật
            </h3>
            <ul className="space-y-2.5 text-sm">
              {popularCategories.map((cat) => (
                <li key={cat.name}>
                  <Link
                    href={cat.href}
                    className="text-slate-400 hover:text-white transition-colors duration-150 inline-block hover:translate-x-1 transition-transform"
                  >
                    {cat.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* About & Quick Links */}
          <div>
            <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-4">
              Thông tin & Pháp lý
            </h3>
            <ul className="space-y-2.5 text-sm">
              <li>
                <Link
                  href="/about"
                  className="text-slate-400 hover:text-white transition-colors duration-150"
                >
                  Về dự án C_Data
                </Link>
              </li>
              <li>
                <Link
                  href="/about#how-it-works"
                  className="text-slate-400 hover:text-white transition-colors duration-150"
                >
                  Cơ chế tổng hợp tin tự động
                </Link>
              </li>
              <li>
                <Link
                  href="/jobs"
                  className="text-slate-400 hover:text-white transition-colors duration-150"
                >
                  Toàn bộ tin tuyển dụng
                </Link>
              </li>
              <li>
                <Link
                  href="/about#contact"
                  className="text-slate-400 hover:text-white transition-colors duration-150"
                >
                  Liên hệ & Hợp tác
                </Link>
              </li>
            </ul>

            <div className="mt-6 p-3.5 rounded-xl bg-slate-800/80 border border-slate-700/60">
              <span className="text-xs font-semibold text-accent-400 block mb-1">
                Dự án Nguồn Mở & Cộng Đồng
              </span>
              <p className="text-xs text-slate-400 leading-normal">
                Dữ liệu được thu thập tự động từ các trang việc làm uy tín nhằm hỗ trợ người lao động Việt Nam tiếp cận việc làm nhanh nhất.
              </p>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="mt-12 pt-8 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500">
          <p>© {new Date().getFullYear()} VịnhViệc. Nền tảng việc làm &amp; cơ hội nghề nghiệp Hạ Long.</p>
          <p className="flex items-center gap-1.5 text-slate-400">
            Phát triển với <HeartIcon className="h-4 w-4 text-red-500 inline fill-red-500" /> vì cộng đồng người tìm việc Việt Nam
          </p>
        </div>
      </div>
    </footer>
  );
}
