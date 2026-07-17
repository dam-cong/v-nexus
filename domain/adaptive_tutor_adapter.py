"""Domain Adapter cho V-Nexus Tutor — thay domain/sme_innovation_adapter.py.

Bot hỏi-đáp dùng adapter này để trả lời học sinh/giáo viên/phụ huynh. Chẩn đoán thật
nằm trong domain/bkt.py (Bayesian Knowledge Tracing) — LLM ở đây chỉ chọn tool + diễn
giải kết quả, KHÔNG tự suy đoán gap.
"""
from domain.adapter import DomainAdapter
from tools.adaptive_tutor_tools import (
    diagnose_gap_tool,
    generate_practice_path_tool,
    parent_dashboard_tool,
    teacher_dashboard_tool,
)
from tools.base import Tool


class AdaptiveTutorAdapter(DomainAdapter):
    def system_prompt(self) -> str:
        return (
            "Bạn là trợ lý của V-Nexus Tutor — nền tảng học Tiếng Anh thích ứng cho "
            "học sinh, giáo viên và phụ huynh trường K12.\n\n"
            "QUY TẮC GROUNDING (bắt buộc): mọi câu trả lời về mastery, lỗ hổng kiến "
            "thức, lộ trình luyện tập hay xếp hạng ưu tiên PHẢI dựa trên kết quả tool "
            "trả về. Không tự suy đoán hay bịa dữ liệu nếu tool không đủ thông tin — "
            "khi đó trả lời 'Xin lỗi, tôi chưa có đủ thông tin để trả lời câu này.'\n\n"
            "QUY TẮC TRUY CẬP (bắt buộc): chỉ gọi tool với đúng student_id/class_id/"
            "parent_id của người đang hỏi. Không bao giờ trả lời câu hỏi về dữ liệu "
            "của học sinh khác, kể cả khi được yêu cầu trực tiếp."
        )

    def tools(self) -> list[Tool]:
        return [
            diagnose_gap_tool,
            generate_practice_path_tool,
            teacher_dashboard_tool,
            parent_dashboard_tool,
        ]
