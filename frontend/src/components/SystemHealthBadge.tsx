"use client";

import React, { useState } from "react";
import {
  ShieldCheckIcon,
  CheckBadgeIcon,
  ClockIcon,
  ArrowPathIcon,
  XMarkIcon,
  ServerIcon,
  GlobeAmericasIcon,
} from "@heroicons/react/24/outline";

export default function SystemHealthBadge() {
  const [modalOpen, setModalOpen] = useState(false);

  return (
    <>
      <div className="inline-flex items-center">
        <button
          type="button"
          onClick={() => setModalOpen(true)}
          className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl bg-emerald-50/80 hover:bg-emerald-100/80 border border-emerald-200/70 text-xs font-semibold text-emerald-800 transition-colors cursor-pointer"
          title="Hệ thống xác thực Zero-404: 100% việc làm đang tuyển dụng thực tế"
        >
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
          </span>
          <span className="flex items-center gap-1">
            <ShieldCheckIcon className="h-3.5 w-3.5 text-emerald-600" />
            <span>Zero-404</span>
          </span>
        </button>
      </div>

      {/* System Health Status Details Modal */}
      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 overflow-y-auto">
          <div
            className="fixed inset-0 bg-slate-900/60 backdrop-blur-xs transition-opacity"
            onClick={() => setModalOpen(false)}
          />

          <div className="relative w-full max-w-xl rounded-3xl bg-white shadow-2xl border border-slate-200 p-6 sm:p-8 z-10 space-y-5 animate-fadeIn">
            {/* Header */}
            <div className="flex items-start justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-emerald-50 text-emerald-600 border border-emerald-200">
                  <ShieldCheckIcon className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="font-extrabold text-slate-900 text-base flex items-center gap-1.5">
                    <span>Hệ Thống Kiểm Duyệt Tuyển Dụng & Zero-404</span>
                  </h3>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Quy trình kiểm tra 2 lớp bảo chứng tin tuyển dụng còn đang hoạt động
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setModalOpen(false)}
                className="p-1.5 rounded-xl text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
              >
                <XMarkIcon className="h-5 w-5" />
              </button>
            </div>

            {/* Checklist items */}
            <div className="space-y-3 text-xs">
              <div className="p-3.5 rounded-2xl bg-emerald-50/70 border border-emerald-200 flex items-start gap-3">
                <CheckBadgeIcon className="h-5 w-5 text-emerald-600 shrink-0 mt-0.5" />
                <div>
                  <p className="font-bold text-emerald-950">
                    Kiểm định HTTP Status 200 OK
                  </p>
                  <p className="text-emerald-800 text-[11px] mt-0.5 leading-relaxed">
                    Mọi đường link nguồn đều được bot tự động gửi HTTP Request kiểm tra. Những link bị lỗi 404, 500 hoặc trang hết hạn bị xóa lập tức khỏi hệ thống.
                  </p>
                </div>
              </div>

              <div className="p-3.5 rounded-2xl bg-blue-50/70 border border-blue-200 flex items-start gap-3">
                <ClockIcon className="h-5 w-5 text-blue-600 shrink-0 mt-0.5" />
                <div>
                  <p className="font-bold text-blue-950">
                    Cập nhật liên tục 30 phút / lần & Cloud Actions 6h
                  </p>
                  <p className="text-blue-800 text-[11px] mt-0.5 leading-relaxed">
                    Harvester daemon chạy nền tự động dò tìm tin tuyển dụng mới tại Hạ Long và đồng bộ trực tiếp lên GitHub Pages.
                  </p>
                </div>
              </div>

              <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 flex items-start gap-3">
                <GlobeAmericasIcon className="h-5 w-5 text-primary-600 shrink-0 mt-0.5" />
                <div>
                  <p className="font-bold text-slate-900">
                    Lưu trữ toàn văn & Số điện thoại / Zalo HR trực tiếp
                  </p>
                  <p className="text-slate-600 text-[11px] mt-0.5 leading-relaxed">
                    Trích xuất đầy đủ mô tả, yêu cầu và số điện thoại Zalo của bộ phận nhân sự để bạn ứng tuyển thuận tiện nhất mà không lo bị chặn bởi các nền tảng ngoài.
                  </p>
                </div>
              </div>
            </div>

            <div className="pt-2 text-center">
              <button
                type="button"
                onClick={() => setModalOpen(false)}
                className="w-full py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs transition-colors"
              >
                Đã hiểu
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
