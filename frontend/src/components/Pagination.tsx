"use client";

import React from "react";
import Link from "next/link";
import { usePathname, useSearchParams } from "next/navigation";
import { ChevronLeftIcon, ChevronRightIcon } from "@heroicons/react/24/outline";

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange?: (page: number) => void;
}

export default function Pagination({
  currentPage,
  totalPages,
  onPageChange,
}: PaginationProps) {
  const pathname = usePathname();
  const searchParams = useSearchParams();

  if (totalPages <= 1) return null;

  const createPageURL = (pageNumber: number | string) => {
    const params = new URLSearchParams(searchParams?.toString() || "");
    params.set("page", pageNumber.toString());
    return `${pathname}?${params.toString()}`;
  };

  // Generate pagination items
  const getPageNumbers = () => {
    const pages: (number | string)[] = [];
    const maxVisible = 5;

    if (totalPages <= maxVisible + 2) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      pages.push(1);

      if (currentPage > 3) {
        pages.push("...");
      }

      const start = Math.max(2, currentPage - 1);
      const end = Math.min(totalPages - 1, currentPage + 1);

      for (let i = start; i <= end; i++) {
        pages.push(i);
      }

      if (currentPage < totalPages - 2) {
        pages.push("...");
      }

      pages.push(totalPages);
    }

    return pages;
  };

  const pages = getPageNumbers();

  const handlePageClick = (
    e: React.MouseEvent<HTMLAnchorElement>,
    page: number
  ) => {
    if (onPageChange) {
      e.preventDefault();
      onPageChange(page);
    }
  };

  return (
    <nav
      className="flex items-center justify-between border-t border-slate-200 px-4 py-4 sm:px-0"
      aria-label="Phân trang"
    >
      {/* Previous Button */}
      <div className="-mt-px flex w-0 flex-1">
        {currentPage > 1 ? (
          <Link
            href={createPageURL(currentPage - 1)}
            onClick={(e) => handlePageClick(e, currentPage - 1)}
            className="inline-flex items-center gap-2 border-t-2 border-transparent pr-1 pt-4 text-sm font-semibold text-slate-600 hover:border-primary-500 hover:text-primary-600 transition-colors"
          >
            <ChevronLeftIcon className="h-4 w-4" aria-hidden="true" />
            <span>Trang trước</span>
          </Link>
        ) : (
          <span className="inline-flex items-center gap-2 border-t-2 border-transparent pr-1 pt-4 text-sm font-semibold text-slate-300 cursor-not-allowed">
            <ChevronLeftIcon className="h-4 w-4" aria-hidden="true" />
            <span>Trang trước</span>
          </span>
        )}
      </div>

      {/* Page Numbers */}
      <div className="hidden md:-mt-px md:flex gap-1">
        {pages.map((p, idx) => {
          if (p === "...") {
            return (
              <span
                key={`ellipsis-${idx}`}
                className="inline-flex items-center border-t-2 border-transparent px-3 pt-4 text-sm font-medium text-slate-400"
              >
                ...
              </span>
            );
          }

          const pageNum = Number(p);
          const isCurrent = pageNum === currentPage;

          return (
            <Link
              key={`page-${pageNum}`}
              href={createPageURL(pageNum)}
              onClick={(e) => handlePageClick(e, pageNum)}
              className={`inline-flex items-center border-t-2 px-3 pt-4 text-sm font-bold transition-colors ${
                isCurrent
                  ? "border-primary-600 text-primary-600 font-extrabold"
                  : "border-transparent text-slate-500 hover:border-slate-300 hover:text-slate-700"
              }`}
              aria-current={isCurrent ? "page" : undefined}
            >
              {pageNum}
            </Link>
          );
        })}
      </div>

      {/* Mobile Page indicator */}
      <div className="flex md:hidden text-xs font-semibold text-slate-500 pt-4">
        Trang {currentPage} / {totalPages}
      </div>

      {/* Next Button */}
      <div className="-mt-px flex w-0 flex-1 justify-end">
        {currentPage < totalPages ? (
          <Link
            href={createPageURL(currentPage + 1)}
            onClick={(e) => handlePageClick(e, currentPage + 1)}
            className="inline-flex items-center gap-2 border-t-2 border-transparent pl-1 pt-4 text-sm font-semibold text-slate-600 hover:border-primary-500 hover:text-primary-600 transition-colors"
          >
            <span>Trang sau</span>
            <ChevronRightIcon className="h-4 w-4" aria-hidden="true" />
          </Link>
        ) : (
          <span className="inline-flex items-center gap-2 border-t-2 border-transparent pl-1 pt-4 text-sm font-semibold text-slate-300 cursor-not-allowed">
            <span>Trang sau</span>
            <ChevronRightIcon className="h-4 w-4" aria-hidden="true" />
          </span>
        )}
      </div>
    </nav>
  );
}
