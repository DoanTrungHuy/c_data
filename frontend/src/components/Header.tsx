"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BriefcaseIcon,
  Bars3Icon,
  XMarkIcon,
  MagnifyingGlassIcon,
  SparklesIcon,
} from "@heroicons/react/24/outline";
import CDataLogo from "@/components/CDataLogo";

export default function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const pathname = usePathname();

  const navigation = [
    { name: "Trang chủ", href: "/" },
    { name: "Tìm việc làm", href: "/jobs" },
    { name: "Về chúng tôi", href: "/about" },
  ];

  const isActive = (href: string) => {
    if (href === "/") {
      return pathname === "/";
    }
    return pathname.startsWith(href);
  };

  return (
    <header className="sticky top-0 z-50 w-full border-b border-slate-200/80 bg-white/95 backdrop-blur-md transition-all shadow-sm">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8 h-16 md:h-20">
        {/* Brand Logo */}
        <Link href="/" className="group">
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
                className={`px-3.5 py-2 rounded-lg text-sm font-semibold transition-colors duration-150 ${
                  active
                    ? "bg-primary-50 text-primary-600"
                    : "text-slate-600 hover:text-primary-600 hover:bg-slate-50"
                }`}
              >
                {item.name}
              </Link>
            );
          })}
        </nav>

        {/* Action Button & Search */}
        <div className="hidden md:flex items-center gap-3">
          <Link
            href="/jobs"
            className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-slate-600 hover:text-primary-600 rounded-lg hover:bg-slate-100 transition-colors"
            title="Tìm kiếm việc làm nhanh"
          >
            <MagnifyingGlassIcon className="h-4 w-4" />
            <span>Tìm kiếm</span>
          </Link>
          <Link
            href="/jobs"
            className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-primary-600 to-blue-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:from-primary-700 hover:to-blue-700 hover:shadow-md hover:shadow-primary-500/20 transition-all duration-200 active:scale-95"
          >
            <SparklesIcon className="h-4 w-4 text-amber-300" />
            <span>Khám phá việc làm</span>
          </Link>
        </div>

        {/* Mobile menu button */}
        <div className="flex md:hidden items-center gap-2">
          <Link
            href="/jobs"
            className="p-2 text-slate-600 hover:text-primary-600 rounded-lg hover:bg-slate-100"
            aria-label="Tìm việc"
          >
            <MagnifyingGlassIcon className="h-5 w-5" />
          </Link>
          <button
            type="button"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 rounded-lg text-slate-700 hover:bg-slate-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
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
        <div className="md:hidden border-t border-slate-200 bg-white px-4 pt-3 pb-6 shadow-xl animate-in fade-in slide-in-from-top-2 duration-200">
          <div className="flex flex-col space-y-1">
            {navigation.map((item) => {
              const active = isActive(item.href);
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`px-3 py-2.5 rounded-lg text-base font-semibold ${
                    active
                      ? "bg-primary-50 text-primary-600 font-bold"
                      : "text-slate-700 hover:bg-slate-50 hover:text-primary-600"
                  }`}
                >
                  {item.name}
                </Link>
              );
            })}
          </div>
          <div className="mt-4 pt-4 border-t border-slate-100">
            <Link
              href="/jobs"
              onClick={() => setMobileMenuOpen(false)}
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-primary-600 py-3 text-center text-sm font-semibold text-white shadow-sm hover:bg-primary-700"
            >
              <SparklesIcon className="h-4 w-4 text-amber-300" />
              <span>Khám phá toàn bộ việc làm</span>
            </Link>
          </div>
        </div>
      )}
    </header>
  );
}
