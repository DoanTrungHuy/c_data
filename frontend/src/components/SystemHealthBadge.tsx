"use client";

import React, { useState, useEffect } from "react";
import { createPortal } from "react-dom";
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
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <>
      <div className="inline-flex items-center">
        <button
          type="button"
          onClick={() => setModalOpen(true)}
          className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl bg-neutral-100 hover:bg-neutral-200 border border-neutral-300 text-xs font-bold text-neutral-900 transition-colors cursor-pointer"
          title="Hệ thống xác thực Zero-404: 100% việc làm đang tuyển dụng thực tế"
        >
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-black opacity-40" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-black" />
          </span>
          <span className="flex items-center gap-1">
            <ShieldCheckIcon className="h-3.5 w-3.5 text-black" />
            <span>Zero-404</span>
          </span>
        </button>
      </div>

      {/* System Health Status Details Modal */}
      {modalOpen && mounted && createPortal(
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-3 sm:p-6 overflow-y-auto">
          <div
            className="fixed inset-0 bg-black/60 backdrop-blur-xs transition-opacity"
            onClick={() => setModalOpen(false)}
          />

          <div className="relative w-full max-w-xl max-h-[90vh] overflow-y-auto rounded-3xl bg-white shadow-2xl border border-neutral-200 p-5 sm:p-8 z-10 space-y-5 animate-fadeIn">
            {/* Header */}
            <div className="flex items-start justify-between pb-3 border-b border-neutral-100">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-neutral-100 text-black border border-neutral-200">
                  <ShieldCheckIcon className="h-6 w-6" />
                </div>
                <div>
                  <h3 className="font-extrabold text-black text-base flex items-center gap-1.5">
                    <span>Hệ Thống Kiểm Duyệt Tuyển Dụng & Zero-404</span>
                  </h3>
                  <p className="text-xs text-neutral-500 mt-0.5">
                    Quy trình kiểm tra 2 lớp bảo chứng tin tuyển dụng còn đang hoạt động
                  </p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setModalOpen(false)}
                className="p-1.5 rounded-xl text-neutral-400 hover:text-black hover:bg-neutral-100 transition-colors"
              >
                <XMarkIcon className="h-5 w-5" />
              </button>
            </div>

            {/* Checklist items */}
            <div className="space-y-3 text-xs">
              <div className="p-3.5 rounded-2xl bg-neutral-50 border border-neutral-200 flex items-start gap-3">
                <CheckBadgeIcon className="h-5 w-5 text-black shrink-0 mt-0.5" />
                <div>
                  <p className="font-bold text-black">
                    Kiểm định HTTP Status 200 OK
                  </p>
                  <p className="text-neutral-600 text-[11px] mt-0.5 leading-relaxed">
                    Mọi đường link nguồn đều được bot tự động gửi HTTP Request kiểm tra. Những link bị lỗi 404, 500 hoặc trang hết hạn bị xóa lập tức khỏi hệ thống.
                  </p>
                </div>
              </div>

              <div className="p-3.5 rounded-2xl bg-neutral-50 border border-neutral-200 flex items-start gap-3">
                <ClockIcon className="h-5 w-5 text-black shrink-0 mt-0.5" />
                <div>
                  <p className="font-bold text-black">
                    Cập nhật liên tục 30 phút / lần & Cloud Actions 6h
                  </p>
                  <p className="text-neutral-600 text-[11px] mt-0.5 leading-relaxed">
                    Harvester daemon chạy nền tự động dò tìm tin tuyển dụng mới tại Hạ Long và đồng bộ trực tiếp lên GitHub Pages.
                  </p>
                </div>
              </div>

              <div className="p-3.5 rounded-2xl bg-neutral-50 border border-neutral-200 flex items-start gap-3">
                <GlobeAmericasIcon className="h-5 w-5 text-black shrink-0 mt-0.5" />
                <div>
                  <p className="font-bold text-black">
                    Lưu trữ toàn văn & Số điện thoại / Zalo HR trực tiếp
                  </p>
                  <p className="text-neutral-600 text-[11px] mt-0.5 leading-relaxed">
                    Trích xuất đầy đủ mô tả, yêu cầu và số điện thoại Zalo của bộ phận nhân sự để bạn ứng tuyển thuận tiện nhất mà không lo bị chặn bởi các nền tảng ngoài.
                  </p>
                </div>
              </div>
            </div>

            <div className="pt-2 text-center">
              <button
                type="button"
                onClick={() => setModalOpen(false)}
                className="w-full py-2.5 rounded-xl bg-black hover:bg-neutral-800 text-white font-bold text-xs transition-colors"
              >
                Đã hiểu
              </button>
            </div>
          </div>
        </div>,
        document.body
      )}
    </>
  );
}
