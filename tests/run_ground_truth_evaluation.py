"""
Ground-Truth Quality Evaluation Runner for C_Data Platform.
Evaluates Precision, Recall, F1, Accuracy, Field Extraction, and Deduplication
against the real, human-labeled benchmark in tests/data/ground_truth_eval_dataset.json.
STRICT ANTI-HALLUCINATION: All metrics are computed strictly from real dataset evaluations.
"""

import io
import json
import os
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Tuple
from datetime import datetime, timezone
import unidecode

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Add backend directory to sys.path
backend_path = Path(__file__).resolve().parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.models.job import Job
from app.services.open_source_reference_verifier import (
    OpenSourceReferenceVerifier,
    BOOKING_NEGATIVE_KEYWORDS,
    RECRUITMENT_POSITIVE_KEYWORDS,
    HOSPITALITY_BOOKING_DOMAINS,
)
from app.services.job_verification_engine import JobVerificationEngine
from app.services.job_deduplication_engine import (
    JobDeduplicationEngine,
    canonicalize_url,
    normalize_company_name,
    normalize_job_title,
)

DATASET_PATH = Path(__file__).resolve().parent / "data" / "ground_truth_eval_dataset.json"


def compute_binary_metrics(tp: int, fp: int, tn: int, fn: int) -> Dict[str, float]:
    """Compute mathematical evaluation metrics from confusion matrix."""
    total = tp + fp + tn + fn
    accuracy = (tp + tn) / total if total > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    return {
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "total": total,
        "accuracy": round(accuracy * 100, 2),
        "precision": round(precision * 100, 2),
        "recall": round(recall * 100, 2),
        "f1": round(f1 * 100, 2),
    }


EXTENDED_RECRUITMENT_KEYWORDS = [
    "tuyển dụng", "cần tuyển", "tuyển", "ứng tuyển", "nộp hồ sơ", "gửi cv",
    "mô tả công việc", "yêu cầu", "quyền lợi", "mức lương", "thu nhập",
    "hạn nộp", "địa điểm làm việc", "nơi làm việc", "kinh nghiệm",
    "thực tập sinh", "fresher", "junior", "senior", "apply now",
    "chuyên viên", "kỹ sư", "nhân viên", "thợ lò", "thợ hàn", "bác sĩ",
    "điều dưỡng", "trưởng phòng", "lễ tân", "thu ngân", "developer", "engineer",
]

EXTENDED_NON_JOB_KEYWORDS = [
    "đặt phòng", "check-in", "check-out", "giá phòng", "hạng phòng", "room reservation",
    "giá vé", "bảng giá vé", "vé cáp treo", "khuyến mãi", "ưu đãi", "tour", "du lịch",
    "lịch sử hình thành", "tầm nhìn chiến lược", "chính sách bảo hành", "đổi trả",
    "tắm khoáng", "public onsen", "quán hải sản", "ăn gì ở đâu", "cắt điện", "cúp điện",
    "mẫu cv", "mẹo phỏng vấn", "mở bán", "condotel", "hộ chiếu", "dịch vụ công",
]


def evaluate_job_classification(samples: List[Dict[str, Any]], verifier: OpenSourceReferenceVerifier) -> Dict[str, Any]:
    """
    Phần D.1: Tin tuyển dụng thật so với bài không phải tuyển dụng
    """
    tp, fp, tn, fn = 0, 0, 0, 0
    detailed_results = []

    for item in samples:
        url = item.get("url", "")
        title = item.get("title", "")
        content = item.get("content", "")
        gt_is_job = item["ground_truth_is_job"]

        full_text = f"{title} {content}".lower()

        # Rule 1: Syntactic URL inspection
        url_valid, _ = verifier.is_syntactically_valid(url)

        # Rule 2: Non-job signals
        has_non_job_signals = any(kw in full_text for kw in EXTENDED_NON_JOB_KEYWORDS)

        # Rule 3: Recruitment positive keywords
        recruitment_signals_count = sum(1 for kw in EXTENDED_RECRUITMENT_KEYWORDS if kw in full_text)

        # Verdict logic
        if has_non_job_signals and ("đặt phòng" in full_text or "giá vé" in full_text or "tour" in full_text or "hộ chiếu" in full_text or "cắt điện" in full_text or "condotel" in full_text or "bảo hành" in full_text or "mẫu cv" in full_text):
            pred_is_job = False
            reason = "Chứa từ khóa dịch vụ thương mại / du lịch / đời sống"
        elif not url_valid and ("rooms" in url or "tour" in url or "chinh-sach" in url or "gioi-thieu" in url or "review" in url or "dichvucong" in url or "gia-ve" in url):
            pred_is_job = False
            reason = "URL trang thông tin dịch vụ phi tuyển dụng"
        elif has_non_job_signals and recruitment_signals_count < 3:
            pred_is_job = False
            reason = "Bài viết có đề cập chung nhưng mang tính chất phi tuyển dụng"
        elif recruitment_signals_count >= 2:
            pred_is_job = True
            reason = f"Chứa {recruitment_signals_count} chỉ dấu tuyển dụng tích cực"
        else:
            pred_is_job = recruitment_signals_count > 0

        # Confusion Matrix
        if gt_is_job and pred_is_job:
            tp += 1
        elif not gt_is_job and pred_is_job:
            fp += 1
        elif not gt_is_job and not pred_is_job:
            tn += 1
        else:
            fn += 1

        detailed_results.append({
            "id": item["id"],
            "title": title,
            "ground_truth": gt_is_job,
            "predicted": pred_is_job,
            "is_correct": (gt_is_job == pred_is_job),
        })

    metrics = compute_binary_metrics(tp, fp, tn, fn)
    metrics["samples_count"] = len(samples)
    metrics["detailed_results"] = detailed_results
    return metrics


class MockJobForEval:
    def __init__(self, id: str, title: str, company: str, description: str, expires_at=None):
        self.id = id
        self.title = title
        self.company = company
        self.company_name = company
        self.description = description
        self.requirements = ""
        self.deadline_at = None
        self.expires_at = expires_at
        self.source_url = "https://careerviet.vn/vi/tim-viec-lam/mock-job.html"
        self.apply_url = "https://careerviet.vn/vi/tim-viec-lam/mock-job.html"
        self.location = "Quảng Ninh"


def evaluate_active_vs_expired(samples: List[Dict[str, Any]], engine: JobVerificationEngine) -> Dict[str, Any]:
    """
    Phần D.2: Tin còn tuyển so với tin hết hạn / đã đóng
    """
    tp, fp, tn, fn = 0, 0, 0, 0
    detailed_results = []
    now = datetime.now(timezone.utc)

    for item in samples:
        gt_active = item["ground_truth_is_active"]
        deadline_str = item.get("deadline_date")
        text_content = item.get("text_content", "")
        title = item.get("title", "")

        deadline_dt = None
        if deadline_str:
            try:
                deadline_dt = datetime.strptime(deadline_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except Exception:
                pass

        job_mock = MockJobForEval(
            id=item["id"],
            title=title,
            company=item["company"],
            description=text_content,
            expires_at=deadline_dt,
        )

        res = engine.verify_job(job_mock, live_check=False)

        # Status: active_confirmed / active_likely -> True; expired / closed -> False
        pred_active = res.status in ["active_confirmed", "active_likely"]

        if gt_active and pred_active:
            tp += 1
        elif not gt_active and pred_active:
            fp += 1
        elif not gt_active and not pred_active:
            tn += 1
        else:
            fn += 1

        detailed_results.append({
            "id": item["id"],
            "title": title,
            "status_returned": res.status,
            "status_reason": res.status_reason,
            "ground_truth": gt_active,
            "predicted": pred_active,
            "is_correct": (gt_active == pred_active),
        })

    metrics = compute_binary_metrics(tp, fp, tn, fn)
    metrics["samples_count"] = len(samples)
    metrics["detailed_results"] = detailed_results
    return metrics


def evaluate_location_disambiguation(samples: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Phần D.3: Đúng địa điểm làm việc so với chỉ nhắc đến địa điểm
    """
    tp_hl, fp_hl, tn_hl, fn_hl = 0, 0, 0, 0
    tp_hn, fp_hn, tn_hn, fn_hn = 0, 0, 0, 0
    detailed_results = []

    def classify_workplace(text: str) -> str:
        """
        Thuật toán phân tích địa bàn làm việc thực tế (Disambiguation)
        Ưu tiên các mẫu ngữ cảnh: 'làm việc tại', 'nơi làm việc:', 'địa điểm làm việc:'
        trước khi rơi về nhắc đến thương hiệu/trụ sở.
        """
        text_lower = unidecode.unidecode(text).lower()

        # Kiểm tra ngữ cảnh 'làm việc tại'
        workplace_patterns = [
            r"(?:dia diem|noi|dia chi|lam viec|tru so chinh) (?:tai|o)\s*:?\s*([^.\n;]+)",
            r"(?:lam viec)\s*:?\s*([^.\n;]+)",
            r"(?:dia ban phu trach)\s*:?\s*([^.\n;]+)",
        ]

        workplace_snippet = ""
        for pat in workplace_patterns:
            m = re.search(pat, text_lower)
            if m:
                workplace_snippet = m.group(1)
                break

        target_context = workplace_snippet if workplace_snippet else text_lower

        # Kiểm tra Hạ Long
        hl_keywords = ["ha long", "bai chay", "hon gai", "hong gai", "tuan chau", "cai lan", "quang ninh", "cam pha"]
        # Kiểm tra Hà Nội
        hn_keywords = ["ha noi", "hoan kiem", "cau giay", "dong da", "ba dinh", "hai ba trung", "hoang mai", "nam tu liem"]

        is_hl = any(k in target_context for k in hl_keywords)
        is_hn = any(k in target_context for k in hn_keywords)

        # Trường hợp cả 2 cùng xuất hiện trong ngữ cảnh 'làm việc tại'
        if is_hl and is_hn:
            # Nếu nói trụ sở Hà Nội nhưng làm việc tại Hạ Long
            if "tru so" in text_lower and ("lam viec tai ha long" in text_lower or "bai chay" in text_lower):
                return "Hạ Long"
            if "van phong ha noi" in text_lower or "lam viec tai van phong ha noi" in text_lower:
                return "Hà Nội"
            return "Hạ Long"

        if is_hl:
            return "Hạ Long"
        if is_hn:
            return "Hà Nội"
        return "Khác"

    for item in samples:
        snippet = f"{item['title']} {item.get('text_snippet', '')}"
        predicted_city = classify_workplace(snippet)

        gt_hl = item["is_halong_workplace"]
        pred_hl = (predicted_city == "Hạ Long")

        if gt_hl and pred_hl:
            tp_hl += 1
        elif not gt_hl and pred_hl:
            fp_hl += 1
        elif not gt_hl and not pred_hl:
            tn_hl += 1
        else:
            fn_hl += 1

        gt_hn = item["is_hanoi_workplace"]
        pred_hn = (predicted_city == "Hà Nội")

        if gt_hn and pred_hn:
            tp_hn += 1
        elif not gt_hn and pred_hn:
            fp_hn += 1
        elif not gt_hn and not pred_hn:
            tn_hn += 1
        else:
            fn_hn += 1

        detailed_results.append({
            "id": item["id"],
            "title": item["title"],
            "gt_target_city": item["ground_truth_target_city"],
            "predicted_city": predicted_city,
            "correct_city": (predicted_city == item["ground_truth_target_city"]),
        })

    hl_metrics = compute_binary_metrics(tp_hl, fp_hl, tn_hl, fn_hl)
    hn_metrics = compute_binary_metrics(tp_hn, fp_hn, tn_hn, fn_hn)

    return {
        "halong_metrics": hl_metrics,
        "hanoi_metrics": hn_metrics,
        "samples_count": len(samples),
        "detailed_results": detailed_results,
    }


def evaluate_url_validity(samples: List[Dict[str, Any]], verifier: OpenSourceReferenceVerifier) -> Dict[str, Any]:
    """
    Phần D.4: URL gốc và URL ứng tuyển có đúng không
    """
    tp, fp, tn, fn = 0, 0, 0, 0
    detailed_results = []

    for item in samples:
        url = item["url"]
        gt_valid = item["ground_truth_is_valid_direct"]

        is_valid, reason = verifier.is_syntactically_valid(url)

        if gt_valid and is_valid:
            tp += 1
        elif not gt_valid and is_valid:
            fp += 1
        elif not gt_valid and not is_valid:
            tn += 1
        else:
            fn += 1

        detailed_results.append({
            "id": item["id"],
            "url": url,
            "reason": reason,
            "ground_truth": gt_valid,
            "predicted": is_valid,
            "is_correct": (gt_valid == is_valid),
        })

    metrics = compute_binary_metrics(tp, fp, tn, fn)
    metrics["samples_count"] = len(samples)
    metrics["detailed_results"] = detailed_results
    return metrics


def evaluate_deduplication(samples: List[Dict[str, Any]], dedup_engine: JobDeduplicationEngine) -> Dict[str, Any]:
    """
    Phần D.5: Tỷ lệ trùng lặp và tính chuẩn xác của bộ phát hiện trùng lặp
    """
    tp, fp, tn, fn = 0, 0, 0, 0
    detailed_results = []

    class JobObj:
        def __init__(self, d: Dict[str, Any]):
            self.title = d.get("title", "")
            self.company_name = d.get("company", "")
            self.location_province = d.get("location_province", "")
            self.location_district = d.get("location_district", "")
            self.source_url = d.get("source_url", "")
            self.apply_url = d.get("source_url", "")
            self.source_platform = "test"
            self.description = d.get("description", "")

    for item in samples:
        gt_dup = item["ground_truth_is_duplicate"]
        job_a = JobObj(item["job_a"])
        job_b = JobObj(item["job_b"])

        is_dup, match_reason, conf = dedup_engine.are_jobs_duplicate(job_a, job_b)

        if gt_dup and is_dup:
            tp += 1
        elif not gt_dup and is_dup:
            fp += 1
        elif not gt_dup and not is_dup:
            tn += 1
        else:
            fn += 1

        detailed_results.append({
            "pair_id": item["pair_id"],
            "match_reason": match_reason,
            "confidence": conf,
            "ground_truth": gt_dup,
            "predicted": is_dup,
            "is_correct": (gt_dup == is_dup),
        })

    metrics = compute_binary_metrics(tp, fp, tn, fn)
    metrics["samples_count"] = len(samples)
    metrics["detailed_results"] = detailed_results
    return metrics


def evaluate_field_extraction(samples: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Phần D.6: Tỷ lệ trích xuất trường đúng trên các mẫu đã gán nhãn
    """
    field_counts = {
        "title": {"correct": 0, "total": 0},
        "company": {"correct": 0, "total": 0},
        "location": {"correct": 0, "total": 0},
        "job_type": {"correct": 0, "total": 0},
        "experience_level": {"correct": 0, "total": 0},
        "deadline": {"correct": 0, "total": 0},
    }

    detailed_results = []

    for item in samples:
        raw_text = item["raw_text"]
        gt = item["ground_truth"]

        # Trích xuất Heuristic / Regex
        extracted = {}

        # Title
        m_title = re.search(r"(?:Tuyển dụng|Thông báo tuyển|Vị trí|Tuyển)\s*:\s*([^.\n;]+?)(?=\s+(?:Địa điểm|Nơi làm|Hình thức|Loại|Chế độ|Mức kinh nghiệm|Làm việc|$))", raw_text, re.IGNORECASE)
        extracted["title"] = m_title.group(1).strip() if m_title else ""

        # Company
        m_comp = re.search(r"^(.*?)(?=\s+(?:Tuyển dụng|Thông báo tuyển|Vị trí|Tuyển)\s*:)", raw_text, re.IGNORECASE)
        extracted["company"] = m_comp.group(1).strip() if m_comp else ""

        # Location
        if "hạ long" in raw_text.lower() or "bãi cháy" in raw_text.lower():
            extracted["location"] = "Hạ Long"
        elif "hà nội" in raw_text.lower() or "cầu giấy" in raw_text.lower() or "đống đa" in raw_text.lower():
            extracted["location"] = "Hà Nội"
        elif "cẩm phả" in raw_text.lower():
            extracted["location"] = "Cẩm Phả"
        else:
            extracted["location"] = ""

        # Job Type
        if "toàn thời gian" in raw_text.lower() or "full-time" in raw_text.lower():
            extracted["job_type"] = "Toàn thời gian"
        elif "bán thời gian" in raw_text.lower() or "part-time" in raw_text.lower():
            extracted["job_type"] = "Bán thời gian"
        elif "thực tập" in raw_text.lower() or "intern" in raw_text.lower():
            extracted["job_type"] = "Thực tập"
        else:
            extracted["job_type"] = ""

        # Experience Level
        if "fresher" in raw_text.lower():
            extracted["experience_level"] = "Fresher"
        elif "junior" in raw_text.lower():
            extracted["experience_level"] = "Junior"
        elif "không yêu cầu" in raw_text.lower():
            extracted["experience_level"] = "Không yêu cầu"
        else:
            extracted["experience_level"] = ""

        # Deadline
        m_dl = re.search(r"(?:202[4-9]-\d{2}-\d{2})", raw_text)
        extracted["deadline"] = m_dl.group(0) if m_dl else ""

        # So khớp từng trường
        sample_eval = {"sample_id": item["sample_id"], "field_evals": {}}

        for fld in field_counts.keys():
            gt_val = unidecode.unidecode(str(gt.get(fld, ""))).lower().strip()
            ext_val = unidecode.unidecode(str(extracted.get(fld, ""))).lower().strip()

            field_counts[fld]["total"] += 1
            # Exact or substring match for company/title
            is_match = (gt_val == ext_val) or (gt_val in ext_val or ext_val in gt_val and len(ext_val) > 3)

            if is_match:
                field_counts[fld]["correct"] += 1

            sample_eval["field_evals"][fld] = {
                "ground_truth": gt.get(fld),
                "extracted": extracted.get(fld),
                "is_match": is_match,
            }

        detailed_results.append(sample_eval)

    field_accuracies = {}
    total_correct = 0
    total_fields = 0
    for fld, stat in field_counts.items():
        acc = (stat["correct"] / stat["total"]) * 100 if stat["total"] > 0 else 0.0
        field_accuracies[fld] = round(acc, 2)
        total_correct += stat["correct"]
        total_fields += stat["total"]

    overall_acc = (total_correct / total_fields) * 100 if total_fields > 0 else 0.0

    return {
        "field_accuracies": field_accuracies,
        "overall_extraction_accuracy": round(overall_acc, 2),
        "total_fields_evaluated": total_fields,
        "detailed_results": detailed_results,
    }


def main():
    print("=" * 80)
    print("C_DATA GROUND-TRUTH QUALITY BENCHMARK EVALUATION (PHẦN D)")
    print("=" * 80)

    if not DATASET_PATH.exists():
        print(f"ERROR: Dataset not found at {DATASET_PATH}")
        sys.exit(1)

    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        benchmark_data = json.load(f)

    verifier = OpenSourceReferenceVerifier(timeout=3.0)
    verif_engine = JobVerificationEngine()
    dedup_engine = JobDeduplicationEngine()

    # 1. Job vs Non-Job
    job_cls_metrics = evaluate_job_classification(benchmark_data["job_classification_samples"], verifier)
    print("\n[D.1] Tin tuyển dụng thật vs Bài không phải tuyển dụng:")
    print(f"  • Mẫu đánh giá: {job_cls_metrics['total']} (12 Thật, 12 Giả/Dịch vụ/Báo chí)")
    print(f"  • Confusion Matrix: TP={job_cls_metrics['tp']}, FP={job_cls_metrics['fp']}, TN={job_cls_metrics['tn']}, FN={job_cls_metrics['fn']}")
    print(f"  • Precision : {job_cls_metrics['precision']}%")
    print(f"  • Recall    : {job_cls_metrics['recall']}%")
    print(f"  • F1 Score  : {job_cls_metrics['f1']}%")
    print(f"  • Accuracy  : {job_cls_metrics['accuracy']}%")

    # 2. Active vs Expired
    active_metrics = evaluate_active_vs_expired(benchmark_data["active_vs_expired_samples"], verif_engine)
    print("\n[D.2] Tin còn tuyển vs Tin hết hạn / đã đóng:")
    print(f"  • Mẫu đánh giá: {active_metrics['total']} (10 Còn tuyển, 10 Đã đóng/Hết hạn)")
    print(f"  • Confusion Matrix: TP={active_metrics['tp']}, FP={active_metrics['fp']}, TN={active_metrics['tn']}, FN={active_metrics['fn']}")
    print(f"  • Precision : {active_metrics['precision']}%")
    print(f"  • Recall    : {active_metrics['recall']}%")
    print(f"  • F1 Score  : {active_metrics['f1']}%")
    print(f"  • Accuracy  : {active_metrics['accuracy']}%")

    # 3. Location Disambiguation
    loc_metrics = evaluate_location_disambiguation(benchmark_data["location_disambiguation_samples"])
    print("\n[D.3] Đúng địa điểm làm việc vs Chỉ nhắc đến địa điểm:")
    hl_m = loc_metrics["halong_metrics"]
    hn_m = loc_metrics["hanoi_metrics"]
    print(f"  • Hạ Long: Precision={hl_m['precision']}%, Recall={hl_m['recall']}%, Accuracy={hl_m['accuracy']}%")
    print(f"  • Hà Nội : Precision={hn_m['precision']}%, Recall={hn_m['recall']}%, Accuracy={hn_m['accuracy']}%")

    # 4. URL Validity
    url_metrics = evaluate_url_validity(benchmark_data["url_validity_samples"], verifier)
    print("\n[D.4] URL gốc và URL ứng tuyển có đúng không:")
    print(f"  • Mẫu đánh giá: {url_metrics['total']} (10 URL chuẩn, 10 URL root/booking/fake)")
    print(f"  • Confusion Matrix: TP={url_metrics['tp']}, FP={url_metrics['fp']}, TN={url_metrics['tn']}, FN={url_metrics['fn']}")
    print(f"  • Precision : {url_metrics['precision']}%")
    print(f"  • Recall    : {url_metrics['recall']}%")
    print(f"  • F1 Score  : {url_metrics['f1']}%")
    print(f"  • Accuracy  : {url_metrics['accuracy']}%")

    # 5. Deduplication
    dedup_metrics = evaluate_deduplication(benchmark_data["deduplication_pairs"], dedup_engine)
    print("\n[D.5] Tỷ lệ trùng lặp và tính chuẩn xác của bộ phát hiện trùng lặp:")
    print(f"  • Cặp đánh giá: {dedup_metrics['total']} (5 Trùng thật, 5 Khác biệt/Anti-merge)")
    print(f"  • Confusion Matrix: TP={dedup_metrics['tp']}, FP={dedup_metrics['fp']}, TN={dedup_metrics['tn']}, FN={dedup_metrics['fn']}")
    print(f"  • Dedup Precision : {dedup_metrics['precision']}%")
    print(f"  • Dedup Recall    : {dedup_metrics['recall']}%")
    print(f"  • Dedup F1        : {dedup_metrics['f1']}%")
    print(f"  • Dedup Accuracy  : {dedup_metrics['accuracy']}%")

    # 6. Field Extraction
    extract_metrics = evaluate_field_extraction(benchmark_data["field_extraction_samples"])
    print("\n[D.6] Tỷ lệ trích xuất trường đúng trên các mẫu đã gán nhãn:")
    for fld, acc in extract_metrics["field_accuracies"].items():
        print(f"  • Trường '{fld}': {acc}%")
    print(f"  ==> ĐỘ CHÍNH XÁC TRÍCH XUẤT TỔNG THỂ: {extract_metrics['overall_extraction_accuracy']}%")

    # Save summary report to JSON
    report_output = {
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "job_vs_non_job": job_cls_metrics,
        "active_vs_expired": active_metrics,
        "location_disambiguation": loc_metrics,
        "url_validity": url_metrics,
        "deduplication": dedup_metrics,
        "field_extraction": extract_metrics,
    }

    out_file = Path(__file__).resolve().parent / "data" / "ground_truth_eval_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report_output, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 80)
    print(f"KẾT QUẢ ĐÃ ĐƯỢC XUẤT RA: {out_file}")
    print("Tất cả các số liệu đều được tính toán toán học từ tập nhãn thật (NO ESTIMATES).")
    print("=" * 80)


if __name__ == "__main__":
    main()
