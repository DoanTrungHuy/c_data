"use client";

import React, { useState, useMemo } from "react";
import { Job } from "@/types/job";
import {
  ChevronDownIcon,
  ChevronUpIcon,
  SparklesIcon,
  ClipboardDocumentCheckIcon,
  PlayIcon,
  PauseIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  LightBulbIcon,
  ExclamationTriangleIcon,
} from "@heroicons/react/24/outline";

interface InterviewQuestion {
  id: string;
  category: "technical" | "behavioral" | "situational" | "salary";
  categoryLabel: string;
  question: string;
  intent: string;
  starAnswer: {
    situation: string;
    task: string;
    action: string;
    result: string;
  };
  sampleScript: string;
  redFlags: string[];
}

interface InterviewPrepKitProps {
  job: Job;
}

export default function InterviewPrepKit({ job }: InterviewPrepKitProps) {
  const [expandedId, setExpandedId] = useState<string>("q-1");
  const [copiedScriptId, setCopiedScriptId] = useState<string | null>(null);

  // Timer for practice mode
  const [isPracticing, setIsPracticing] = useState(false);
  const [practiceSeconds, setPracticeSeconds] = useState(0);
  const [practiceQuestion, setPracticeQuestion] = useState<string>("");

  React.useEffect(() => {
    let interval: any = null;
    if (isPracticing) {
      interval = setInterval(() => {
        setPracticeSeconds((s) => s + 1);
      }, 1000);
    } else {
      clearInterval(interval);
    }
    return () => clearInterval(interval);
  }, [isPracticing]);

  const questions: InterviewQuestion[] = useMemo(() => {
    const title = job.title || "Ứng viên";
    const company = job.company_name || "Nhà tuyển dụng";
    const techs = job.tech_stack || [];
    const mainTech = techs.length > 0 ? techs[0] : "chuyên môn của bạn";
    const loc = job.location_district || job.location_province || "Quảng Ninh";

    return [
      {
        id: "q-1",
        category: "technical",
        categoryLabel: "Kỹ năng chuyên môn",
        question: `Anh/Chị hãy giới thiệu kinh nghiệm thực tế của mình liên quan đến vị trí ${title}, đặc biệt là với ${mainTech}?`,
        intent: "Đánh giá mức độ tự tin, khả năng hệ thống hóa kinh nghiệm làm việc và sự trùng khớp giữa năng lực thực tế với bản mô tả công việc (JD).",
        starAnswer: {
          situation: `Tóm lược 1-2 dự án hoặc môi trường làm việc gần nhất mà bạn đảm nhiệm nhiệm vụ tương đương với ${title}.`,
          task: `Nêu rõ trách nhiệm chính của bạn: giải quyết bài toán gì hoặc chịu trách nhiệm về chỉ số/kết quả nào.`,
          action: `Kể tên các công cụ, giải pháp (${techs.slice(0, 3).join(", ") || mainTech}) và phương pháp bạn trực tiếp áp dụng để xử lý công việc.`,
          result: `Đưa ra kết quả có con số cụ thể: hoàn thành đúng hạn, giảm thiểu lỗi, tăng hiệu suất hoặc nhận được phản hồi tốt từ cấp trên.`,
        },
        sampleScript: `“Chào Anh/Chị, trong hơn 2 năm qua em tập trung chuyên sâu vào vai trò tương đương ${title}. Gần đây nhất, em phụ trách triển khai và tối ưu các nhiệm vụ liên quan đến ${mainTech}. Ví dụ trong dự án gần nhất, khi hệ thống cần bàn giao gấp, em đã trực tiếp chuẩn hóa quy trình làm việc, giúp đội ngũ tiết kiệm 25% thời gian và bàn giao đúng tiến độ. Em tin kinh nghiệm thực chiến này sẽ giúp em đóng góp ngay lập tức cho mục tiêu của ${company}.”`,
        redFlags: [
          "Nói dài dòng lan man kể lể từ thời đi học mà không tập trung vào kinh nghiệm cốt lõi.",
          "Chỉ nói lý thuyết sách vở mà không nêu được ví dụ công việc cụ thể đã từng làm.",
        ],
      },
      {
        id: "q-2",
        category: "situational",
        categoryLabel: "Xử lý tình huống",
        question: `Khi nhận nhiệm vụ gấp từ quản lý nhưng tài nguyên thiếu hoặc phát sinh sự cố đột xuất tại địa bàn ${loc}, bạn xử lý thế nào?`,
        intent: "Kiểm tra kỹ năng quản lý thời gian, tư duy ưu tiên công việc (Prioritization) và khả năng giữ bình tĩnh trước áp lực cao.",
        starAnswer: {
          situation: "Xác định sự cố phát sinh bất ngờ đòi hỏi phản ứng ngay.",
          task: "Cần đảm bảo công việc không bị gián đoạn và khách hàng/hệ thống không bị ảnh hưởng.",
          action: "Phân loại mức độ khẩn cấp (P1/P2), trao đổi ngay với quản lý để thống nhất mức độ ưu tiên, chủ động đề xuất giải pháp thay thế tạm thời.",
          result: "Khắc phục sự cố trong thời gian cam kết, sau đó làm báo cáo rút kinh nghiệm (Post-mortem) để không lặp lại.",
        },
        sampleScript: `“Khi gặp tình huống gấp, nguyên tắc đầu tiên của em là không hoảng loạn. Em sẽ đánh giá nhanh tác động: việc nào ảnh hưởng trực tiếp đến vận hành của ${company} sẽ được xử lý trước. Tiếp theo, em báo cáo ngắn gọn cho quản lý hiện trạng kèm 2 phương án giải quyết để xin ý kiến chỉ đạo, thay vì chỉ mang vấn đề đến cho sếp. Sau khi xử lý xong, em luôn ghi chép lại tài liệu để đội ngũ có thể ứng phó nếu tình huống tái diễn.”`,
        redFlags: [
          "Tự ý quyết định những việc vượt thẩm quyền gây hậu quả lớn.",
          "Im lặng tự xử lý không báo cáo để đến khi vỡ tiến độ mới thông báo.",
        ],
      },
      {
        id: "q-3",
        category: "behavioral",
        categoryLabel: "Hành vi & Làm việc nhóm (STAR)",
        question: `Hãy kể về một lần bạn có bất đồng quan điểm với đồng nghiệp hoặc khách hàng và cách bạn giải quyết?`,
        intent: "Đánh giá trí tuệ cảm xúc (EQ), sự lắng nghe, thái độ cầu thị và văn hóa hợp tác nội bộ.",
        starAnswer: {
          situation: "Có sự khác biệt về giải pháp triển khai giữa bạn và đồng nghiệp.",
          task: "Cần tìm ra phương án tối ưu nhất phục vụ mục tiêu chung mà không làm rạn nứt quan hệ đồng đội.",
          action: "Chủ động hẹn gặp riêng, lắng nghe quan điểm của đối phương trước, dựa trên dữ liệu khách quan để thảo luận.",
          result: "Hai bên thống nhất được giải pháp kết hợp ưu điểm của cả hai, hoàn thành dự án suôn sẻ.",
        },
        sampleScript: `“Trong một dự án trước, em và bạn đồng nghiệp từng bất đồng về cách phân bổ công việc. Thay vì tranh cãi trong buổi họp chung, em đã mời bạn đi uống cà phê để cùng ngồi lại phân tích số liệu thực tế. Khi cả hai nhận thấy mục tiêu cao nhất là chất lượng sản phẩm bàn giao, chúng em đã nhanh chóng thống nhất được tiếng nói chung. Qua lần đó, em học được rằng việc lắng nghe trước khi bảo vệ ý kiến cá nhân là chìa khóa của làm việc nhóm hiệu quả.”`,
        redFlags: [
          "Đổ lỗi hoàn toàn cho đồng nghiệp hoặc nói xấu công ty cũ.",
          "Khẳng định mình 'chưa bao giờ bất đồng với ai' (thiếu tính chân thực).",
        ],
      },
      {
        id: "q-4",
        category: "salary",
        categoryLabel: "Đàm phán đãi ngộ",
        question: `Mức lương kỳ vọng của bạn cho vị trí ${title} tại ${company} là bao nhiêu?`,
        intent: "Xem bạn có hiểu đúng giá trị thị trường của bản thân hay không và sự linh hoạt trong đàm phán gói đãi ngộ tổng thể (Total Compensation).",
        starAnswer: {
          situation: "Nhà tuyển dụng muốn biết ngân sách có phù hợp với kỳ vọng của bạn không.",
          task: "Đưa ra khoảng lương thực tế dựa trên khảo sát thị trường tại địa bàn.",
          action: "Đưa ra khoảng lương linh hoạt (Range), nhấn mạnh sự quan tâm tới cơ hội phát triển lâu dài và môi trường làm việc.",
          result: "Tạo ấn tượng chuyên nghiệp, sẵn sàng thương lượng dựa trên trách nhiệm cụ thể.",
        },
        sampleScript: `“Dựa trên khảo sát thị trường vị trí ${title} tại khu vực ${loc} cũng như các yêu cầu trách nhiệm công việc mà ${company} đang tìm kiếm, em kỳ vọng mức thu nhập gộp trong khoảng ${job.salary_text || "12 - 18 triệu VNĐ/tháng"}. Tuy nhiên, em coi trọng cơ hội đóng góp lâu dài và gói quyền lợi tổng thể (thưởng hiệu quả, đào tạo, môi trường). Em rất sẵn lòng lắng nghe mức ngân sách chuẩn của công ty dành cho vị trí này.”`,
        redFlags: [
          "Đưa ra một con số cứng nhắc, không giải thích lý do.",
          "Nói 'sao cũng được, công ty trả bao nhiêu em nhận bấy nhiêu' (thể hiện sự thiếu tự tin).",
        ],
      },
    ];
  }, [job]);

  const copyScript = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedScriptId(id);
    setTimeout(() => setCopiedScriptId(null), 2500);
  };

  const startPractice = (qText: string) => {
    setPracticeQuestion(qText);
    setPracticeSeconds(0);
    setIsPracticing(true);
  };

  const formatTime = (totalSeconds: number) => {
    const mins = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <div className="rounded-2xl sm:rounded-3xl border border-neutral-200 bg-white p-4 sm:p-6 lg:p-8 shadow-xs space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-neutral-200 pb-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl sm:rounded-2xl bg-black text-white text-lg font-black shadow-xs">
            🎯
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base sm:text-xl font-black text-black">
                Bộ Câu Hỏi Phỏng Vấn & Gợi Ý Trả Lời Chuẩn STAR
              </h2>
              <span className="text-[10px] bg-neutral-100 text-black border border-neutral-300 font-bold px-2 py-0.5 rounded-full uppercase">
                AI Kit
              </span>
            </div>
            <p className="text-xs text-neutral-600 mt-0.5">
              Được thiết kế riêng theo vị trí <strong>{job.title}</strong> tại <strong>{job.company_name}</strong>
            </p>
          </div>
        </div>

        {/* Practice Mode Toggle */}
        <div className="flex items-center gap-2 self-start sm:self-auto">
          {isPracticing ? (
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-neutral-100 border border-neutral-300 text-xs font-mono font-bold text-black animate-pulse">
              <span className="h-2 w-2 rounded-full bg-red-600 animate-ping inline-block" />
              <span>Đang bấm giờ: {formatTime(practiceSeconds)}</span>
              <button
                type="button"
                onClick={() => setIsPracticing(false)}
                className="ml-2 text-neutral-500 hover:text-black font-sans font-bold text-xs"
              >
                Dừng
              </button>
            </div>
          ) : (
            <button
              type="button"
              onClick={() => startPractice(questions[0].question)}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-neutral-100 hover:bg-neutral-200 border border-neutral-300 text-black font-bold text-xs transition-colors cursor-pointer shadow-xs active:scale-95"
            >
              <PlayIcon className="h-3.5 w-3.5 text-black" />
              <span>Bật chế độ tự luyện nói</span>
            </button>
          )}
        </div>
      </div>

      {/* Practice Timer Notice Bar */}
      {isPracticing && (
        <div className="p-3.5 rounded-2xl bg-neutral-50 border border-neutral-300 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
          <div>
            <span className="font-bold text-black">Câu hỏi đang luyện: </span>
            <span className="text-neutral-700 font-medium italic">"{practiceQuestion}"</span>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <span className="text-neutral-500 text-[11px]">Mục tiêu: 90 - 120 giây</span>
            <button
              type="button"
              onClick={() => setPracticeSeconds(0)}
              className="text-black hover:underline font-bold text-xs inline-flex items-center gap-1 cursor-pointer"
            >
              <ArrowPathIcon className="h-3 w-3" />
              Đặt lại giờ
            </button>
          </div>
        </div>
      )}

      {/* Questions Accordion List */}
      <div className="space-y-3">
        {questions.map((item, index) => {
          const isExpanded = expandedId === item.id;
          return (
            <div
              key={item.id}
              className={`rounded-2xl border transition-all duration-200 overflow-hidden ${
                isExpanded
                  ? "border-black bg-white shadow-xs"
                  : "border-neutral-200 bg-neutral-50 hover:border-neutral-300"
              }`}
            >
              {/* Question Header */}
              <button
                type="button"
                onClick={() => setExpandedId(isExpanded ? "" : item.id)}
                className="w-full p-4 sm:p-5 flex items-start justify-between gap-3 text-left cursor-pointer"
              >
                <div className="flex items-start gap-3">
                  <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-black text-[11px] font-black text-white mt-0.5">
                    {index + 1}
                  </span>
                  <div className="space-y-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-neutral-500 bg-neutral-200 px-2 py-0.5 rounded-md">
                        {item.categoryLabel}
                      </span>
                    </div>
                    <h3 className="text-xs sm:text-sm font-bold text-black leading-snug">
                      {item.question}
                    </h3>
                  </div>
                </div>

                <div className="shrink-0 text-neutral-400 mt-1">
                  {isExpanded ? (
                    <ChevronUpIcon className="h-4 w-4 text-black" />
                  ) : (
                    <ChevronDownIcon className="h-4 w-4" />
                  )}
                </div>
              </button>

              {/* Accordion Body */}
              {isExpanded && (
                <div className="px-4 sm:px-5 pb-5 pt-1 space-y-4 border-t border-neutral-100 text-xs">
                  {/* Recruiter's True Intent */}
                  <div className="p-3.5 rounded-xl bg-neutral-50 border border-neutral-200 space-y-1">
                    <div className="flex items-center gap-1.5 font-bold text-black text-xs">
                      <LightBulbIcon className="h-4 w-4 text-black" />
                      <span>Ý đồ thực sự của nhà tuyển dụng:</span>
                    </div>
                    <p className="text-neutral-600 leading-relaxed text-[11px] pl-5.5">
                      {item.intent}
                    </p>
                  </div>

                  {/* STAR Method Breakdown */}
                  <div className="space-y-2">
                    <h4 className="font-black text-black text-xs uppercase tracking-wider">
                      Cấu trúc câu trả lời chuẩn mô hình STAR:
                    </h4>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px]">
                      <div className="p-3 rounded-xl bg-white border border-neutral-200 space-y-1">
                        <span className="font-black text-black block">S - Situation (Bối cảnh):</span>
                        <p className="text-neutral-600 leading-relaxed">{item.starAnswer.situation}</p>
                      </div>
                      <div className="p-3 rounded-xl bg-white border border-neutral-200 space-y-1">
                        <span className="font-black text-black block">T - Task (Nhiệm vụ):</span>
                        <p className="text-neutral-600 leading-relaxed">{item.starAnswer.task}</p>
                      </div>
                      <div className="p-3 rounded-xl bg-white border border-neutral-200 space-y-1">
                        <span className="font-black text-black block">A - Action (Hành động):</span>
                        <p className="text-neutral-600 leading-relaxed">{item.starAnswer.action}</p>
                      </div>
                      <div className="p-3 rounded-xl bg-white border border-neutral-200 space-y-1">
                        <span className="font-black text-black block">R - Result (Kết quả):</span>
                        <p className="text-neutral-600 leading-relaxed">{item.starAnswer.result}</p>
                      </div>
                    </div>
                  </div>

                  {/* Sample Answer Script */}
                  <div className="p-4 rounded-xl sm:rounded-2xl bg-neutral-100 border border-neutral-300 space-y-2.5">
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-black text-xs flex items-center gap-1.5">
                        <SparklesIcon className="h-4 w-4 text-black" />
                        Lời thoại mẫu đề xuất (Nói trong 60 - 90s):
                      </span>
                      <button
                        type="button"
                        onClick={() => copyScript(item.id, item.sampleScript)}
                        className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-white hover:bg-neutral-200 text-black font-bold text-[10px] border border-neutral-300 transition-colors shadow-2xs cursor-pointer active:scale-95"
                      >
                        {copiedScriptId === item.id ? (
                          <>
                            <CheckCircleIcon className="h-3 w-3 text-black" />
                            <span>Đã sao chép!</span>
                          </>
                        ) : (
                          <>
                            <ClipboardDocumentCheckIcon className="h-3 w-3" />
                            <span>Sao chép mẫu</span>
                          </>
                        )}
                      </button>
                    </div>
                    <p className="italic text-neutral-800 text-[11px] sm:text-xs leading-relaxed bg-white p-3 rounded-xl border border-neutral-200">
                      {item.sampleScript}
                    </p>
                  </div>

                  {/* Red Flags to Avoid */}
                  <div className="p-3.5 rounded-xl bg-white border border-neutral-200 space-y-1.5">
                    <div className="flex items-center gap-1.5 font-bold text-black text-xs">
                      <ExclamationTriangleIcon className="h-4 w-4 text-black" />
                      <span>Các lỗi tối kỵ (Red Flags) cần tránh:</span>
                    </div>
                    <ul className="list-disc list-inside space-y-1 text-[11px] text-neutral-600 pl-1">
                      {item.redFlags.map((flag, idx) => (
                        <li key={idx}>{flag}</li>
                      ))}
                    </ul>
                  </div>

                  {/* Action row */}
                  <div className="flex items-center justify-end gap-2 pt-1">
                    <button
                      type="button"
                      onClick={() => startPractice(item.question)}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-black hover:bg-neutral-800 text-white font-bold text-xs transition-colors cursor-pointer shadow-xs active:scale-95"
                    >
                      <PlayIcon className="h-3 w-3" />
                      <span>Luyện trả lời câu này</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
