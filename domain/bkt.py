"""Bayesian Knowledge Tracing (BKT) Engine — Tầng 2 cốt lõi.

Tính xác suất thành thạo từng kỹ năng của học sinh dựa trên lịch sử trả lời,
sau đó truy tìm gốc rễ lỗ hổng qua Knowledge Graph.

Tham số BKT cố định (docs/ai-danh-gia.md §2.1): không tự ước lượng từ dữ liệu
vì bản demo không có đủ dữ liệu. Giá trị này minh bạch và dễ giải thích.
"""
from domain.knowledge_graph import (
    get_prerequisites,
    get_skill_name,
    has_skill,
    trace_root_causes,
)

# Tham số BKT cố định
PRIOR = 0.3        # xác suất đã biết trước khi học
TRANSIT = 0.3      # xác suất học được sau mỗi lượt
GUESS = 0.2        # xác suất đoán đúng dù chưa biết
SLIP = 0.1         # xác suất làm sai dù đã biết

# Ngưỡng đánh giá trạng thái
# Lưu ý: do tham số transit luôn cộng tiến bộ mỗi lượt (kể cả khi sai), xác suất
# sau một chuỗi toàn sai sẽ không xuống dưới ~0.34. Vì vậy ngưỡng "developing"
# đặt ở 0.45 để các kỹ năng học sinh làm sai phần lớn vẫn bị đánh dấu là lỗ hổng.
THRESHOLD_MASTERED = 0.7
THRESHOLD_DEVELOPING = 0.45
ROOT_THRESHOLD = 0.5  # ngưỡng truy tìm gốc rễ


def _status(probability: float) -> str:
    if probability >= THRESHOLD_MASTERED:
        return "mastered"
    if probability >= THRESHOLD_DEVELOPING:
        return "developing"
    return "weak"


def update_probability(prior_p: float, correct: bool) -> float:
    """Cập nhật xác suất thành thạo theo 2 bước (docs §2.2).

    Bước 1: cập nhật theo bằng chứng (đúng/sai).
    Bước 2: cộng tiến bộ tự nhiên qua lượt luyện (transit).
    """
    if correct:
        # P(đúng | biết) = 1 - slip ; P(đúng | không biết) = guess
        num = prior_p * (1 - SLIP)
        den = prior_p * (1 - SLIP) + (1 - prior_p) * GUESS
        posterior = num / den if den > 0 else prior_p
    else:
        # P(sai | biết) = slip ; P(sai | không biết) = 1 - guess
        num = prior_p * SLIP
        den = prior_p * SLIP + (1 - prior_p) * (1 - GUESS)
        posterior = num / den if den > 0 else 0.0

    # Bước 2: tiến bộ tự nhiên
    updated = posterior + (1 - posterior) * TRANSIT
    return max(0.0, min(1.0, updated))


def compute_mastery(answers: list, questions: list = None) -> dict:
    """Tính mastery theo từng skill_id từ danh sách câu trả lời.

    `answers`: list dict có {question_id, correct, skill_id, ...}
    Trả về { skill_id: {probability, correct, total, skill_name, status, is_default} }
    """
    # Khởi tạo xác suất prior cho mỗi skill được đề cập
    mastery = {}
    for a in answers or []:
        sid = a.get("skill_id")
        if sid and sid not in mastery:
            mastery[sid] = {
                "probability": PRIOR,
                "correct": 0,
                "total": 0,
                "skill_name": get_skill_name(sid),
                "status": _status(PRIOR),
                "is_default": True,
            }

    for a in answers or []:
        sid = a.get("skill_id")
        if not sid or sid not in mastery:
            continue
        m = mastery[sid]
        m["is_default"] = False
        m["total"] += 1
        correct = bool(a.get("correct"))
        if correct:
            m["correct"] += 1
        m["probability"] = update_probability(m["probability"], correct)
        m["status"] = _status(m["probability"])

    return mastery


def diagnose_gaps(mastery_map: dict, skill_ids: list = None) -> list:
    """Chẩn đoán lỗ hổng + truy tìm gốc rễ (docs §2.3, §2.4).

    Trả về list các gap:
    {
      skill_id, skill_name, probability, status, severity,
      root_causes: [skill_id...], reason
    }
    """
    gaps = []
    # Mở rộng tập kỹ năng cần xét: các kỹ năng đã làm + toàn bộ tiên quyết truy vết ngược
    # (đệ quy), để cả kỹ năng "gốc" (không có trong bài làm) cũng được chẩn đoán.
    skills_to_check = set(skill_ids or list(mastery_map.keys()))

    def _expand(sid):
        for p in get_prerequisites(sid):
            if p not in skills_to_check:
                skills_to_check.add(p)
                _expand(p)

    for sid in list(skills_to_check):
        _expand(sid)

    for sid in skills_to_check:
        if not has_skill(sid):
            # Kỹ năng không có trong đồ thị -> báo lỗi rõ (§2.4)
            gaps.append({
                "skill_id": sid,
                "skill_name": get_skill_name(sid),
                "probability": mastery_map.get(sid, {}).get("probability"),
                "status": "unknown",
                "severity": "unknown",
                "root_causes": [],
                "reason": f"Kỹ năng '{sid}' không tồn tại trong đồ thị kiến thức — cần bổ sung dữ liệu.",
            })
            continue

        prob = mastery_map.get(sid, {}).get("probability", PRIOR)
        if prob >= THRESHOLD_DEVELOPING:
            continue  # kỹ năng này ổn, không phải lỗ hổng

        roots = trace_root_causes(sid, mastery_map, threshold=ROOT_THRESHOLD)
        severity = "high" if prob < 0.15 else "medium"
        reason = f"Chưa nắm vững {get_skill_name(sid)}"
        if roots:
            root_names = ", ".join(get_skill_name(r) for r in roots)
            reason += f". Gốc rễ: {root_names}."

        gaps.append({
            "skill_id": sid,
            "skill_name": get_skill_name(sid),
            "probability": round(prob, 3),
            "status": _status(prob),
            "severity": severity,
            "root_causes": roots,
            "reason": reason,
        })

    # Sắp xếp: high trước, rồi theo probability tăng dần
    gaps.sort(key=lambda g: (g["severity"] != "high", g.get("probability") or 0))
    return gaps


def run_assessment(answers: list, questions: list = None) -> dict:
    """Hàm tiện ích: chạy toàn bộ Tầng 2, trả về {mastery, gaps}."""
    mastery = compute_mastery(answers, questions)
    gaps = diagnose_gaps(mastery)
    return {"mastery": mastery, "gaps": gaps}


# ---------------------------------------------------------------------------
# Tầng 2.5: Sinh danh sách bước lộ trình CÓ CẤU TRÚC (deterministic, không LLM)
# ---------------------------------------------------------------------------
# Đây là nơi QUANH GỌI nhất: BKT + Knowledge Graph quyết định THỨ TỰ và NỘI DUNG
# từng bước. LLM chỉ nhận output của hàm này và diễn giải thành văn bản tự nhiên.

# Độ khó gợi ý theo mastery
_DIFFICULTY_MAP = {
    "high": "easy",      # gốc rễ yếu nhất -> bắt đầu từ dễ
    "medium": "medium",
}

# Thời lượng gợi ý (phút/buổi) theo severity
_DURATION_MAP = {
    "high": "20 phút",
    "medium": "15 phút",
}


def generate_learning_steps(mastery: dict, gaps: list) -> list:
    """Sinh danh sách bước lộ trình học tập có cấu trúc từ kết quả BKT.

    Trả về list[dict], mỗi dict:
    {
      "step_order": int,           # thứ tự (1-based)
      "skill_id": str,
      "skill_name": str,
      "current_mastery": float,    # probability hiện tại (0-1)
      "status": str,               # weak / developing / mastered
      "severity": str,             # high / medium
      "reason": str,               # tại sao bước này được chọn
      "suggested_difficulty": str, # easy / medium
      "estimated_duration": str,   # "15 phút" / "20 phút"
    }

    Nguyên tắc sắp xếp:
    1. Gốc rễ (root causes) có severity "high" lên trước.
    2. Sau đó đến các kỹ năng "medium" theo thứ tự tiên quyết.
    3. Không thêm kỹ năng ngoài danh sách gaps.
    """
    if not gaps:
        return []

    steps = []
    step_num = 0

    # Bước 1: các gap có severity "high" (gốc rễ)
    for g in gaps:
        if g.get("severity") != "high":
            continue
        step_num += 1
        sid = g.get("skill_id", "")
        prob = g.get("probability") or 0
        steps.append({
            "step_order": step_num,
            "skill_id": sid,
            "skill_name": g.get("skill_name", sid),
            "current_mastery": round(prob, 3),
            "status": g.get("status", _status(prob)),
            "severity": "high",
            "reason": g.get("reason", f"Gốc rễ lỗ hổng — cần ưu tiên ôn trước"),
            "suggested_difficulty": "easy",
            "estimated_duration": _DURATION_MAP["high"],
        })

    # Bước 2: các gap có severity "medium"
    for g in gaps:
        if g.get("severity") != "medium":
            continue
        step_num += 1
        sid = g.get("skill_id", "")
        prob = g.get("probability") or 0
        root_info = ""
        if g.get("root_causes"):
            root_names = [get_skill_name(r) for r in g["root_causes"]]
            root_info = f". Tiên quyết: {', '.join(root_names)}"
        steps.append({
            "step_order": step_num,
            "skill_id": sid,
            "skill_name": g.get("skill_name", sid),
            "current_mastery": round(prob, 3),
            "status": g.get("status", _status(prob)),
            "severity": "medium",
            "reason": g.get("reason", f"Cần củng cố thêm") + root_info,
            "suggested_difficulty": _DIFFICULTY_MAP["medium"],
            "estimated_duration": _DURATION_MAP["medium"],
        })

    return steps


def format_steps_for_llm(steps: list) -> str:
    """Format danh sách bước thành bảng có cấu trúc để truyền vào prompt LLM.

    Đây là INPUT DỮ LIỆU cho LLM — LLM chỉ được diễn giải nội dung này,
    không được thêm/bớt bước hay đổi thứ tự.
    """
    if not steps:
        return "(Không có bước lộ trình — học sinh đã nắm vững tất cả kỹ năng.)"

    lines = [
        "LO TRÌNH HỌC TẬP (dữ liệu từ BKT Engine — KHÔNG được sửa đổi thứ tự hoặc nội dung):",
        "",
        "| # | Kỹ năng | Mastery hiện tại | Mức ưu tiên | Độ khó gợi ý | Thời lượng | Lý do |",
        "|---|---------|-----------------|-------------|--------------|------------|-------|",
    ]
    for s in steps:
        mastery_pct = f"{round(s['current_mastery'] * 100)}%"
        lines.append(
            f"| {s['step_order']} | {s['skill_name']} ({s['skill_id']}) | {mastery_pct} | "
            f"{s['severity']} | {s['suggested_difficulty']} | {s['estimated_duration']} | "
            f"{s['reason']} |"
        )
    return "\n".join(lines)


def get_input_skill_ids(steps: list) -> list:
    """Trích xuất danh sách skill_id từ steps — dùng cho post-validation."""
    return [s["skill_id"] for s in steps]
