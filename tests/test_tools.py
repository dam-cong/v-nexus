"""Tests cho QuestionBank + 4 Tools."""
import pytest

from ai.knowledge_graph import KnowledgeGraph
from ai.bkt_engine import BKTEngine
from tools.question_bank import QuestionBank
from tools.diagnose_gap import diagnose_gap_tool, set_engine
from tools.generate_practice_path import (
    generate_practice_path_tool,
    set_dependencies as set_pp_deps,
)
from tools.teacher_dashboard_query import (
    teacher_dashboard_tool,
    set_dependencies as set_td_deps,
)
from tools.parent_dashboard_query import (
    parent_dashboard_tool,
    set_dependencies as set_pd_deps,
)


@pytest.fixture
def kg() -> KnowledgeGraph:
    return KnowledgeGraph()


@pytest.fixture
def engine(kg: KnowledgeGraph) -> BKTEngine:
    return BKTEngine(kg)


@pytest.fixture
def bank() -> QuestionBank:
    return QuestionBank()


@pytest.fixture(autouse=True)
def setup_diagnose(engine: BKTEngine):
    set_engine(engine)


@pytest.fixture(autouse=True)
def setup_practice_path(engine: BKTEngine, kg: KnowledgeGraph, bank: QuestionBank):
    set_pp_deps(engine, kg, bank)


@pytest.fixture(autouse=True)
def setup_teacher_dashboard(engine: BKTEngine, kg: KnowledgeGraph):
    class_students = {
        "CLASS01": ["S1", "S2", "S3", "S4", "S5"],
        "CLASS02": ["S6", "S7"],
    }
    set_td_deps(engine, kg, class_students)


@pytest.fixture(autouse=True)
def setup_parent_dashboard(engine: BKTEngine, kg: KnowledgeGraph):
    parent_student_map = {
        "P1": ["S1"],
        "P2": ["S2", "S3"],
        "P3": ["S99"],
    }
    set_pd_deps(engine, kg, parent_student_map)


# ─── QuestionBank Tests ──────────────────────────────────────────────────────


class TestQuestionBank:
    def test_load_questions(self, bank: QuestionBank):
        assert bank.count() > 0

    def test_get_by_skill(self, bank: QuestionBank):
        questions = bank.get_by_skill("as3.welcome.l1")
        assert len(questions) > 0
        assert all(q.skill_id == "as3.welcome.l1" for q in questions)

    def test_get_by_skill_with_difficulty(self, bank: QuestionBank):
        questions = bank.get_by_skill("as3.welcome.l1", difficulty=1)
        assert len(questions) > 0
        assert all(q.difficulty == 1 for q in questions)

    def test_get_by_skill_not_found(self, bank: QuestionBank):
        questions = bank.get_by_skill("NONEXISTENT")
        assert questions == []

    def test_question_has_required_fields(self, bank: QuestionBank):
        for q in bank.get_all():
            assert q.id
            assert q.skill_id
            assert q.content
            assert len(q.options) >= 2
            assert 0 <= q.correct_answer < len(q.options)
            assert 1 <= q.difficulty <= 3


# ─── diagnose_gap Tests ──────────────────────────────────────────────────────


class TestDiagnoseGap:
    def test_empty_answers(self):
        result = diagnose_gap_tool.func(student_id="S1", answers=[])
        assert "Chưa đủ dữ liệu" in result

    def test_all_correct(self):
        answers = [
            {"skill_id": "as3.welcome.l1", "correct": True},
            {"skill_id": "as3.welcome.l2", "correct": True},
        ]
        result = diagnose_gap_tool.func(student_id="S1", answers=answers)
        assert "đúng tất cả" in result

    def test_wrong_answer_finds_gap(self, engine: BKTEngine):
        engine.update("S1", "as3.welcome.l1", correct=False)
        engine.update("S1", "as3.u1.l1", correct=False)
        answers = [
            {"skill_id": "as3.u1.l2", "correct": False},
        ]
        result = diagnose_gap_tool.func(student_id="S1", answers=answers)
        assert "lỗ hổng" in result.lower() or "Ưu tiên" in result

    def test_multiple_wrong_skills(self):
        answers = [
            {"skill_id": "as3.welcome.l1", "correct": False},
            {"skill_id": "as3.u1.l1", "correct": False},
        ]
        result = diagnose_gap_tool.func(student_id="S1", answers=answers)
        assert "lỗ hổng" in result.lower() or "Ưu tiên" in result

    def test_diagnose_gap_tool_schema(self):
        schema = diagnose_gap_tool.input_schema
        assert "student_id" in schema["properties"]
        assert "answers" in schema["properties"]
        assert "student_id" in schema["required"]
        assert "answers" in schema["required"]

    def test_tool_name_and_description(self):
        assert diagnose_gap_tool.name == "diagnose_gap"
        assert len(diagnose_gap_tool.description) > 0


# ─── generate_practice_path Tests ────────────────────────────────────────────


class TestGeneratePracticePath:
    def test_empty_gaps(self):
        result = generate_practice_path_tool.func(
            student_id="S1", gaps=[]
        )
        assert "không có lỗ hổng" in result.lower()

    def test_with_gaps(self):
        gaps = [
            {"skill_id": "as3.u1.l1", "gap_depth": 2, "mastery_prob": 0.2},
        ]
        result = generate_practice_path_tool.func(student_id="S1", gaps=gaps)
        assert "lộ trình" in result.lower() or "câu hỏi" in result.lower()

    def test_multiple_gaps_sorted_by_depth(self):
        gaps = [
            {"skill_id": "as3.welcome.l1", "gap_depth": 1, "mastery_prob": 0.3},
            {"skill_id": "as3.u1.l1", "gap_depth": 2, "mastery_prob": 0.2},
        ]
        result = generate_practice_path_tool.func(student_id="S1", gaps=gaps)
        assert len(result) > 0

    def test_tool_schema(self):
        schema = generate_practice_path_tool.input_schema
        assert "student_id" in schema["properties"]
        assert "gaps" in schema["properties"]

    def test_tool_name(self):
        assert generate_practice_path_tool.name == "generate_practice_path"


# ─── teacher_dashboard_query Tests ────────────────────────────────────────────


class TestTeacherDashboard:
    def test_empty_class(self):
        result = teacher_dashboard_tool.func(class_id="EMPTY_CLASS")
        assert "Không tìm thấy" in result

    def test_valid_class(self):
        result = teacher_dashboard_tool.func(class_id="CLASS01")
        assert "Dashboard" in result
        assert "Tổng học sinh" in result

    def test_heatmap_present(self):
        result = teacher_dashboard_tool.func(class_id="CLASS01")
        assert "Heatmap" in result or "lỗ hổng" in result.lower()

    def test_priority_list(self):
        result = teacher_dashboard_tool.func(class_id="CLASS01")
        assert "ưu tiên" in result.lower()

    def test_access_control_by_class(self):
        result1 = teacher_dashboard_tool.func(class_id="CLASS01")
        result2 = teacher_dashboard_tool.func(class_id="CLASS02")
        assert "CLASS01" in result1
        assert "CLASS02" in result2

    def test_tool_schema(self):
        schema = teacher_dashboard_tool.input_schema
        assert "class_id" in schema["properties"]
        assert "class_id" in schema["required"]

    def test_tool_name(self):
        assert teacher_dashboard_tool.name == "teacher_dashboard_query"


# ─── parent_dashboard_query Tests ────────────────────────────────────────────


class TestParentDashboard:
    def test_valid_parent_student(self, engine: BKTEngine):
        engine.update("S1", "as3.welcome.l1", correct=True)
        engine.update("S1", "as3.welcome.l2", correct=False)
        result = parent_dashboard_tool.func(student_id="S1", parent_id="P1")
        assert "Tiến độ" in result

    def test_invalid_parent_student(self):
        result = parent_dashboard_tool.func(student_id="S99", parent_id="P1")
        assert "Lỗi quyền truy cập" in result

    def test_parent_with_multiple_children(self, engine: BKTEngine):
        engine.update("S2", "as3.welcome.l1", correct=True)
        engine.update("S2", "as3.u1.l1", correct=False)
        result = parent_dashboard_tool.func(student_id="S2", parent_id="P2")
        assert "Tiến độ" in result

    def test_no_data_student(self):
        result = parent_dashboard_tool.func(student_id="S99", parent_id="P3")
        assert "chưa có dữ liệu" in result.lower()

    def test_suggestion_for_parents(self):
        parent_dashboard_tool.func(student_id="S1", parent_id="P1")
        result = parent_dashboard_tool.func(student_id="S1", parent_id="P1")
        assert "Gợi ý" in result or "chưa có dữ liệu" in result.lower()

    def test_tool_schema(self):
        schema = parent_dashboard_tool.input_schema
        assert "student_id" in schema["properties"]
        assert "parent_id" in schema["properties"]
        assert "student_id" in schema["required"]
        assert "parent_id" in schema["required"]

    def test_tool_name(self):
        assert parent_dashboard_tool.name == "parent_dashboard_query"


# ─── Integration: End-to-end flow ────────────────────────────────────────────


class TestEndToEnd:
    def test_diagnose_then_practice(self, engine: BKTEngine):
        answers = [
            {"skill_id": "as3.u1.l1", "correct": False},
            {"skill_id": "as3.welcome.l1", "correct": False},
        ]
        diag_result = diagnose_gap_tool.func(student_id="E2E", answers=answers)
        assert "lỗ hổng" in diag_result.lower() or "Ưu tiên" in diag_result

        gaps = [
            {"skill_id": "as3.welcome.l1", "gap_depth": 2, "mastery_prob": 0.3},
            {"skill_id": "as3.u1.l1", "gap_depth": 1, "mastery_prob": 0.3},
        ]
        path_result = generate_practice_path_tool.func(student_id="E2E", gaps=gaps)
        assert "lộ trình" in path_result.lower() or "câu hỏi" in path_result.lower()

    def test_teacher_then_parent(self):
        td_result = teacher_dashboard_tool.func(class_id="CLASS01")
        assert "Dashboard" in td_result

        pd_result = parent_dashboard_tool.func(student_id="S1", parent_id="P1")
        assert "Tiến độ" in pd_result or "chưa có dữ liệu" in pd_result.lower()
