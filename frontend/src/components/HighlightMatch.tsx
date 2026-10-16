"use client";

import React, { useMemo } from "react";

interface HighlightMatchProps {
  text: string;
  query?: string;
  className?: string;
  matchClassName?: string;
}

// 1:1 Character mapping to strip Vietnamese diacritics without changing string length
const VIETNAMESE_ACCENT_MAP: Record<string, string> = {
  à: "a", á: "a", ả: "a", ã: "a", ạ: "a",
  ă: "a", ắ: "a", ằ: "a", ẳ: "a", ẵ: "a", ặ: "a",
  â: "a", ấn: "a", ầ: "a", ẩ: "a", ẫ: "a", ậ: "a",
  è: "e", é: "e", ẻ: "e", ẽ: "e", ẹ: "e",
  ê: "e", ế: "e", ề: "e", ể: "e", ễ: "e", ệ: "e",
  ì: "i", í: "i", ỉ: "i", ĩ: "i", ị: "i",
  ò: "o", ó: "o", ỏ: "o", õ: "o", ọ: "o",
  ô: "o", ố: "o", ồ: "o", ổ: "o", ỗ: "o", ộ: "o",
  ơ: "o", ớ: "o", ờ: "o", ở: "o", ỡ: "o", ợ: "o",
  ù: "u", ú: "u", ủ: "u", ũ: "u", ụ: "u",
  ư: "u", ứ: "u", ừ: "u", ử: "u", ữ: "u", ự: "u",
  ỳ: "y", ý: "y", ỷ: "y", ỹ: "y", ỵ: "y",
  đ: "d",
  À: "A", Á: "A", Ả: "A", Ã: "A",Ạ: "A",
  Ă: "A", Ắ: "A", Ằ: "A", Ẳ: "A", Ẵ: "A", Ặ: "A",
  Â: "A", Ấ: "A", Ầ: "A", Ẩ: "A", Ẫ: "A", Ậ: "A",
  È: "E", É: "E", Ẻ: "E", Ẽ: "E", Ẹ: "E",
  Ê: "E", Ế: "E", Ề: "E", Ể: "E", Ễ: "E", Ệ: "E",
  Ì: "I", Í: "I", Ỉ: "I", Ĩ: "I", Ị: "I",
  Ò: "O", Ó: "O", Ỏ: "O", Õ: "O", Ọ: "O",
  Ô: "O", Ố: "O", Ồ: "O", Ổ: "O", Ỗ: "O", Ộ: "O",
  Ơ: "O", Ớ: "O", Ờ: "O", Ở: "O", Ỡ: "O", Ợ: "O",
  Ù: "U", Ú: "U", Ủ: "U", Ũ: "U", Ụ: "U",
  Ư: "U", Ứ: "U", Ừ: "U", Ử: "U", Ữ: "U", Ự: "U",
  Ỳ: "Y", Ý: "Y", Ỷ: "Y", Ỹ: "Y", Ỵ: "Y",
  Đ: "D",
};

export function stripTonesExact(str: string): string {
  if (!str) return "";
  return str.replace(/[^a-zA-Z0-9 ]/g, (ch) => VIETNAMESE_ACCENT_MAP[ch] || ch);
}

function isWordChar(char?: string): boolean {
  if (!char) return false;
  return /[a-zA-Z0-9]/.test(char);
}

export default function HighlightMatch({
  text,
  query,
  className = "",
  matchClassName = "bg-neutral-200 text-black font-bold px-0.5 rounded-xs",
}: HighlightMatchProps) {
  const parts = useMemo(() => {
    if (!text || !query || !query.trim()) {
      return [{ text, match: false }];
    }

    const normText = stripTonesExact(text).toLowerCase();
    const rawTerms = query
      .trim()
      .split(/\s+/)
      .filter((t) => t.length > 0);
    // Include full phrase first, then individual words
    const terms = [query.trim(), ...rawTerms].filter(
      (t, i, arr) => arr.indexOf(t) === i
    );

    const ranges: [number, number][] = [];

    for (const term of terms) {
      const lowerTerm = term.toLowerCase();
      // Skip 1-character terms unless standard abbreviations
      if (
        term.length < 2 &&
        !["it", "c#", "c+", "ai", "ui", "ux"].includes(lowerTerm)
      ) {
        continue;
      }

      const normTerm = stripTonesExact(term).toLowerCase();
      let pos = 0;
      while ((pos = normText.indexOf(normTerm, pos)) !== -1) {
        const prevChar = pos > 0 ? normText[pos - 1] : "";
        const nextChar =
          pos + normTerm.length < normText.length
            ? normText[pos + normTerm.length]
            : "";

        const isStartWord = !isWordChar(prevChar);
        // Short terms must be separated by boundary at end as well
        const isEndWord = normTerm.length <= 3 ? !isWordChar(nextChar) : true;

        if (isStartWord && isEndWord) {
          ranges.push([pos, pos + normTerm.length]);
        }
        pos += 1;
      }
    }

    if (ranges.length === 0) {
      return [{ text, match: false }];
    }

    // Sort ranges by start pos
    ranges.sort((a, b) => a[0] - b[0] || b[1] - a[1]);

    // Merge overlapping and adjacent (with single space) ranges
    const merged: [number, number][] = [ranges[0]];
    for (let i = 1; i < ranges.length; i++) {
      const last = merged[merged.length - 1];
      const curr = ranges[i];

      const isAdjacentSpace =
        curr[0] - last[1] <= 1 && normText.slice(last[1], curr[0]) === " ";

      if (curr[0] <= last[1] || isAdjacentSpace) {
        last[1] = Math.max(last[1], curr[1]);
      } else {
        merged.push(curr);
      }
    }

    // Build segments
    const segments: { text: string; match: boolean }[] = [];
    let lastIndex = 0;
    for (const [start, end] of merged) {
      if (start > lastIndex) {
        segments.push({
          text: text.slice(lastIndex, start),
          match: false,
        });
      }
      segments.push({
        text: text.slice(start, end),
        match: true,
      });
      lastIndex = end;
    }
    if (lastIndex < text.length) {
      segments.push({
        text: text.slice(lastIndex),
        match: false,
      });
    }

    return segments;
  }, [text, query]);

  if (!query || !query.trim()) {
    return <span className={className}>{text}</span>;
  }

  return (
    <span className={className}>
      {parts.map((part, index) =>
        part.match ? (
          <mark key={index} className={matchClassName}>
            {part.text}
          </mark>
        ) : (
          <React.Fragment key={index}>{part.text}</React.Fragment>
        )
      )}
    </span>
  );
}
