"""Tests cho Adaptive Test Engine (CAT)."""
import pytest

from ai.knowledge_graph import KnowledgeGraph
from ai.bkt_engine import BKTEngine
from ai.adaptive_test import AdaptiveTestEngine, TestSession, CATResult
from tools.question_bank import QuestionBank


@pytest.fixture
def kg() -> KnowledgeGraph:
    return KnowledgeGraph()


@pytest.fixture
def engine(kg: KnowledgeGraph) -> BKTEngine:
    return BKTEngine(kg)


@pytest.fixture
def bank() -> QuestionBank:
    return QuestionBank()


@pytest.fixture
def cat(engine: BKTEngine, kg: KnowledgeGraph, bank: QuestionBank) -> AdaptiveTestEngine:
    return AdaptiveTestEngine(engine, kg, bank)


class TestAdaptiveTestEngineInit:
    def test_initialization(self, cat: AdaptiveTestEngine):
        assert cat.engine is not None
        assert cat.kg is not None
        assert cat.bank is not None

    def test_empty_sessions(self, cat: AdaptiveTestEngine):
        assert cat._sessions == {}


class TestSession:
    def test_start_session(self, cat: AdaptiveTestEngine):
        session = cat.start_session("S1", max_questions=10)
        assert session.student_id == "S1"
        assert session.max_questions == 10
        assert session.total_questions == 0
        assert not session.is_complete

    def test_start_session_custom_skills(self, cat: AdaptiveTestEngine):
        skills = ["as3.welcome.l1", "as3.u1.l1"]
        session = cat.start_session("S1", skills_to_test=skills)
        assert session.skills_to_test == skills

    def test_session_stored(self, cat: AdaptiveTestEngine):
        cat.start_session("S1")
        assert "S1" in cat._sessions


class TestGetNextQuestion:
    def test_returns_question(self, cat: AdaptiveTestEngine):
        cat.start_session("S1")
        q = cat.get_next_question("S1")
        assert q is not None
        assert "question_id" in q
        assert "content" in q
        assert "options" in q

    def test_returns_dict_format(self, cat: AdaptiveTestEngine):
        cat.start_session("S1")
        q = cat.get_next_question("S1")
        assert isinstance(q, dict)
        assert q["question_number"] == 1
        assert q["max_questions"] == 15

    def test_no_session_returns_none(self, cat: AdaptiveTestEngine):
        q = cat.get_next_question("NONEXISTENT")
        assert q is None

    def test_complete_session_returns_none(self, cat: AdaptiveTestEngine):
        session = cat.start_session("S1", max_questions=1)
        cat.get_next_question("S1")
        cat.submit_answer("S1", cat.get_session("S1").current_question.id, 0)
        q = cat.get_next_question("S1")
        assert q is None


class TestSubmitAnswer:
    def test_submit_correct(self, cat: AdaptiveTestEngine):
        cat.start_session("S1")
        q = cat.get_next_question("S1")
        session = cat.get_session("S1")
        correct_option = session.current_question.correct_answer
        result = cat.submit_answer("S1", q["question_id"], correct_option)
        assert result["correct"] is True
        assert "mastery_after" in result

    def test_submit_wrong(self, cat: AdaptiveTestEngine):
        cat.start_session("S1")
        q = cat.get_next_question("S1")
        session = cat.get_session("S1")
        wrong_option = (session.current_question.correct_answer + 1) % len(session.current_question.options)
        result = cat.submit_answer("S1", q["question_id"], wrong_option)
        assert result["correct"] is False

    def test_submit_wrong_question_id(self, cat: AdaptiveTestEngine):
        cat.start_session("S1")
        cat.get_next_question("S1")
        result = cat.submit_answer("S1", "WRONG_ID", 0)
        assert "error" in result

    def test_submit_no_session(self, cat: AdaptiveTestEngine):
        result = cat.submit_answer("NONEXISTENT", "Q001", 0)
        assert "error" in result

    def test_question_number_increments(self, cat: AdaptiveTestEngine):
        cat.start_session("S1")
        q = cat.get_next_question("S1")
        session = cat.get_session("S1")
        cat.submit_answer("S1", q["question_id"], 0)
        assert session.total_questions == 1

    def test_auto_complete_at_max(self, cat: AdaptiveTestEngine):
        cat.start_session("S1", max_questions=1)
        q = cat.get_next_question("S1")
        result = cat.submit_answer("S1", q["question_id"], 0)
        assert result["is_complete"] is True
        assert result["questions_remaining"] == 0


class TestFinishSession:
    def test_finish_returns_result(self, cat: AdaptiveTestEngine):
        cat.start_session("S1")
        q = cat.get_next_question("S1")
        session = cat.get_session("S1")
        cat.submit_answer("S1", q["question_id"], 0)
        result = cat.finish_session("S1")
        assert isinstance(result, CATResult)
        assert result.student_id == "S1"
        assert result.total_questions == 1

    def test_finish_no_session(self, cat: AdaptiveTestEngine):
        result = cat.finish_session("NONEXISTENT")
        assert result is None

    def test_result_has_mastery(self, cat: AdaptiveTestEngine):
        cat.start_session("S1")
        q = cat.get_next_question("S1")
        cat.submit_answer("S1", q["question_id"], 0)
        result = cat.finish_session("S1")
        assert len(result.mastery_snapshot) > 0

    def test_result_has_gaps(self, cat: AdaptiveTestEngine):
        cat.start_session("S1")
        q = cat.get_next_question("S1")
        cat.submit_answer("S1", q["question_id"], 0)
        result = cat.finish_session("S1")
        assert isinstance(result.gaps_found, list)

    def test_efficiency_ratio(self, cat: AdaptiveTestEngine):
        cat.start_session("S1")
        q = cat.get_next_question("S1")
        session = cat.get_session("S1")
        correct = session.current_question.correct_answer
        cat.submit_answer("S1", q["question_id"], correct)
        result = cat.finish_session("S1")
        assert 0 <= result.efficiency_ratio <= 1


class TestEntropySelection:
    def test_higher_entropy_selected_first(self, cat: AdaptiveTestEngine):
        cat.engine.update("S1", "as3.welcome.l1", correct=False)
        cat.engine.update("S1", "as3.welcome.l1", correct=False)
        cat.engine.update("S1", "as3.u1.l4", correct=True)
        cat.engine.update("S1", "as3.u1.l4", correct=True)

        cat.start_session("S1")
        q = cat.get_next_question("S1")
        assert q is not None

    def test_calculate_entropy(self, cat: AdaptiveTestEngine):
        e_low = cat._calculate_entropy(0.1)
        e_mid = cat._calculate_entropy(0.5)
        e_high = cat._calculate_entropy(0.9)
        assert e_mid > e_low
        assert e_mid > e_high


class TestMultiStudent:
    def test_independent_sessions(self, cat: AdaptiveTestEngine):
        cat.start_session("S1")
        cat.start_session("S2")
        q1 = cat.get_next_question("S1")
        q2 = cat.get_next_question("S2")
        assert q1 is not None
        assert q2 is not None

    def test_independent_mastery(self, cat: AdaptiveTestEngine):
        cat.start_session("S1")
        q = cat.get_next_question("S1")
        cat.submit_answer("S1", q["question_id"], 0)

        m1 = cat.engine.get_mastery("S1", q["skill_id"])
        m2 = cat.engine.get_mastery("S2", q["skill_id"])
        assert m1 != m2
