"""Output Interpreter — LLM diễn giải kết quả BKT thành ngôn ngữ tự nhiên.

2 tông giọng:
- Giáo viên: thuật ngữ, heatmap, gợi ý sư phạm
- Phụ huynh: đơn giản, hành động cụ thể tại nhà, KHÔNG so sánh

Sử dụng OpenAI-compatible API (FPT AI Inference).
"""
from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass

logger = logging.getLogger(__name__)

_model: str | None = None


def set_model(model: str) -> None:
    global _model
    _model = model


def _get_model() -> str:
    return _model or os.environ.get("LLM_MODEL", "GLM-5.2")


@dataclass
class InterpretedOutput:
    role: str
    raw_data: dict
    natural_language: str


def _build_teacher_prompt(gaps: list[dict], mastery_map: dict[str, float]) -> str:
    lines = [
        "Bạn là trợ lý giáo dục. Diễn giải kết quả chẩn đoán sau thành "
        "ngôn ngữ tiếng Việt cho **giáo viên**.\n",
        "## Dữ liệu đầu vào\n",
    ]

    if gaps:
        lines.append("### Lỗ hổng kiến thức (gap list)\n")
        for g in gaps:
            lines.append(
                f"- **{g.get('skill_name', g.get('skill_id', '?'))}** "
                f"(mastery: {g.get('mastery_prob', g.get('mastery', 0)) * 100:.0f}%, "
                f"gap_depth: {g.get('gap_depth', '?')}, "
                f"lớp {g.get('grade', '?')})"
            )
        lines.append("")

    alert_skills = [sid for sid, m in mastery_map.items() if m < 0.3]
    if alert_skills:
        lines.append(f"### Kỹ năng cần cảnh báo (mastery < 30%): {', '.join(alert_skills[:5])}\n")

    lines.extend([
        "## Yêu cầu\n",
        "1. Tổng quan lớp: bao nhiêu kỹ năng có gap, bao nhiêu học sinh bị ảnh hưởng",
        "2. Ưu tiên dạy lại: liệt kê kỹ năng cần dạy lại cả lớp, sắp xếp theo mức độ nghiêm trọng",
        "3. Gợi ý nhóm: nhóm học sinh cần hỗ trợ thêm",
        "4. Cảnh báo nếu có kỹ năng >50% học sinh hổng",
        "",
        "## Định dạng trả lời\n",
        "Trả lời bằng markdown, có heading rõ ràng.",
    ])
    return "\n".join(lines)


def _build_parent_prompt(student_id: str, gaps: list[dict], mastery_map: dict[str, float]) -> str:
    mastered = [sid for sid, m in mastery_map.items() if m >= 0.7]
    struggling = [sid for sid, m in mastery_map.items() if m < 0.5]

    lines = [
        "Bạn là trợ lý giáo dục. Diễn giải kết quả sau thành "
        "ngôn ngữ tiếng Việt đơn giản cho **phụ huynh**.\n",
        "## Dữ liệu đầu vào\n",
        f"- Học sinh: {student_id}",
        f"- Số kỹ năng đã nắm vững: {len(mastered)}",
        f"- Số kỹ năng cần hỗ trợ: {len(struggling)}",
    ]

    if gaps:
        lines.append("\n### Kỹ năng cần hỗ trợ\n")
        for g in gaps[:5]:
            lines.append(
                f"- {g.get('skill_name', g.get('skill_id', '?'))} "
                f"(đúng khoảng {g.get('mastery_prob', g.get('mastery', 0)) * 100:.0f}%)"
            )

    lines.extend([
        "",
        "## Yêu cầu QUAN TRỌNG\n",
        "1. KHÔNG dùng thuật ngữ kỹ thuật (mastery, gap, depth...)",
        "2. KHÔNG so sánh với học sinh khác",
        "3. Chỉ nói về tiến độ của riêng con mình",
        "4. Gợi ý 1-2 hành động CỤ THỂ tại nhà",
        "5. Nhấn mạnh tiến bộ, động viên phụ huynh",
        "",
        "## Định dạng trả lời\n",
        "Ngắn gọn, 3-5 câu. Bằng ngôn ngữ đời thường, dễ hiểu.",
    ])
    return "\n".join(lines)


def _call_llm(system: str, user_message: str) -> str:
    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=os.environ.get("API_KEY", ""),
            base_url=os.environ.get("LLM_BASE_URL", "https://mkp-api.fptcloud.com/v1"),
        )
        response = client.chat.completions.create(
            model=_get_model(),
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_message},
            ],
            max_tokens=4096,
        )
        msg = response.choices[0].message
        return msg.content or getattr(msg, "reasoning_content", None) or ""
    except Exception as e:
        logger.warning("LLM call failed: %s — falling back to raw data", e)
        return ""


def interpret_for_teacher(
    gaps: list[dict], mastery_map: dict[str, float], use_llm: bool = True,
) -> InterpretedOutput:
    raw = {
        "gaps": gaps,
        "mastery_summary": {
            "total_skills": len(mastery_map),
            "mastered": sum(1 for m in mastery_map.values() if m >= 0.7),
            "struggling": sum(1 for m in mastery_map.values() if m < 0.5),
        },
        "alerts": [sid for sid, m in mastery_map.items() if m < 0.3],
    }

    if use_llm:
        prompt = _build_teacher_prompt(gaps, mastery_map)
        nl = _call_llm(
            system="Bạn là chuyên gia giáo dục, diễn giải dữ liệu cho giáo viên.",
            user_message=prompt,
        )
        if nl:
            return InterpretedOutput(role="teacher", raw_data=raw, natural_language=nl)

    lines = ["**Tổng quan:**\n"]
    lines.append(f"- Tổng kỹ năng theo dõi: {raw['mastery_summary']['total_skills']}")
    lines.append(f"- Đã nắm vững: {raw['mastery_summary']['mastered']}")
    lines.append(f"- Cần hỗ trợ: {raw['mastery_summary']['struggling']}")
    if raw["alerts"]:
        lines.append(f"\n**Cảnh báo:** {', '.join(raw['alerts'][:5])}")
    if gaps:
        lines.append("\n**Ưu tiên dạy lại:**")
        for i, g in enumerate(gaps[:5], 1):
            name = g.get("skill_name", g.get("skill_id", "?"))
            mastery = g.get("mastery_prob", g.get("mastery", 0)) * 100
            lines.append(f"{i}. {name} (mastery: {mastery:.0f}%)")
    return InterpretedOutput(role="teacher", raw_data=raw, natural_language="\n".join(lines))


def interpret_for_parent(
    student_id: str, gaps: list[dict], mastery_map: dict[str, float], use_llm: bool = True,
) -> InterpretedOutput:
    raw = {
        "student_id": student_id,
        "gaps": gaps,
        "mastery_summary": {
            "total_skills": len(mastery_map),
            "mastered": sum(1 for m in mastery_map.values() if m >= 0.7),
            "struggling": sum(1 for m in mastery_map.values() if m < 0.5),
        },
    }

    if use_llm:
        prompt = _build_parent_prompt(student_id, gaps, mastery_map)
        nl = _call_llm(
            system="Bạn là trợ lý giáo dục, diễn giải dữ liệu cho phụ huynh bằng ngôn ngữ đơn giản.",
            user_message=prompt,
        )
        if nl:
            return InterpretedOutput(role="parent", raw_data=raw, natural_language=nl)

    mastered_count = raw["mastery_summary"]["mastered"]
    struggling_count = raw["mastery_summary"]["struggling"]
    lines = [f"**Tiến độ của con ({student_id}):**\n"]
    if struggling_count == 0:
        lines.append("Con đang học tốt! Các kỹ năng đều đạt yêu cầu.")
    else:
        lines.append(f"Con đã nắm vững {mastered_count} kỹ năng, cần hỗ trợ thêm {struggling_count} kỹ năng.")
        if gaps:
            weakest = gaps[0]
            name = weakest.get("skill_name", weakest.get("skill_id", "?"))
            lines.append(f"\n**Cần hỗ trợ thêm:** {name}")
            lines.append("\n**Gợi ý:** Mỗi ngày 15 phút ôn cùng con bài về kỹ năng này.")
    return InterpretedOutput(role="parent", raw_data=raw, natural_language="\n".join(lines))


def interpret_diagnose_student(gaps: list[dict], use_llm: bool = True) -> InterpretedOutput:
    raw = {"gaps": gaps}

    if gaps:
        prompt_parts = ["Kết quả chẩn đoán cho học sinh:\n"]
        for g in gaps:
            prompt_parts.append(
                f"- {g.get('skill_name', g.get('skill_id', '?'))} "
                f"(mastery: {g.get('mastery_prob', g.get('mastery', 0)) * 100:.0f}%)"
            )
        prompt_parts.extend(["\nDiễn giải thành câu trả lời thân thiện cho học sinh.", "Ngôn ngữ đơn giản, động viên, gợi ý luyện tập."])
        user_msg = "\n".join(prompt_parts)
    else:
        user_msg = "Học sinh trả lời đúng tất cả. Chúc mừng!"

    if use_llm:
        nl = _call_llm(
            system="Bạn là gia sư thân thiện, diễn giải kết quả cho học sinh.",
            user_message=user_msg,
        )
        if nl:
            return InterpretedOutput(role="student", raw_data=raw, natural_language=nl)

    if not gaps:
        return InterpretedOutput(role="student", raw_data=raw, natural_language="Chúc mừng! Em trả lời đúng tất cả!")
    lines = ["Em đã trả lời xong rồi!\n"]
    for g in gaps[:3]:
        name = g.get("skill_name", g.get("skill_id", "?"))
        mastery = g.get("mastery_prob", g.get("mastery", 0)) * 100
        lines.append(f"- Em chưa vững phần **{name}** (đúng khoảng {mastery:.0f}%)")
    lines.append("\nEm có thể luyện tập thêm phần này để giỏi hơn!")
    return InterpretedOutput(role="student", raw_data=raw, natural_language="\n".join(lines))
