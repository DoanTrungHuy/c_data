"use client";

import React, { useState } from "react";
import {
  XMarkIcon,
  SparklesIcon,
  CheckIcon,
  BriefcaseIcon,
} from "@heroicons/react/24/outline";
import {
  POPULAR_IT_SKILLS,
  useUserSkills,
} from "@/lib/skillMatcher";

interface SkillMatcherModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const QUICK_PRESETS = [
  {
    name: "IT Khách sạn 5*",
    icon: "🏨",
    skills: ["it_support", "lan_wan", "cctv", "hardware", "voip", "hospitality_pms", "shift_work"],
  },
  {
    name: "IT Y tế số",
    icon: "🏥",
    skills: ["it_support", "lan_wan", "windows_server", "hospital_his", "security", "hardware"],
  },
  {
    name: "Cảng & SCADA",
    icon: "⚓",
    skills: ["lan_wan", "linux", "scada_plc", "database_sql", "shift_work"],
  },
  {
    name: "Mạng & Bảo mật",
    icon: "🛡️",
    skills: ["lan_wan", "windows_server", "cisco", "virtualization", "security"],
  },
  {
    name: "Web / Fullstack",
    icon: "💻",
    skills: ["frontend_dev", "backend_dev", "database_sql", "devops_docker"],
  },
];

export default function SkillMatcherModal({
  isOpen,
  onClose,
}: SkillMatcherModalProps) {
  const { skills, updateSkills } = useUserSkills();
  const [selected, setSelected] = useState<string[]>(skills);

  // Sync state when modal opens
  React.useEffect(() => {
    if (isOpen) {
      setSelected(skills);
    }
  }, [isOpen, skills]);

  if (!isOpen) return null;

  const toggleSkill = (id: string) => {
    if (selected.includes(id)) {
      setSelected(selected.filter((s) => s !== id));
    } else {
      setSelected([...selected, id]);
    }
  };

  const applyPreset = (presetSkills: string[]) => {
    setSelected(presetSkills);
  };

  const handleSave = () => {
    updateSkills(selected);
    onClose();
  };

  const handleClear = () => {
    setSelected([]);
    updateSkills([]);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 md:p-6 overflow-hidden">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/60 backdrop-blur-xs transition-opacity"
        onClick={onClose}
      />

      {/* Modal Dialog */}
      <div className="relative w-full max-w-2xl rounded-2xl sm:rounded-3xl bg-white shadow-2xl border border-neutral-200 z-10 flex flex-col max-h-[85vh] overflow-hidden animate-fadeIn">
        {/* Fixed Header */}
        <div className="shrink-0 px-4 sm:px-6 py-3.5 sm:py-4 border-b border-neutral-200 bg-white flex items-center justify-between gap-3">
          <div className="flex items-center gap-2.5 sm:gap-3 min-w-0">
            <div className="flex h-9 w-9 sm:h-10 sm:w-10 shrink-0 items-center justify-center rounded-xl sm:rounded-2xl bg-neutral-100 text-black border border-neutral-200">
              <SparklesIcon className="h-5 w-5 text-black" />
            </div>
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <h3 className="text-base sm:text-lg font-black text-black truncate">
                  AI So Khớp Hồ Sơ &amp; Kỹ Năng IT
                </h3>
                <span className="text-[10px] bg-neutral-100 text-neutral-800 border border-neutral-300 font-bold px-1.5 py-0.5 rounded-md uppercase shrink-0">
                  AI Match
                </span>
              </div>
              <p className="text-xs text-neutral-500 truncate mt-0.5">
                Chọn kỹ năng để tự động chấm điểm độ phù hợp (%) trên mọi việc làm
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="shrink-0 p-1.5 rounded-xl text-neutral-400 hover:text-black hover:bg-neutral-100 transition-colors"
            title="Đóng"
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
        </div>

        {/* Scrollable Content with Slim Scrollbar */}
        <div className="flex-1 overflow-y-auto px-4 sm:px-6 py-4 space-y-4 [scrollbar-width:thin] [&::-webkit-scrollbar]:w-1.5 [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar-thumb]:bg-neutral-300 [&::-webkit-scrollbar-thumb]:rounded-full hover:[&::-webkit-scrollbar-thumb]:bg-neutral-400">
          {/* Quick Presets */}
          <div className="space-y-1.5">
            <label className="text-[11px] font-bold text-neutral-600 uppercase tracking-wider flex items-center gap-1.5">
              <BriefcaseIcon className="h-3.5 w-3.5 text-black" />
              <span>Định hướng vị trí nhanh:</span>
            </label>
            <div className="flex flex-wrap gap-1.5">
              {QUICK_PRESETS.map((p) => {
                const isActive =
                  p.skills.length === selected.length &&
                  p.skills.every((s) => selected.includes(s));
                return (
                  <button
                    key={p.name}
                    type="button"
                    onClick={() => applyPreset(p.skills)}
                    className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                      isActive
                        ? "bg-black text-white shadow-2xs font-bold"
                        : "bg-neutral-100 hover:bg-neutral-200 text-neutral-800 border border-neutral-200"
                    }`}
                  >
                    <span>{p.icon} {p.name}</span>
                    {isActive && <CheckIcon className="h-3 w-3 text-white" />}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Skill Categories in Compact 2-column Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
            {POPULAR_IT_SKILLS.map((group) => (
              <div
                key={group.category}
                className="p-3 rounded-2xl bg-neutral-50/80 border border-neutral-200 space-y-2"
              >
                <h4 className="text-[11px] font-extrabold text-neutral-700 uppercase tracking-wider">
                  {group.category}
                </h4>
                <div className="flex flex-wrap gap-1.5">
                  {group.skills.map((skill) => {
                    const isChecked = selected.includes(skill.id);
                    return (
                      <button
                        key={skill.id}
                        type="button"
                        onClick={() => toggleSkill(skill.id)}
                        className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-medium transition-all cursor-pointer ${
                          isChecked
                            ? "bg-black text-white font-bold shadow-2xs"
                            : "bg-white text-neutral-800 hover:bg-neutral-100 border border-neutral-200 hover:border-neutral-300"
                        }`}
                      >
                        {isChecked && <CheckIcon className="h-3 w-3 text-white shrink-0" />}
                        <span>{skill.name}</span>
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Fixed Footer */}
        <div className="shrink-0 px-4 sm:px-6 py-3.5 border-t border-neutral-200 bg-white flex items-center justify-between gap-3">
          <div className="text-xs text-neutral-600">
            Đã chọn: <strong className="text-black font-bold">{selected.length}</strong> kỹ năng
          </div>
          <div className="flex items-center gap-2">
            {selected.length > 0 && (
              <button
                type="button"
                onClick={handleClear}
                className="px-3 py-1.5 rounded-xl text-xs font-semibold text-neutral-600 hover:text-black hover:bg-neutral-100 transition-colors cursor-pointer"
              >
                Đặt lại
              </button>
            )}
            <button
              type="button"
              onClick={handleSave}
              className="inline-flex items-center justify-center gap-1.5 px-5 py-2 rounded-xl bg-black hover:bg-neutral-800 text-white font-bold text-xs shadow-xs transition-all active:scale-95 cursor-pointer"
            >
              <SparklesIcon className="h-3.5 w-3.5 text-white" />
              <span>Lưu &amp; So khớp việc làm</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
