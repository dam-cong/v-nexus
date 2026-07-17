"""Domain Adapter cho V-Nexus Tutor — Adaptive English Tutoring (VAIC 2026).

Thay thế placeholder SME cũ. Cung cấp system_prompt (trợ lý giáo dục) và 4 tool cốt lõi
theo docs/ai-danh-gia.md §5: chẩn đoán lỗ hổng (BKT), sinh kế hoạch đào tạo, tổng hợp
cho giáo viên, tổng hợp cho phụ huynh. Không cần sửa agent/, tools/registry.py, mcp_server/,
hay gateway/ — PlannerAgent tự đăng ký các tool trả về đây.
"""
from domain.adapter import DomainAdapter
from tools.base import Tool
from tools.assess_tool import assess_tool
from tools.plan_tool import plan_tool
from tools.teacher_summary_tool import teacher_summary_tool
from tools.parent_summary_tool import parent_summary_tool


class VNexusTutorAdapter(DomainAdapter):
    def system_prompt(self) -> str:
        return (
            "Bạn là Medi Bee, trợ lý AI giáo dục của V-Nexus Tutor — nền tảng tiếng Anh thích "
            "ứng cho học sinh tiểu học. Hệ thống dùng BKT Engine (không phải LLM) để chẩn đoán "
            "lỗ hổng kiến thức một cách minh bạch. Khi cần chẩn đoán, hãy gọi tool "
            "diagnose_knowledge_gaps. Khi cần kế hoạch đào tạo, gọi generate_training_plan.\n"
            "QUY TẮC BẮT BUỘC: chỉ được diễn giải những gì BKT Engine và dữ liệu thực tế trả "
            "về. TUYỆT ĐỐI không tự suy diễn hay thêm lỗ hổng kiến thức không có trong kết quả "
            "tính toán. Trả lời bằng tiếng Việt, thân thiện, khích lệ học sinh."
        )

    def tools(self) -> list[Tool]:
        return [assess_tool, plan_tool, teacher_summary_tool, parent_summary_tool]
