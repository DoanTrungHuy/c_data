"use client";

import React, { useState } from "react";
import { ClipboardDocumentCheckIcon, DocumentDuplicateIcon } from "@heroicons/react/24/outline";

interface CopySourceButtonProps {
  url: string;
  label?: string;
  className?: string;
}

export default function CopySourceButton({
  url,
  label = "Sao chép link",
  className = "",
}: CopySourceButtonProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(url);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <button
      type="button"
      onClick={handleCopy}
      className={`inline-flex items-center gap-1.5 transition-colors cursor-pointer ${className}`}
      title="Sao chép liên kết nguồn để dán vào trình duyệt hoặc app Facebook"
    >
      {copied ? (
        <>
          <ClipboardDocumentCheckIcon className="h-4 w-4 text-emerald-600" />
          <span className="text-emerald-700 font-bold">Đã chép link!</span>
        </>
      ) : (
        <>
          <DocumentDuplicateIcon className="h-4 w-4 text-slate-500" />
          <span>{label}</span>
        </>
      )}
    </button>
  );
}
