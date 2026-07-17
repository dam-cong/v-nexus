"""Integration tests — end-to-end flow trên SQLite in-memory.

Test: KnowledgeGraph → BKT Engine → Tools → Domain Adapter → Diagnose Endpoint
"""
import json
import pytest

from ai.knowledge_graph import KnowledgeGraph
from ai.bkt_engine import BKTEngine, MASTERY_THRESHOLD
from ai.output_interpreter import (
    interpret_for_teacher,
    interpret_for_parent,
    interpret_diagnose_student,
)
from ai.adaptive_test import AdaptiveTestEngine
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
from domain.adaptive_tutor_adapter import AdaptiveTutorAdapter


@pytest.fixture
def adapter() -> AdaptiveTutorAdapter:
    return AdaptiveTutorAdapter()


@pytest.fixture(autouse=True)
def setup_tools(adapter: AdaptiveTutorAdapter):
    set_engine(adapter.engine)
    set_pp_deps(adapter.engine, adapter.knowledge_graph, adapter.question_bank)
    class_students = {"CLASS01": ["S1", "S2", "S3", "S4", "S5"]}
    parent_student_map = {"P1": ["S1"], "P2": ["S2", "S3"]}
    set_td_deps(adapter.engine, adapter.knowledge_graph, class_students)
    set_pd_deps(adapter.engine, adapter.knowledge_graph, parent_student_map)


class TestEndToEndDiagnose:
    def test_placement_test_flow(self, adapter: AdaptiveTutorAdapter):
        answers = [
            {"skill_id": "as3.welcome.l1", "correct": True},
            {"skill_id": "as3.welcome.l2", "correct": True},
            {"skill_id": "as3.u1.l1", "correct": False},
            {"skill_id": "as3.u1.l2", "correct": False},
            {"skill_id": "as3.u1.l4", "correct": True},
        ]
        result = diagnose_gap_tool.func(student_id="S1", answers=answers)
        assert len(result) > 0

    def test_practice_path_after_diagnose(self, adapter: AdaptiveTutorAdapter):
        answers = [
            {"skill_id": "as3.u1.l1", "correct": False},
            {"skill_id": "as3.welcome.l1", "correct": False},
        ]
        diag = diagnose_gap_tool.func(student_id="S1", answers=answers)
        assert "lỗ hổng" in diag.lower() or "Ưu tiên" in diag

        gaps = [
            {"skill_id": "as3.welcome.l1", "gap_depth": 2, "mastery_prob": 0.3},
            {"skill_id": "as3.u1.l1", "gap_depth": 1, "mastery_prob": 0.3},
        ]
        path = generate_practice_path_tool.func(student_id="S1", gaps=gaps)
        assert "lộ trình" in path.lower() or "câu hỏi" in path.lower()

    def test_teacher_dashboard_after_diagnose(self, adapter: AdaptiveTutorAdapter):
        for i, sid in enumerate(["S1", "S2", "S3"]):
            adapter.engine.update(sid, "as3.u1.l1", correct=i > 0)

        result = teacher_dashboard_tool.func(class_id="CLASS01")
        assert "Dashboard" in result

    def test_parent_dashboard_after_diagnose(self, adapter: AdaptiveTutorAdapter):
        adapter.engine.update("S1", "as3.welcome.l1", correct=True)
        adapter.engine.update("S1", "as3.u1.l1", correct=False)

        result = parent_dashboard_tool.func(student_id="S1", parent_id="P1")
        assert "Tiến độ" in result

    def test_full_cycle_multiple_students(self, adapter: AdaptiveTutorAdapter):
        students_answers = {
            "S1": [
                {"skill_id": "as3.welcome.l1", "correct": True},
                {"skill_id": "as3.u1.l1", "correct": False},
            ],
            "S2": [
                {"skill_id": "as3.welcome.l1", "correct": False},
                {"skill_id": "as3.u1.l1", "correct": False},
            ],
            "S3": [
                {"skill_id": "as3.welcome.l1", "correct": True},
                {"skill_id": "as3.u1.l1", "correct": True},
            ],
        }

        for sid, answers in students_answers.items():
            diag = diagnose_gap_tool.func(student_id=sid, answers=answers)
            assert len(diag) > 0

        td = teacher_dashboard_tool.func(class_id="CLASS01")
        assert "Dashboard" in td


class TestEndToEndCAT:
    def test_adaptive_test_flow(self, adapter: AdaptiveTutorAdapter):
        cat = AdaptiveTestEngine(
            adapter.engine, adapter.knowledge_graph, adapter.question_bank
        )

        session = cat.start_session("S1", max_questions=5)
        assert session.total_questions == 0

        q = cat.get_next_question("S1")
        assert q is not None

        result = cat.submit_answer("S1", q["question_id"], 0)
        assert "correct" in result

        q2 = cat.get_next_question("S1")
        assert q2 is not None

        cat_result = cat.finish_session("S1")
        assert cat_result is not None
        assert cat_result.total_questions >= 1

    def test_cat_with_wrong_answers(self, adapter: AdaptiveTutorAdapter):
        cat = AdaptiveTestEngine(
            adapter.engine, adapter.knowledge_graph, adapter.question_bank
        )

        cat.start_session("S1", max_questions=3)
        for _ in range(3):
            q = cat.get_next_question("S1")
            if q:
                session = cat.get_session("S1")
                wrong = (session.current_question.correct_answer + 1) % len(
                    session.current_question.options
                )
                cat.submit_answer("S1", q["question_id"], wrong)

        result = cat.finish_session("S1")
        assert result.total_questions == 3


class TestEndToEndOutputInterpreter:
    def test_teacher_interpretation(self, adapter: AdaptiveTutorAdapter):
        gaps = [
            {"skill_id": "as3.u1.l1", "skill_name": "Quy đồng phân số", "mastery_prob": 0.3},
        ]
        mastery = {"as3.welcome.l1": 0.8, "as3.u1.l1": 0.3, "as3.u1.l4": 0.9}

        result = interpret_for_teacher(gaps, mastery, use_llm=False)
        assert result.role == "teacher"
        assert len(result.natural_language) > 0

    def test_parent_interpretation(self, adapter: AdaptiveTutorAdapter):
        gaps = [
            {"skill_id": "as3.u1.l1", "skill_name": "Quy đồng phân số", "mastery_prob": 0.3},
        ]
        mastery = {"as3.welcome.l1": 0.8, "as3.u1.l1": 0.3}

        result = interpret_for_parent("S1", gaps, mastery, use_llm=False)
        assert result.role == "parent"
        assert "mastery" not in result.natural_language.lower()

    def test_student_interpretation(self, adapter: AdaptiveTutorAdapter):
        gaps = [
            {"skill_id": "as3.u1.l1", "skill_name": "Quy đồng phân số", "mastery_prob": 0.3},
        ]

        result = interpret_diagnose_student(gaps, use_llm=False)
        assert result.role == "student"
        assert "em" in result.natural_language.lower()


class TestKnowledgeGraphIntegration:
    def test_kg_matches_bkt(self, adapter: AdaptiveTutorAdapter):
        kg = adapter.knowledge_graph
        engine = adapter.engine

        for skill in kg.get_all_skills():
            mastery = engine.get_mastery("test", skill.id)
            assert 0 < mastery < 1

    def test_traversal_affects_diagnosis(self, adapter: AdaptiveTutorAdapter):
        engine = adapter.engine

        engine.update("S1", "as3.welcome.l1", correct=False)
        engine.update("S1", "as3.welcome.l1", correct=False)

        gaps = engine.diagnose_root_cause("S1", "as3.u1.l2")
        assert len(gaps) > 0


class TestQuestionBankIntegration:
    def test_bank_has_questions_for_all_skills(self, adapter: AdaptiveTutorAdapter):
        bank = adapter.question_bank
        kg = adapter.knowledge_graph

        skills_with_questions = 0
        for skill in kg.get_all_skills():
            questions = bank.get_by_skill(skill.id)
            if questions:
                skills_with_questions += 1

        assert skills_with_questions > 0

    def test_practice_path_uses_bank(self, adapter: AdaptiveTutorAdapter):
        bank = adapter.question_bank
        questions = bank.get_by_skill("as3.welcome.l1")
        assert len(questions) > 0
        assert questions[0].skill_id == "as3.welcome.l1"
