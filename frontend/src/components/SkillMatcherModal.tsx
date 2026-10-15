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
    name: "IT Support Khách sạn 5* / Resort",
    desc: "Opera PMS, WiFi Mesh, Tổng đài VoIP, Camera CCTV, Máy in",
    skills: ["it_support", "lan_wan", "cctv", "hardware", "voip", "hospitality_pms", "shift_work"],
  },
  {
    name: "IT Y tế số & Bệnh viện đa khoa",
    desc: "Phần mềm HIS/LIS, Windows Server, An toàn thông tin, LAN/WAN",
    skills: ["it_support", "lan_wan", "windows_server", "hospital_his", "security", "hardware"],
  },
  {
    name: "SCADA & Tự động hóa Cảng biển / Than",
    desc: "SCADA/PLC, Mạng công nghiệp, Linux, Cơ sở dữ liệu SQL",
    skills: ["lan_wan", "linux", "scada_plc", "database_sql", "shift_work"],
  },
  {
    name: "Quản trị Mạng & Bảo mật doanh nghiệp",
    desc: "Cisco CCNA, Fortinet, Windows Server, Active Directory, Ảo hóa",
    skills: ["lan_wan", "windows_server", "cisco", "virtualization", "security"],
  },
  {
    name: "Lập trình viên Web / Fullstack",
    desc: "React, Next.js, Node.js, Python, SQL, Docker",
    skills: ["frontend_dev", "backend_dev", "database_sql", "devops_docker"],
  },
];

export default function SkillMatcherModal({
  isOpen,
  onClose,
}: SkillMatcherModalProps) {
  const { skills, updateSkills } = useUserSkills();
  const [selected, setSelected] = useState<string[]>(skills);

  // Sync state if modal opens
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
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 overflow-y-auto">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/60 backdrop-blur-xs transition-opacity"
        onClick={onClose}
      />

      {/* Modal Dialog */}
      <div className="relative w-full max-w-3xl rounded-3xl bg-white shadow-2xl border border-neutral-200 p-6 sm:p-8 z-10 space-y-6 max-h-[90vh] overflow-y-auto animate-fadeIn">
        {/* Header */}
        <div className="flex items-start justify-between gap-4 pb-4 border-b border-neutral-200">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-neutral-100 text-black border border-neutral-200">
              <SparklesIcon className="h-6 w-6 text-black" />
            </div>
            <div>
              <h3 className="text-lg sm:text-xl font-black text-black flex items-center gap-2">
                <span>AI So Khớp Hồ Sơ &amp; Kỹ Năng IT</span>
                <span className="text-[10px] bg-neutral-100 text-neutral-800 border border-neutral-300 font-bold px-2 py-0.5 rounded-full uppercase">
                  Thông minh
                </span>
              </h3>
              <p className="text-xs text-neutral-500 mt-0.5">
                Chọn các kỹ năng của bạn để VịnhViệc tự động chấm điểm độ phù hợp (%) trên mọi việc làm Hạ Long.
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1.5 rounded-xl text-neutral-400 hover:text-black hover:bg-neutral-100 transition-colors"
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
        </div>

        {/* Quick Presets for Ha Long */}
        <div className="space-y-2.5">
          <label className="text-xs font-bold text-neutral-700 uppercase tracking-wider flex items-center gap-1.5">
            <BriefcaseIcon className="h-4 w-4 text-black" />
            <span>Chọn nhanh theo định hướng vị trí tại Hạ Long:</span>
          </label>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {QUICK_PRESETS.map((p) => {
              const isActive =
                p.skills.length === selected.length &&
                p.skills.every((s) => selected.includes(s));
              return (
                <button
                  key={p.name}
                  type="button"
                  onClick={() => applyPreset(p.skills)}
                  className={`text-left p-3 rounded-xl border text-xs transition-all ${
                    isActive
                      ? "border-black bg-neutral-100 text-black font-bold ring-1 ring-black"
                      : "border-neutral-200 bg-neutral-50 hover:bg-white hover:border-neutral-300 text-neutral-700"
                  }`}
                >
                  <p className="font-bold flex items-center justify-between">
                    <span>{p.name}</span>
                    {isActive && <CheckIcon className="h-3.5 w-3.5 text-black" />}
                  </p>
                  <p className="text-[11px] text-neutral-500 mt-0.5 line-clamp-1">{p.desc}</p>
                </button>
              );
            })}
          </div>
        </div>

        {/* Skill Groups */}
        <div className="space-y-5 pt-2">
          {POPULAR_IT_SKILLS.map((group) => (
            <div key={group.category} className="space-y-2">
              <h4 className="text-xs font-extrabold text-neutral-600 uppercase tracking-wider">
                {group.category}
              </h4>
              <div className="flex flex-wrap gap-2">
                {group.skills.map((skill) => {
                  const isChecked = selected.includes(skill.id);
                  return (
                    <button
                      key={skill.id}
                      type="button"
                      onClick={() => toggleSkill(skill.id)}
                      className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs transition-all font-semibold cursor-pointer ${
                        isChecked
                          ? "bg-black text-white border border-black shadow-xs"
                          : "bg-neutral-100 text-neutral-800 hover:bg-neutral-200 border border-neutral-200"
                      }`}
                    >
                      {isChecked && <CheckIcon className="h-3.5 w-3.5 text-white" />}
                      <span>{skill.name}</span>
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </div>

        {/* Footer Actions */}
        <div className="pt-4 border-t border-neutral-200 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="text-xs text-neutral-600">
            Đã chọn <strong className="text-black font-bold">{selected.length}</strong> kỹ năng hồ sơ
          </div>
          <div className="flex items-center gap-2 w-full sm:w-auto">
            {selected.length > 0 && (
              <button
                type="button"
                onClick={handleClear}
                className="px-4 py-2.5 rounded-xl text-xs font-semibold text-neutral-700 hover:bg-neutral-100 transition-colors"
              >
                Đặt lại
              </button>
            )}
            <button
              type="button"
              onClick={handleSave}
              className="flex-1 sm:flex-initial inline-flex items-center justify-center gap-1.5 px-6 py-2.5 rounded-xl bg-black hover:bg-neutral-800 text-white font-bold text-xs shadow-xs transition-all active:scale-95 cursor-pointer"
            >
              <SparklesIcon className="h-4 w-4 text-white" />
              <span>Lưu &amp; So khớp việc làm ngay</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
