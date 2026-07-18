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
    assert "Học sinh" in plan or "hệ thống" in plan or "lỗ hổng" in plan or "ôn" in plan

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
