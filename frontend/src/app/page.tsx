import React from "react";
import Link from "next/link";
import {
  BriefcaseIcon,
  BuildingOffice2Icon,
  MapPinIcon,
  SparklesIcon,
  ArrowRightIcon,
  FireIcon,
  CheckBadgeIcon,
  GlobeAmericasIcon,
  CommandLineIcon,
  MegaphoneIcon,
  CalculatorIcon,
  UserGroupIcon,
  WrenchScrewdriverIcon,
  PhoneArrowUpRightIcon,
} from "@heroicons/react/24/outline";
import SearchBar from "@/components/SearchBar";
import JobCard from "@/components/JobCard";
import StatsCard from "@/components/StatsCard";
import HaLongITHub from "@/components/HaLongITHub";
import { getDashboardStats, getJobs } from "@/lib/api";

export const revalidate = 60; // Revalidate every minute (ISR/SSR)

export default async function HomePage() {
  // Fetch stats and latest jobs in parallel on the server
  const [stats, jobsResponse] = await Promise.all([
    getDashboardStats(),
    getJobs({ page_size: 8 }),
  ]);

  const featuredCategories = [
    {
      name: "Công nghệ thông tin / IT",
      desc: "Lập trình viên, QA, DevOps, AI",
      icon: <CommandLineIcon className="h-6 w-6 text-primary-600" />,
      href: "/jobs?category=Công nghệ thông tin",
      count: "3,200+ việc làm",
      bgClass: "bg-blue-50 text-blue-600",
    },
    {
      name: "Kinh doanh / Bán hàng",
      desc: "Sale B2B, B2C, Quản lý thị trường",
      icon: <BriefcaseIcon className="h-6 w-6 text-emerald-600" />,
      href: "/jobs?category=Kinh doanh",
      count: "2,800+ việc làm",
      bgClass: "bg-emerald-50 text-emerald-600",
    },
    {
      name: "Marketing & Truyền thông",
      desc: "SEO, Performance, Content, PR",
      icon: <MegaphoneIcon className="h-6 w-6 text-accent-600" />,
      href: "/jobs?category=Marketing",
      count: "1,750+ việc làm",
      bgClass: "bg-orange-50 text-orange-600",
    },
    {
      name: "Tài chính / Kế toán",
      desc: "Kế toán tổng hợp, Thuế, Kiểm toán",
      icon: <CalculatorIcon className="h-6 w-6 text-indigo-600" />,
      href: "/jobs?category=Kế toán",
      count: "1,420+ việc làm",
      bgClass: "bg-indigo-50 text-indigo-600",
    },
    {
      name: "Hành chính & Nhân sự",
      desc: "Tuyển dụng, C&B, Hành chính tổng hợp",
      icon: <UserGroupIcon className="h-6 w-6 text-rose-600" />,
      href: "/jobs?category=Nhân sự",
      count: "1,100+ việc làm",
      bgClass: "bg-rose-50 text-rose-600",
    },
    {
      name: "Kỹ thuật / Sản xuất",
      desc: "Cơ khí, Điện tử, Tự động hóa, Quản lý xưởng",
      icon: <WrenchScrewdriverIcon className="h-6 w-6 text-amber-600" />,
      href: "/jobs?category=Kỹ thuật",
      count: "960+ việc làm",
      bgClass: "bg-amber-50 text-amber-600",
    },
    {
      name: "Du lịch & Khách sạn",
      desc: "Điều hành tour, Lễ tân, F&B, Resort",
      icon: <GlobeAmericasIcon className="h-6 w-6 text-teal-600" />,
      href: "/jobs?category=Du lịch",
      count: "810+ việc làm",
      bgClass: "bg-teal-50 text-teal-600",
    },
    {
      name: "CSKH & Tư vấn",
      desc: "Chăm sóc khách hàng, Telesales",
      icon: <PhoneArrowUpRightIcon className="h-6 w-6 text-cyan-600" />,
      href: "/jobs?category=Chăm sóc khách hàng",
      count: "740+ việc làm",
      bgClass: "bg-cyan-50 text-cyan-600",
    },
  ];

  const popularProvinces = [
    {
      name: "Hà Nội",
      count: stats.jobs_by_province.find((p) => p.province === "Hà Nội")?.count || "4,800+",
      desc: "Trung tâm văn hóa, chính trị & công nghệ miền Bắc",
      tag: "Sôi động",
    },
    {
      name: "Hồ Chí Minh",
      count: stats.jobs_by_province.find((p) => p.province === "Hồ Chí Minh")?.count || "5,300+",
      desc: "Đầu tàu kinh tế, thương mại dịch vụ số 1 cả nước",
      tag: "Lương cao",
    },
    {
      name: "Đà Nẵng",
      count: stats.jobs_by_province.find((p) => p.province === "Đà Nẵng")?.count || "850+",
      desc: "Thành phố đáng sống với ngành IT & du lịch bùng nổ",
      tag: "Đáng sống",
    },
    {
      name: "Quảng Ninh",
      count: stats.jobs_by_province.find((p) => p.province === "Quảng Ninh")?.count || "490+",
      desc: "Hạ Long - Kỳ quan thế giới, du lịch, cảng biển & dịch vụ",
      tag: "Tiềm năng",
    },
    {
      name: "Hải Phòng",
      count: stats.jobs_by_province.find((p) => p.province === "Hải Phòng")?.count || "340+",
      desc: "Trung tâm công nghiệp, logistics & cảng biển quốc tế",
      tag: "Công nghiệp",
    },
    {
      name: "Bình Dương",
      count: stats.jobs_by_province.find((p) => p.province === "Bình Dương")?.count || "420+",
      desc: "Thủ phủ khu công nghiệp thông minh và chuỗi cung ứng",
      tag: "Khu CN",
    },
  ];

  return (
    <div className="flex flex-col space-y-16 lg:space-y-24 pb-20">
      {/* 1. HERO SECTION */}
      <section className="relative overflow-hidden pt-12 pb-16 md:pt-20 md:pb-24 bg-gradient-to-b from-blue-50/70 via-white to-slate-50 border-b border-slate-200/60">
        {/* Soft Background Glow Circles */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[350px] bg-gradient-to-tr from-blue-300/30 to-amber-200/20 blur-3xl rounded-full pointer-events-none" />

        <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white border border-blue-200 shadow-sm text-xs md:text-sm font-semibold text-primary-700 mb-6 animate-pulse">
            <SparklesIcon className="h-4 w-4 text-accent-500" />
            <span>Nền tảng tổng hợp việc làm đa nguồn #1 Việt Nam</span>
          </div>

          {/* Eye-catching Vietnamese Headline */}
          <h1 className="text-3xl sm:text-5xl lg:text-6xl font-black tracking-tight text-slate-900 leading-tight max-w-4xl mx-auto">
            Tìm việc làm phù hợp trên khắp{" "}
            <span className="bg-gradient-to-r from-primary-600 via-blue-600 to-accent-500 bg-clip-text text-transparent">
              Việt Nam
            </span>
          </h1>

          {/* Subtitle */}
          <p className="mt-4 sm:mt-6 text-base sm:text-xl text-slate-600 max-w-2xl mx-auto leading-relaxed">
            Tổng hợp hàng nghìn tin tuyển dụng từ mọi nguồn — hoàn toàn miễn phí & tra cứu mức lương minh bạch 63 tỉnh thành.
          </p>

          {/* Big Search Bar */}
          <div className="mt-8 sm:mt-12 max-w-4xl mx-auto">
            <SearchBar />
          </div>

          {/* Quick Trending Searches */}
          <div className="mt-6 flex flex-wrap items-center justify-center gap-2 text-xs sm:text-sm text-slate-500">
            <span className="font-semibold text-slate-700 flex items-center gap-1">
              <FireIcon className="h-4 w-4 text-accent-500" />
              Tìm kiếm phổ biến:
            </span>
            {[
              { label: "Frontend React", href: "/jobs?q=Frontend" },
              { label: "Quảng Ninh (Hạ Long)", href: "/jobs?province=Quảng Ninh" },
              { label: "Kế toán tổng hợp", href: "/jobs?q=Kế toán" },
              { label: "Nhân viên kinh doanh", href: "/jobs?q=Kinh doanh" },
              { label: "Làm việc từ xa", href: "/jobs?job_type=Làm việc từ xa" },
              { label: "Việc làm Hà Nội", href: "/jobs?province=Hà Nội" },
            ].map((trend) => (
              <Link
                key={trend.label}
                href={trend.href}
                className="px-3 py-1 rounded-full bg-white hover:bg-primary-50 hover:text-primary-600 border border-slate-200 text-slate-600 transition-colors shadow-2xs"
              >
                {trend.label}
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* 2. QUICK STATS SECTION */}
      <section className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 -mt-6 sm:-mt-10">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
          <StatsCard
            label="Tổng việc làm đang tuyển"
            value={stats.total_jobs}
            subtitle="Đang tuyển dụng"
            icon={<BriefcaseIcon className="h-7 w-7 text-primary-600" />}
            iconBgClass="bg-primary-50 text-primary-600"
          />
          <StatsCard
            label="Doanh nghiệp tuyển dụng"
            value={stats.total_companies}
            subtitle="Đã xác thực"
            icon={<BuildingOffice2Icon className="h-7 w-7 text-emerald-600" />}
            iconBgClass="bg-emerald-50 text-emerald-600"
          />
          <StatsCard
            label="Tỉnh thành có việc làm"
            value={`${stats.total_provinces_with_jobs} / 63`}
            subtitle="Bao phủ toàn quốc"
            icon={<MapPinIcon className="h-7 w-7 text-accent-600" />}
            iconBgClass="bg-accent-50 text-accent-600"
          />
          <StatsCard
            label="Việc làm mới hôm nay"
            value={`+${stats.new_jobs_today}`}
            subtitle="Cập nhật tự động"
            icon={<SparklesIcon className="h-7 w-7 text-purple-600" />}
            iconBgClass="bg-purple-50 text-purple-600"
          />
        </div>
      </section>

      {/* 2.5. HA LONG IT RADAR HUB */}
      <section className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <HaLongITHub />
      </section>

      {/* 3. FEATURED JOB CATEGORIES */}
      <section className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between mb-8 gap-4">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-primary-600">
              Danh mục việc làm
            </span>
            <h2 className="text-2xl sm:text-3xl font-black text-slate-900 mt-1">
              Khám phá theo ngành nghề hot nhất
            </h2>
          </div>
          <Link
            href="/jobs"
            className="inline-flex items-center gap-1.5 text-sm font-bold text-primary-600 hover:text-primary-700 hover:gap-2 transition-all"
          >
            <span>Tất cả ngành nghề</span>
            <ArrowRightIcon className="h-4 w-4" />
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
          {featuredCategories.map((cat) => (
            <Link
              key={cat.name}
              href={cat.href}
              className="group p-5 rounded-2xl border border-slate-200/90 bg-white hover:border-primary-400 hover:shadow-card transition-all duration-200 flex flex-col justify-between"
            >
              <div className="flex items-start gap-4">
                <div
                  className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-xl ${cat.bgClass} group-hover:scale-110 transition-transform`}
                >
                  {cat.icon}
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-900 group-hover:text-primary-600 transition-colors">
                    {cat.name}
                  </h3>
                  <p className="text-xs text-slate-500 mt-0.5 line-clamp-1">
                    {cat.desc}
                  </p>
                </div>
              </div>
              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs font-semibold text-slate-500 group-hover:text-primary-600">
                <span>{cat.count}</span>
                <span className="text-slate-400 group-hover:translate-x-1 transition-transform">
                  →
                </span>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* 4. LATEST JOBS SECTION */}
      <section className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between mb-8 gap-4">
          <div>
            <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 text-xs font-bold mb-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
              Mới cập nhật
            </div>
            <h2 className="text-2xl sm:text-3xl font-black text-slate-900">
              Việc làm mới đăng tuyển hôm nay
            </h2>
          </div>
          <Link
            href="/jobs"
            className="inline-flex items-center gap-2 rounded-xl bg-primary-600 px-4 py-2.5 text-sm font-bold text-white shadow-sm hover:bg-primary-700 transition-colors"
          >
            <span>Xem tất cả {stats.total_jobs.toLocaleString("vi-VN")} việc làm</span>
            <ArrowRightIcon className="h-4 w-4" />
          </Link>
        </div>

        {/* Job Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 sm:gap-6">
          {jobsResponse.items.slice(0, 8).map((job) => (
            <JobCard key={job.id} job={job} />
          ))}
        </div>
      </section>

      {/* 5. JOBS BY POPULAR PROVINCES */}
      <section className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-10">
          <span className="text-xs font-bold uppercase tracking-wider text-accent-600">
            Phân bố địa lý
          </span>
          <h2 className="text-2xl sm:text-3xl font-black text-slate-900 mt-1">
            Việc làm tại các tỉnh thành trọng điểm
          </h2>
          <p className="text-sm text-slate-600 mt-2">
            Tìm kiếm cơ hội nghề nghiệp tại nơi bạn sinh sống hoặc sẵn sàng định cư
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {popularProvinces.map((prov) => (
            <Link
              key={prov.name}
              href={`/jobs?province=${encodeURIComponent(prov.name)}`}
              className="group relative overflow-hidden rounded-2xl border border-slate-200/90 bg-white p-6 hover:border-primary-400 hover:shadow-card transition-all duration-200"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold px-2 py-0.5 rounded bg-blue-50 text-primary-700">
                  {prov.tag}
                </span>
                <span className="text-xs font-bold text-slate-500">
                  {typeof prov.count === "number"
                    ? `${prov.count.toLocaleString("vi-VN")} việc làm`
                    : `${prov.count} việc làm`}
                </span>
              </div>
              <h3 className="text-xl font-black text-slate-900 group-hover:text-primary-600 transition-colors">
                {prov.name}
              </h3>
              <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                {prov.desc}
              </p>
              <div className="mt-4 flex items-center text-xs font-bold text-primary-600 group-hover:gap-2 transition-all">
                <span>Khám phá ngay</span>
                <ArrowRightIcon className="h-3.5 w-3.5 ml-1" />
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* 6. WHY CHOOSE C_DATA BANNER */}
      <section className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="rounded-3xl bg-gradient-to-tr from-slate-900 via-primary-950 to-slate-900 p-8 sm:p-12 text-white shadow-xl relative overflow-hidden">
          <div className="relative z-10 max-w-3xl">
            <span className="inline-block text-xs font-bold tracking-widest text-accent-400 uppercase mb-3">
              Minh bạch • Toàn diện • Tự động hóa
            </span>
            <h2 className="text-2xl sm:text-4xl font-black tracking-tight leading-snug">
              Vì sao hàng vạn ứng viên tin dùng C_Data mỗi ngày?
            </h2>
            <div className="mt-8 grid grid-cols-1 sm:grid-cols-3 gap-6">
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-accent-400 font-bold text-base">
                  <CheckBadgeIcon className="h-5 w-5" />
                  <span>Dữ liệu tập trung</span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  Tổng hợp thông tin từ TopCV, VietnamWorks, CareerViet, ITviec, không bỏ sót bất kỳ cơ hội nào.
                </p>
              </div>

              <div className="space-y-2">
                <div className="flex items-center gap-2 text-accent-400 font-bold text-base">
                  <CheckBadgeIcon className="h-5 w-5" />
                  <span>Cập nhật liên tục</span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  Robot thu thập dữ liệu tự động theo chu kỳ mỗi giờ, loại bỏ tin hết hạn và tin trùng lặp.
                </p>
              </div>

              <div className="space-y-2">
                <div className="flex items-center gap-2 text-accent-400 font-bold text-base">
                  <CheckBadgeIcon className="h-5 w-5" />
                  <span>Phi lợi nhuận 100%</span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  Miễn phí hoàn toàn cho người lao động, chuyển hướng ứng tuyển trực tiếp đến nhà tuyển dụng.
                </p>
              </div>
            </div>

            <div className="mt-8">
              <Link
                href="/about"
                className="inline-flex items-center gap-2 rounded-xl bg-accent-500 px-5 py-3 text-sm font-bold text-white shadow-md hover:bg-accent-600 transition-colors"
              >
                <span>Tìm hiểu câu chuyện C_Data</span>
                <ArrowRightIcon className="h-4 w-4" />
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
