"""Input Extractor — LLM trích xuất có cấu trúc từ dữ liệu thô.

- Curriculum text → skill graph JSON
- Student text → structured profile (dùng cho BKT prior)

Sử dụng OpenAI-compatible API (FPT AI Inference).
"""
from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

_model: str | None = None


def set_model(model: str) -> None:
    global _model
    _model = model


def _get_model() -> str:
    return _model or os.environ.get("LLM_MODEL", "GLM-5.2")


@dataclass
class ExtractedSkill:
    id: str
    code_gdpt: str
    name_vi: str
    name_en: str
    grade: int
    unit: str
    skill_type: str
    prerequisites: list[str] = field(default_factory=list)


@dataclass
class ExtractedStudentProfile:
    student_id: str
    grade: int
    years_studying: int
    self_assessment: str
    environment: str
    target_level: str


def extract_skills_from_text(
    text: str, subject: str = "Tiếng Anh", grade_range: tuple[int, int] = (3, 4),
) -> list[ExtractedSkill]:
    system_prompt = (
        "Bạn là chuyên gia giáo dục. Trích xuất danh sách kỹ năng từ "
        "chương trình học được cung cấp. Trả về JSON array.\n\n"
        "Format yêu cầu:\n"
        '```json\n[{"id": "as3.u1.l3", "code_gdpt": "", '
        '"name_vi": "Tên kỹ năng", "name_en": "Skill name", '
        '"grade": 3, "unit": "Unit 1", "skill_type": "grammar", '
        '"prerequisites": []}]\n```\n'
        "Rules:\n"
        "- id: as{grade}.u{unit}.l{lesson}\n"
        "- prerequisites: list các id kỹ năng tiên quyết\n"
        "- Chỉ trả về JSON array, không giải thích"
    )

    user_msg = f"Trích xuất kỹ năng cho môn {subject}, lớp {grade_range[0]}-{grade_range[1]}:\n\n{text[:8000]}"

    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=os.environ.get("API_KEY", ""),
            base_url=os.environ.get("LLM_BASE_URL", "https://mkp-api.fptcloud.com/v1"),
        )
        response = client.chat.completions.create(
            model=_get_model(),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg},
            ],
            max_tokens=8192,
        )
        msg = response.choices[0].message
        content = msg.content or getattr(msg, "reasoning_content", None) or ""

        json_str = content
        if "```json" in content:
            json_str = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            json_str = content.split("```")[1].split("```")[0]

        skills_raw = json.loads(json_str.strip())
        return [
            ExtractedSkill(
                id=s["id"], code_gdpt=s.get("code_gdpt", ""),
                name_vi=s["name_vi"], name_en=s.get("name_en", ""),
                grade=s["grade"], unit=s.get("unit", ""),
                skill_type=s.get("skill_type", "unknown"),
                prerequisites=s.get("prerequisites", []),
            )
            for s in skills_raw
        ]
    except Exception as e:
        logger.warning("LLM extraction failed: %s", e)
        return []


def extract_student_profile(text: str, student_id: str = "unknown") -> ExtractedStudentProfile | None:
    system_prompt = (
        "Bạn là chuyên gia giáo dục. Trích xuất thông tin hồ sơ học viên.\n"
        "Trả về JSON object:\n"
        '```json\n{"student_id": "S001", "grade": 3, "years_studying": 2, '
        '"self_assessment": "trung bình", "environment": "trường tư", '
        '"target_level": "A2"}\n```\n'
        "Rules: years_studying: số năm học. self_assessment: yếu/trung bình/khá/giỏi. "
        "target_level: Pre-A1/A1/A2/B1. Chỉ trả JSON."
    )

    user_msg = f"Học sinh {student_id}:\n\n{text[:4000]}"

    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=os.environ.get("API_KEY", ""),
            base_url=os.environ.get("LLM_BASE_URL", "https://mkp-api.fptcloud.com/v1"),
        )
        response = client.chat.completions.create(
            model=_get_model(),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg},
            ],
            max_tokens=4096,
        )
        msg = response.choices[0].message
        content = msg.content or getattr(msg, "reasoning_content", None) or ""

        json_str = content
        if "```json" in content:
            json_str = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            json_str = content.split("```")[1].split("```")[0]

        data = json.loads(json_str.strip())
        return ExtractedStudentProfile(
            student_id=data.get("student_id", student_id),
            grade=data.get("grade", 3),
            years_studying=data.get("years_studying", 1),
            self_assessment=data.get("self_assessment", "trung bình"),
            environment=data.get("environment", "trường công"),
            target_level=data.get("target_level", "A1"),
        )
    except Exception as e:
        logger.warning("LLM profile extraction failed: %s", e)
        return None


def profile_to_prior(profile: ExtractedStudentProfile) -> dict[str, float]:
    base_map = {"yếu": 0.2, "trung bình": 0.4, "khá": 0.6, "giỏi": 0.8}
    base = base_map.get(profile.self_assessment.lower(), 0.4)
    years_adj = min(profile.years_studying * 0.03, 0.15)
    prior = min(base + years_adj, 0.95)
    return {"p_init_default": prior}
