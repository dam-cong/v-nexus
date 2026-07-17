"""Tool 1 (quan trọng nhất): Chẩn đoán lỗ hổng kiến thức qua BKT Engine + Knowledge Graph.

Nhận câu trả lời của học sinh, gọi Tầng 2 (BKT) để tính mastery và truy tìm gốc rễ,
trả về danh sách kỹ năng bị hổng kèm mức độ tin cậy và giải thích. LLM KHÔNG tự đoán
lỗ hổng — nó chỉ diễn giải kết quả này (docs/ai-danh-gia.md §5.1).
"""
from domain.bkt import compute_mastery, diagnose_gaps, run_assessment
from tools.base import Tool


def assess_gaps(answers: list, questions: list = None) -> dict:
    """Chạy BKT Engine và trả về {mastery, gaps}."""
    if not answers:
        return {
            "mastery": {},
            "gaps": [],
            "note": "Chưa có dữ liệu câu trả lời — không đủ để chẩn đoán.",
        }
    result = run_assessment(answers, questions)
    return result


assess_tool = Tool(
    name="diagnose_knowledge_gaps",
    description=(
        "Chẩn đoán lỗ hổng kiến thức của học sinh từ kết quả bài làm, dùng BKT Engine "
        "và đồ thị kiến thức. Trả về mastery (xác suất thành thạo từng kỹ năng) và gaps "
        "(danh sách kỹ năng yếu kèm gốc rễ và mức độ tin cậy). CHỈ dùng dữ liệu này, "
        "tuyệt đối không tự suy diễn lỗ hổng khác."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "answers": {
                "type": "array",
                "description": "Danh sách câu trả lời: {question_id, skill_id, correct, ...}",
            },
            "questions": {
                "type": "array",
                "description": "Tùy chọn: danh sách câu hỏi tương ứng.",
            },
        },
        "required": ["answers"],
    },
    func=assess_gaps,
)
