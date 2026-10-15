import React from "react";
import Link from "next/link";
import {
  BriefcaseIcon,
  MapPinIcon,
  HeartIcon,
  SparklesIcon,
  CheckBadgeIcon,
  CommandLineIcon,
  CircleStackIcon,
  ArrowRightIcon,
  EnvelopeIcon,
  GlobeAltIcon,
  CodeBracketIcon,
} from "@heroicons/react/24/outline";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Về Chúng Tôi - Câu Chuyện & Sứ Mệnh C_Data",
  description:
    "C_Data sinh ra từ Hạ Long, Quảng Ninh với khát vọng kết nối mọi người lao động Việt Nam với cơ hội việc làm minh bạch, cập nhật liên tục từ mọi nguồn.",
};

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-white pb-20">
      {/* Hero Header */}
      <section className="relative overflow-hidden bg-neutral-50 border-b border-neutral-200 py-16 md:py-24">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 text-center space-y-6">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white border border-neutral-300 text-xs font-bold text-neutral-900 shadow-2xs">
            <SparklesIcon className="h-4 w-4 text-black" />
            <span>Sứ mệnh kết nối việc làm Việt Nam</span>
          </div>

          <h1 className="text-3xl sm:text-5xl font-black text-black tracking-tight leading-tight">
            Mang cơ hội nghề nghiệp đến với mọi người trên khắp{" "}
            <span className="underline decoration-neutral-300 underline-offset-8">
              63 Tỉnh Thành
            </span>
          </h1>

          <p className="text-base sm:text-lg text-neutral-600 max-w-3xl mx-auto leading-relaxed">
            C_Data là nền tảng tổng hợp dữ liệu việc làm mở, tự động thu thập và chuẩn hóa hàng nghìn tin tuyển dụng mỗi ngày từ các trang việc làm hàng đầu Việt Nam.
          </p>
        </div>
      </section>

      <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8 pt-12 space-y-16">
        {/* Story Section */}
        <section className="rounded-3xl border border-neutral-200 bg-white p-8 sm:p-12 shadow-xs space-y-6">
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-neutral-500">
            <MapPinIcon className="h-4 w-4 text-black" />
            <span>Khởi nguồn từ vùng đất Vịnh</span>
          </div>

          <h2 className="text-2xl sm:text-3xl font-black text-black">
            Câu chuyện ra đời của C_Data tại Hạ Long, Quảng Ninh
          </h2>

          <div className="prose-content text-neutral-700 space-y-4 text-base leading-relaxed">
            <p>
              Ý tưởng về <strong>C_Data</strong> được nhen nhóm tại thành phố biển <strong>Hạ Long, tỉnh Quảng Ninh</strong>. Giữa nhịp sống năng động của vùng Đông Bắc đang trên đà phát triển mạnh mẽ về kinh tế biển, du lịch, công nghiệp và chuyển đổi số, chúng tôi nhận thấy một bài toán nan giải:
            </p>
            <blockquote className="border-l-4 border-black pl-4 py-2 italic bg-neutral-50 rounded-r-xl text-neutral-900 font-medium">
              "Người tìm việc thường phải tải hàng chục ứng dụng, mở vô số tab website tuyển dụng khác nhau chỉ để tìm một công việc phù hợp với mức lương minh bạch tại tỉnh nhà hoặc các tỉnh lân cận."
            </blockquote>
            <p>
              Đối với những người lao động trẻ tại các tỉnh thành ngoài hai trung tâm lớn là Hà Nội và TP. Hồ Chí Minh, việc tiếp cận thông tin tuyển dụng chất lượng cao càng khó khăn hơn do dữ liệu bị phân tán, nhiều tin tuyển dụng lỗi thời hoặc không rõ ràng về mức lương và chế độ đãi ngộ.
            </p>
            <p>
              Từ trăn trở đó, đội ngũ kỹ sư tại C_Data đã quyết định bắt tay xây dựng một giải pháp kỹ thuật: một hệ thống crawler tự động, liên tục quét, loại bỏ tin rác, đồng bộ và hiển thị dữ liệu tập trung theo thời gian thực — <strong>hoàn toàn miễn phí vì lợi ích cộng đồng</strong>.
            </p>
          </div>
        </section>

        {/* How It Works Section */}
        <section id="how-it-works" className="space-y-8">
          <div className="text-center max-w-2xl mx-auto">
            <span className="text-xs font-bold uppercase tracking-wider text-neutral-500">
              Kiến trúc kỹ thuật
            </span>
            <h2 className="text-2xl sm:text-3xl font-black text-black mt-1">
              Hệ thống C_Data vận hành như thế nào?
            </h2>
            <p className="text-sm text-neutral-600 mt-2">
              Kết hợp sức mạnh của Celery Crawler, FastAPI Backend và Next.js 14 Frontend hiện đại
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-6 rounded-2xl bg-white border border-neutral-200 shadow-xs space-y-3">
              <div className="h-12 w-12 rounded-xl bg-neutral-100 text-black border border-neutral-300 flex items-center justify-center font-black text-xl">
                1
              </div>
              <h3 className="font-bold text-black text-lg">
                Thu thập đa nguồn (Crawling)
              </h3>
              <p className="text-xs text-neutral-600 leading-relaxed">
                Các worker Celery chạy định kỳ, thu thập dữ liệu an toàn từ TopCV, VietnamWorks, CareerViet, ITviec, Việc Làm 24h và LinkedIn.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-white border border-neutral-200 shadow-xs space-y-3">
              <div className="h-12 w-12 rounded-xl bg-neutral-100 text-black border border-neutral-300 flex items-center justify-center font-black text-xl">
                2
              </div>
              <h3 className="font-bold text-black text-lg">
                Chuẩn hóa & Khử trùng lặp
              </h3>
              <p className="text-xs text-neutral-600 leading-relaxed">
                Hệ thống chuẩn hóa 63 tỉnh thành, bóc tách khoảng lương, phân loại ngành nghề và loại bỏ tin hết hạn vào cơ sở dữ liệu PostgreSQL.
              </p>
            </div>

            <div className="p-6 rounded-2xl bg-white border border-neutral-200 shadow-xs space-y-3">
              <div className="h-12 w-12 rounded-xl bg-neutral-100 text-black border border-neutral-300 flex items-center justify-center font-black text-xl">
                3
              </div>
              <h3 className="font-bold text-black text-lg">
                Tra cứu & Ứng tuyển tức thì
              </h3>
              <p className="text-xs text-neutral-600 leading-relaxed">
                Giao diện Next.js tải nhanh, hỗ trợ lọc theo mức lương, hình thức làm việc và chuyển hướng ứng viên trực tiếp đến nguồn gốc.
              </p>
            </div>
          </div>
        </section>

        {/* Open Source & Community Commitment */}
        <section className="rounded-3xl bg-neutral-50 border border-neutral-200 p-8 sm:p-12 text-black space-y-6">
          <div className="flex items-center gap-2 text-neutral-500 text-xs font-bold tracking-wider uppercase">
            <CodeBracketIcon className="h-4 w-4 text-black" />
            <span>Mã nguồn mở & Cam kết cộng đồng</span>
          </div>

          <h2 className="text-2xl sm:text-3xl font-black text-black">
            Minh bạch tuyệt đối — Không thu phí người tìm việc
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2 text-neutral-700 text-sm leading-relaxed">
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-black font-bold">
                <CheckBadgeIcon className="h-5 w-5 text-black" />
                <span>Không thương mại hóa dữ liệu</span>
              </div>
              <p className="text-xs text-neutral-600">
                Chúng tôi không lưu trữ trái phép hồ sơ cá nhân của bạn, không bán dữ liệu cho bên thứ ba và không chèn quảng cáo gây phiền toái.
              </p>
            </div>

            <div className="space-y-3">
              <div className="flex items-center gap-2 text-black font-bold">
                <CheckBadgeIcon className="h-5 w-5 text-black" />
                <span>Bảo vệ quyền tác giả nguồn gốc</span>
              </div>
              <p className="text-xs text-neutral-600">
                Mọi tin việc làm đều ghi rõ nền tảng nguồn và cung cấp đường dẫn trực tiếp để ứng viên nộp hồ sơ an toàn và chính thống nhất.
              </p>
            </div>
          </div>
        </section>

        {/* Contact Info Section */}
        <section id="contact" className="rounded-3xl border border-neutral-200 bg-white p-8 sm:p-12 shadow-xs space-y-6">
          <span className="text-xs font-bold uppercase tracking-wider text-neutral-500">
            Liên hệ & Hợp tác
          </span>
          <h2 className="text-2xl sm:text-3xl font-black text-black">
            Kết nối cùng đội ngũ C_Data
          </h2>
          <p className="text-sm text-neutral-600 leading-relaxed">
            Bạn là doanh nghiệp muốn đóng góp ý kiến hoặc nhà phát triển muốn tham gia mở rộng crawler cho nhiều nguồn hơn? Chúng tôi luôn sẵn sàng lắng nghe!
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-4 text-sm">
            <div className="flex items-center gap-3 p-4 rounded-2xl bg-neutral-50 border border-neutral-200">
              <MapPinIcon className="h-6 w-6 text-black shrink-0" />
              <div>
                <span className="text-xs text-neutral-500 font-medium block">
                  Địa chỉ
                </span>
                <span className="font-bold text-neutral-900">
                  Thành phố Hạ Long, Tỉnh Quảng Ninh, Việt Nam
                </span>
              </div>
            </div>

            <div className="flex items-center gap-3 p-4 rounded-2xl bg-neutral-50 border border-neutral-200">
              <EnvelopeIcon className="h-6 w-6 text-black shrink-0" />
              <div>
                <span className="text-xs text-neutral-500 font-medium block">
                  Email hỗ trợ
                </span>
                <span className="font-bold text-neutral-900">
                  contact@cdata.vn / huy.cdata@gmail.com
                </span>
              </div>
            </div>
          </div>

          <div className="pt-6 border-t border-neutral-200 flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="text-xs text-neutral-500">
              Cảm ơn bạn đã đồng hành cùng cộng đồng C_Data!
            </p>
            <Link
              href="/jobs"
              className="inline-flex items-center gap-2 rounded-xl bg-black px-5 py-2.5 text-xs font-bold text-white hover:bg-neutral-800 shadow-xs transition-colors"
            >
              <span>Bắt đầu tìm việc làm</span>
              <ArrowRightIcon className="h-4 w-4" />
            </Link>
          </div>
        </section>
      </div>
    </div>
  );
}
