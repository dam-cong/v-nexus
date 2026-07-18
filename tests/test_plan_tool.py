import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tools.plan_tool import generate_training_plan, generate_training_plan_from_survey

def test_generate_training_plan():
    gaps = [{"skill_name": "Present Simple vs Present Continuous", "severity": "high", "root_causes": [], "probability": 0.8, "reason": "Test"}]
    mastery = {"as3.u1.l3": {"skill_name": "To Be", "probability": 0.9, "status": "mastered"}}
    plan = generate_training_plan(gaps, mastery, student_name="Học sinh test", level="A1")
    assert plan is not None
    assert len(plan) > 0
    # Should contain either the AI response or the fallback content
    assert any(word in plan.lower() for word in ["học sinh", "hệ thống", "lỗ hổng", "ôn", "em", "present", "bài học"])

def test_generate_training_plan_from_survey():
    plan = generate_training_plan_from_survey(
        student_name="Học sinh test",
        grade="Lớp 6",
        years_studying_english=2,
        learning_environment="school",
        self_assessment_level="A1",
        learning_goal="Giao tiếp tốt"
    )
    assert plan is not None
    assert len(plan) > 0
    assert "Học sinh" in plan or "Khảo sát" in plan or "lộ trình" in plan or "ôn" in plan


def test_generate_alternative_plans():
    from tools.plan_tool import generate_alternative_plans
    
    gaps = [
        {"skill_id": "SKILL_MATH_08", "skill_name": "Phân tích đa thức thành nhân tử", "severity": "medium", "root_causes": [], "probability": 0.42},
        {"skill_id": "SKILL_MATH_05", "skill_name": "Hằng đẳng thức đáng nhớ", "severity": "high", "root_causes": [], "probability": 0.35}
    ]
    mastery = {
        "SKILL_MATH_08": {"skill_name": "Phân tích đa thức thành nhân tử", "probability": 0.42, "status": "weak"},
        "SKILL_MATH_05": {"skill_name": "Hằng đẳng thức đáng nhớ", "probability": 0.35, "status": "weak"}
    }
    
    plans = generate_alternative_plans(
        gaps=gaps,
        mastery=mastery,
        student_name="Nguyễn Văn A",
        level="A1",
        old_plan="Ôn tập lý thuyết cũ"
    )
    
    assert plans is not None
    assert "alternative_paths" in plans
    assert "path_1_back_to_roots" in plans["alternative_paths"]
    assert "path_2_pacing_density" in plans["alternative_paths"]
    assert "path_3_alternative_modality" in plans["alternative_paths"]
    assert "teacher_summary_comparison" in plans
    
    p1 = plans["alternative_paths"]["path_1_back_to_roots"]
    assert p1["target_prerequisite_skills"] is not None
    assert len(p1["action_steps"]) > 0

