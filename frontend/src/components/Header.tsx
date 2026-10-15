"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Bars3Icon,
  XMarkIcon,
  BookmarkIcon,
  ArrowRightIcon,
} from "@heroicons/react/24/outline";
import CDataLogo from "@/components/CDataLogo";
import { useSavedJobs } from "@/lib/savedJobs";
import SystemHealthBadge from "@/components/SystemHealthBadge";

export default function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const pathname = usePathname();
  const { count: savedCount } = useSavedJobs();

  const navigation = [
    { name: "Tìm việc làm", href: "/jobs" },
    {
      name: "IT Hạ Long",
      href: "/jobs?q=IT&province=Qu%E1%BA%A3ng+Ninh",
    },
    { name: "Về chúng tôi", href: "/about" },
  ];

  const isActive = (href: string) => {
    if (href === "/") return pathname === "/";
    return pathname.startsWith(href);
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b border-neutral-200 bg-white/95 backdrop-blur-md transition-all">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8 h-16 sm:h-18">
        {/* Brand Logo - VịnhViệc */}
        <Link href="/" className="group flex items-center">
          <CDataLogo size="md" />
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-1 lg:gap-2">
          {navigation.map((item) => {
            const active = isActive(item.href);
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`px-3.5 py-2 rounded-xl text-sm font-semibold transition-colors duration-150 ${
                  active
                    ? "bg-neutral-100 text-black font-bold"
                    : "text-neutral-600 hover:text-black hover:bg-neutral-50"
                }`}
              >
                {item.name}
              </Link>
            );
          })}
        </nav>

        {/* Desktop Actions */}
        <div className="hidden md:flex items-center gap-3">
          {/* Subtle Verified Status Badge */}
          <SystemHealthBadge />

          {/* Saved Jobs Bookmark Pill */}
          <Link
            href="/jobs?saved=true"
            className="relative flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold text-neutral-700 hover:text-black hover:bg-neutral-100 border border-neutral-200 transition-colors"
            title="Danh sách việc làm đã lưu"
          >
            <BookmarkIcon className="h-4 w-4 text-black" />
            <span>Đã lưu</span>
            {savedCount > 0 && (
              <span className="flex h-4 min-w-4 px-1 items-center justify-center rounded-full bg-black text-[10px] font-bold text-white">
                {savedCount}
              </span>
            )}
          </Link>

          {/* Single Primary Action CTA */}
          <Link
            href="/jobs"
            className="inline-flex items-center gap-1.5 px-4 py-2 bg-black hover:bg-neutral-800 text-white text-xs font-bold rounded-xl shadow-xs transition-colors duration-150"
          >
            <span>Khám phá việc làm</span>
            <ArrowRightIcon className="h-3.5 w-3.5" />
          </Link>
        </div>

        {/* Mobile menu button */}
        <div className="flex md:hidden items-center gap-2">
          <Link
            href="/jobs?saved=true"
            className="relative p-2 text-neutral-700 hover:text-black rounded-lg"
            aria-label="Việc làm đã lưu"
          >
            <BookmarkIcon className="h-5 w-5 text-black" />
            {savedCount > 0 && (
              <span className="absolute top-1 right-1 flex h-4 w-4 items-center justify-center rounded-full bg-black text-[9px] font-bold text-white">
                {savedCount}
              </span>
            )}
          </Link>

          <button
            type="button"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 rounded-lg text-neutral-800 hover:bg-neutral-100 focus:outline-none"
            aria-label="Mở menu"
          >
            {mobileMenuOpen ? (
              <XMarkIcon className="h-6 w-6" />
            ) : (
              <Bars3Icon className="h-6 w-6" />
            )}
          </button>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-neutral-200 bg-white px-4 pt-3 pb-6 shadow-xl animate-in fade-in duration-150 space-y-3">
          <div className="flex flex-col space-y-1">
            {navigation.map((item) => {
              const active = isActive(item.href);
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`px-3 py-2.5 rounded-xl text-base font-semibold ${
                    active
                      ? "bg-neutral-100 text-black font-bold"
                      : "text-neutral-700 hover:bg-neutral-50 hover:text-black"
                  }`}
                >
                  {item.name}
                </Link>
              );
            })}
            <Link
              href="/jobs?saved=true"
              onClick={() => setMobileMenuOpen(false)}
              className="px-3 py-2.5 rounded-xl text-base font-semibold text-neutral-800 hover:bg-neutral-100 flex items-center justify-between"
            >
              <span className="flex items-center gap-2">
                <BookmarkIcon className="h-5 w-5 text-black" />
                <span>Việc làm đã lưu</span>
              </span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-black text-white font-bold">
                {savedCount}
              </span>
            </Link>
          </div>
          <div className="pt-2 border-t border-neutral-100 flex flex-col gap-2.5">
            <div className="flex items-center justify-between px-1">
              <span className="text-xs text-neutral-500 font-medium">Hệ thống tuyển dụng:</span>
              <SystemHealthBadge />
            </div>
            <Link
              href="/jobs"
              onClick={() => setMobileMenuOpen(false)}
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-black py-3 text-center text-sm font-semibold text-white shadow-xs hover:bg-neutral-800"
            >
              <span>Tất cả việc làm</span>
              <ArrowRightIcon className="h-4 w-4" />
            </Link>
          </div>
        </div>
      )}
    </header>
  );
}
