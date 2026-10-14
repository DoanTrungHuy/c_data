import React from "react";

export default function JobCardSkeleton() {
  return (
    <div className="flex flex-col justify-between rounded-2xl border border-slate-200/80 bg-white p-5 sm:p-6 animate-pulse">
      <div>
        {/* Top Header skeleton */}
        <div className="flex items-start justify-between gap-3 mb-4">
          <div className="flex items-center gap-3">
            <div className="h-11 w-11 rounded-xl bg-slate-200 shrink-0" />
            <div className="space-y-1.5">
              <div className="h-3.5 w-32 bg-slate-200 rounded" />
              <div className="h-2.5 w-20 bg-slate-100 rounded" />
            </div>
          </div>
          <div className="h-6 w-20 bg-slate-200 rounded-full" />
        </div>

        {/* Title skeleton */}
        <div className="space-y-2 mb-3">
          <div className="h-5 w-4/5 bg-slate-200 rounded" />
          <div className="h-4 w-3/5 bg-slate-100 rounded" />
        </div>

        {/* Badges skeleton */}
        <div className="flex items-center gap-2 mb-3">
          <div className="h-6 w-24 bg-slate-200 rounded-lg" />
          <div className="h-6 w-20 bg-slate-100 rounded-lg" />
        </div>

        {/* Location skeleton */}
        <div className="h-4 w-36 bg-slate-100 rounded" />
      </div>

      {/* Footer skeleton */}
      <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
        <div className="h-3.5 w-20 bg-slate-200 rounded" />
        <div className="h-3.5 w-16 bg-slate-100 rounded" />
      </div>
    </div>
  );
}
