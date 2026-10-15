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
      desc: "Lập trình viên, QA, DevOps, Helpdesk, AI",
      icon: <CommandLineIcon className="h-6 w-6 text-black" />,
      href: "/jobs?category=Công nghệ thông tin",
      count: "53 việc làm",
    },
    {
      name: "Du lịch & Khách sạn",
      desc: "Điều hành tour, Lễ tân, F&B, Resort 5*",
      icon: <GlobeAmericasIcon className="h-6 w-6 text-black" />,
      href: "/jobs?category=Du lịch",
      count: "8 việc làm",
    },
    {
      name: "Kinh doanh / Bán hàng",
      desc: "Sale B2B, B2C, Quản lý thị trường",
      icon: <BriefcaseIcon className="h-6 w-6 text-black" />,
      href: "/jobs?category=Kinh doanh",
      count: "6 việc làm",
    },
    {
      name: "Tài chính / Kế toán",
      desc: "Kế toán tổng hợp, Thuế, Ngân hàng",
      icon: <CalculatorIcon className="h-6 w-6 text-black" />,
      href: "/jobs?category=Kế toán",
      count: "5 việc làm",
    },
    {
      name: "Kỹ thuật / Than - Cơ điện",
      desc: "Cơ khí, Tự động hóa SCADA, Khai mỏ",
      icon: <WrenchScrewdriverIcon className="h-6 w-6 text-black" />,
      href: "/jobs?category=Kỹ thuật",
      count: "5 việc làm",
    },
    {
      name: "Hành chính & Nhân sự",
      desc: "Tuyển dụng, C&B, Hành chính tổng hợp",
      icon: <UserGroupIcon className="h-6 w-6 text-black" />,
      href: "/jobs?category=Nhân sự",
      count: "4 việc làm",
    },
    {
      name: "Nhà hàng & F&B",
      desc: "Bếp, Phụ bếp, Quản lý nhà hàng",
      icon: <MegaphoneIcon className="h-6 w-6 text-black" />,
      href: "/jobs?category=Nhà hàng",
      count: "4 việc làm",
    },
    {
      name: "CSKH & Tư vấn",
      desc: "Chăm sóc khách hàng, Lễ tân tour",
      icon: <PhoneArrowUpRightIcon className="h-6 w-6 text-black" />,
      href: "/jobs?category=Chăm sóc khách hàng",
      count: "3 việc làm",
    },
  ];

  const popularProvinces: Array<{
    name: string;
    count: number | string;
    desc: string;
    tag: string;
  }> = [
    {
      name: "Quảng Ninh",
      count: stats.jobs_by_province.find((p) => p.province === "Quảng Ninh")?.count ?? 75,
      desc: "Hạ Long, Cẩm Phả - Du lịch, CNTT, Cảng biển & Khai thác Than",
      tag: "Trọng điểm",
    },
    {
      name: "Hà Nội",
      count: stats.jobs_by_province.find((p) => p.province === "Hà Nội")?.count ?? 5,
      desc: "Trung tâm văn hóa, chính trị & công nghệ miền Bắc",
      tag: "Công nghệ",
    },
    {
      name: "Bình Dương",
      count: stats.jobs_by_province.find((p) => p.province === "Bình Dương")?.count ?? 3,
      desc: "Thủ phủ khu công nghiệp thông minh và chuỗi cung ứng",
      tag: "Khu CN",
    },
    {
      name: "Hồ Chí Minh",
      count: stats.jobs_by_province.find((p) => p.province === "Hồ Chí Minh")?.count ?? 2,
      desc: "Đầu tàu kinh tế, thương mại dịch vụ lớn",
      tag: "Sôi động",
    },
    {
      name: "Đà Nẵng",
      count: stats.jobs_by_province.find((p) => p.province === "Đà Nẵng")?.count ?? 2,
      desc: "Thành phố đáng sống với ngành IT & du lịch",
      tag: "Đáng sống",
    },
    {
      name: "Hải Phòng",
      count: stats.jobs_by_province.find((p) => p.province === "Hải Phòng")?.count ?? 2,
      desc: "Trung tâm công nghiệp, logistics & cảng biển quốc tế",
      tag: "Logistics",
    },
  ];

  return (
    <div className="flex flex-col space-y-16 lg:space-y-24 pb-20">
      {/* 1. HERO SECTION */}
      <section className="relative overflow-hidden pt-12 pb-16 md:pt-20 md:pb-24 bg-white border-b border-neutral-200">
        <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 text-center">
          {/* Subtle Category Badge */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-neutral-100 border border-neutral-300 text-xs sm:text-sm font-semibold text-neutral-900 mb-6">
            <SparklesIcon className="h-4 w-4 text-black" />
            <span>Nền tảng việc làm thông minh VịnhViệc</span>
          </div>

          {/* Clean, Impactful Headline */}
          <h1 className="text-3xl sm:text-5xl lg:text-6xl font-black tracking-tight text-black leading-tight max-w-3xl mx-auto">
            Tìm việc làm chất lượng tại{" "}
            <span className="underline decoration-neutral-300 underline-offset-8">
              Hạ Long &amp; Toàn quốc
            </span>
          </h1>

          {/* Subtitle */}
          <p className="mt-4 sm:mt-5 text-sm sm:text-lg text-neutral-600 max-w-2xl mx-auto leading-relaxed">
            Tổng hợp và xác minh tin tuyển dụng đa nguồn thời gian thực. Cam kết 100% dữ liệu chuẩn xác, không tin ảo.
          </p>

          {/* Sleek Search Bar */}
          <div className="mt-8 sm:mt-10 max-w-3xl mx-auto">
            <SearchBar />
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
            icon={<BriefcaseIcon className="h-7 w-7 text-black" />}
            iconBgClass="bg-neutral-100 text-black"
          />
          <StatsCard
            label="Doanh nghiệp tuyển dụng"
            value={stats.total_companies}
            subtitle="Đã xác thực"
            icon={<BuildingOffice2Icon className="h-7 w-7 text-black" />}
            iconBgClass="bg-neutral-100 text-black"
          />
          <StatsCard
            label="Tỉnh thành có việc làm"
            value={`${stats.total_provinces_with_jobs} / 63`}
            subtitle="Bao phủ toàn quốc"
            icon={<MapPinIcon className="h-7 w-7 text-black" />}
            iconBgClass="bg-neutral-100 text-black"
          />
          <StatsCard
            label="Việc làm mới hôm nay"
            value={`+${stats.new_jobs_today}`}
            subtitle="Cập nhật tự động"
            icon={<SparklesIcon className="h-7 w-7 text-black" />}
            iconBgClass="bg-neutral-100 text-black"
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
            <span className="text-xs font-bold uppercase tracking-wider text-neutral-500">
              Danh mục việc làm
            </span>
            <h2 className="text-2xl sm:text-3xl font-black text-black mt-1">
              Khám phá theo ngành nghề hot nhất
            </h2>
          </div>
          <Link
            href="/jobs"
            className="inline-flex items-center gap-1.5 text-sm font-bold text-black hover:underline transition-all"
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
              className="group p-5 rounded-2xl border border-neutral-200 bg-white hover:border-black hover:shadow-md transition-all duration-200 flex flex-col justify-between"
            >
              <div className="flex items-start gap-4">
                <div
                  className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-neutral-100 text-black border border-neutral-200 group-hover:scale-105 transition-transform"
                >
                  {cat.icon}
                </div>
                <div>
                  <h3 className="text-sm font-bold text-black group-hover:underline transition-colors">
                    {cat.name}
                  </h3>
                  <p className="text-xs text-neutral-500 mt-0.5 line-clamp-1">
                    {cat.desc}
                  </p>
                </div>
              </div>
              <div className="mt-4 pt-3 border-t border-neutral-100 flex items-center justify-between text-xs font-semibold text-neutral-500 group-hover:text-black">
                <span>{cat.count}</span>
                <span className="text-neutral-400 group-hover:translate-x-1 group-hover:text-black transition-transform">
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
            <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-neutral-100 text-neutral-900 border border-neutral-300 text-xs font-bold mb-2">
              <span className="w-1.5 h-1.5 rounded-full bg-black animate-ping" />
              Mới cập nhật
            </div>
            <h2 className="text-2xl sm:text-3xl font-black text-black">
              Việc làm mới đăng tuyển hôm nay
            </h2>
          </div>
          <Link
            href="/jobs"
            className="inline-flex items-center justify-center gap-2 rounded-xl bg-black px-4 py-2.5 text-sm font-bold text-white shadow-xs hover:bg-neutral-800 transition-colors w-full sm:w-auto"
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
          <span className="text-xs font-bold uppercase tracking-wider text-neutral-500">
            Phân bố địa lý
          </span>
          <h2 className="text-2xl sm:text-3xl font-black text-black mt-1">
            Việc làm tại các tỉnh thành trọng điểm
          </h2>
          <p className="text-sm text-neutral-600 mt-2">
            Tìm kiếm cơ hội nghề nghiệp tại nơi bạn sinh sống hoặc sẵn sàng định cư
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {popularProvinces.map((prov) => (
            <Link
              key={prov.name}
              href={`/jobs?province=${encodeURIComponent(prov.name)}`}
              className="group relative overflow-hidden rounded-2xl border border-neutral-200 bg-white p-6 hover:border-black hover:shadow-md transition-all duration-200"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold px-2 py-0.5 rounded bg-neutral-100 text-neutral-800 border border-neutral-200">
                  {prov.tag}
                </span>
                <span className="text-xs font-bold text-neutral-500">
                  {typeof prov.count === "number"
                    ? `${prov.count.toLocaleString("vi-VN")} việc làm`
                    : `${prov.count} việc làm`}
                </span>
              </div>
              <h3 className="text-xl font-black text-black group-hover:underline transition-colors">
                {prov.name}
              </h3>
              <p className="text-xs text-neutral-600 mt-1 leading-relaxed">
                {prov.desc}
              </p>
              <div className="mt-4 flex items-center text-xs font-bold text-black group-hover:gap-2 transition-all">
                <span>Khám phá ngay</span>
                <ArrowRightIcon className="h-3.5 w-3.5 ml-1" />
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* 6. WHY CHOOSE C_DATA BANNER */}
      <section className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="rounded-3xl bg-neutral-50 border border-neutral-200 p-8 sm:p-12 text-black shadow-xs relative overflow-hidden">
          <div className="relative z-10 max-w-3xl">
            <span className="inline-block text-xs font-bold tracking-widest text-neutral-500 uppercase mb-3">
              Minh bạch • Toàn diện • Tự động hóa
            </span>
            <h2 className="text-2xl sm:text-4xl font-black tracking-tight leading-snug text-black">
              Vì sao hàng vạn ứng viên tin dùng C_Data mỗi ngày?
            </h2>
            <div className="mt-8 grid grid-cols-1 sm:grid-cols-3 gap-6">
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-black font-bold text-base">
                  <CheckBadgeIcon className="h-5 w-5 text-black" />
                  <span>Dữ liệu tập trung</span>
                </div>
                <p className="text-xs text-neutral-600 leading-relaxed">
                  Tổng hợp thông tin từ TopCV, VietnamWorks, CareerViet, ITviec, không bỏ sót bất kỳ cơ hội nào.
                </p>
              </div>

              <div className="space-y-2">
                <div className="flex items-center gap-2 text-black font-bold text-base">
                  <CheckBadgeIcon className="h-5 w-5 text-black" />
                  <span>Cập nhật liên tục</span>
                </div>
                <p className="text-xs text-neutral-600 leading-relaxed">
                  Robot thu thập dữ liệu tự động theo chu kỳ mỗi giờ, loại bỏ tin hết hạn và tin trùng lặp.
                </p>
              </div>

              <div className="space-y-2">
                <div className="flex items-center gap-2 text-black font-bold text-base">
                  <CheckBadgeIcon className="h-5 w-5 text-black" />
                  <span>Phi lợi nhuận 100%</span>
                </div>
                <p className="text-xs text-neutral-600 leading-relaxed">
                  Miễn phí hoàn toàn cho người lao động, chuyển hướng ứng tuyển trực tiếp đến nhà tuyển dụng.
                </p>
              </div>
            </div>

            <div className="mt-8">
              <Link
                href="/about"
                className="inline-flex items-center gap-2 rounded-xl bg-black text-white px-5 py-3 text-sm font-bold shadow-xs hover:bg-neutral-800 transition-colors"
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
