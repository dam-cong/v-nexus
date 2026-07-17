"""Tests cho Output Interpreter (chạy offline, không gọi LLM)."""
import pytest

from ai.output_interpreter import (
    interpret_for_teacher,
    interpret_for_parent,
    interpret_diagnose_student,
    InterpretedOutput,
)


@pytest.fixture
def sample_gaps() -> list[dict]:
    return [
        {
            "skill_id": "M6.RA.FRAC01",
            "skill_name": "Phân số và phân số đơn vị",
            "mastery_prob": 0.25,
            "gap_depth": 2,
            "grade": 6,
        },
        {
            "skill_id": "M6.RA.FRAC03",
            "skill_name": "Quy đồng phân số",
            "mastery_prob": 0.35,
            "gap_depth": 1,
            "grade": 6,
        },
    ]


@pytest.fixture
def sample_mastery() -> dict[str, float]:
    return {
        "M6.RA.FRAC01": 0.25,
        "M6.RA.FRAC02": 0.6,
        "M6.RA.FRAC03": 0.35,
        "M6.RA.FRAC04": 0.8,
        "M6.RA.DEC01": 0.9,
    }


class TestInterpretForTeacher:
    def test_returns_interpreted_output(self, sample_gaps, sample_mastery):
        result = interpret_for_teacher(sample_gaps, sample_mastery, use_llm=False)
        assert isinstance(result, InterpretedOutput)
        assert result.role == "teacher"

    def test_has_raw_data(self, sample_gaps, sample_mastery):
        result = interpret_for_teacher(sample_gaps, sample_mastery, use_llm=False)
        assert "gaps" in result.raw_data
        assert "mastery_summary" in result.raw_data
        assert "alerts" in result.raw_data

    def test_natural_language_not_empty(self, sample_gaps, sample_mastery):
        result = interpret_for_teacher(sample_gaps, sample_mastery, use_llm=False)
        assert len(result.natural_language) > 0

    def test_contains_key_info(self, sample_gaps, sample_mastery):
        result = interpret_for_teacher(sample_gaps, sample_mastery, use_llm=False)
        nl = result.natural_language.lower()
        assert "tổng quan" in nl or "kỹ năng" in nl

    def test_empty_gaps(self, sample_mastery):
        result = interpret_for_teacher([], sample_mastery, use_llm=False)
        assert result.role == "teacher"
        assert len(result.natural_language) > 0

    def test_alerts_detected(self, sample_gaps, sample_mastery):
        result = interpret_for_teacher(sample_gaps, sample_mastery, use_llm=False)
        assert "M6.RA.FRAC01" in result.raw_data["alerts"]


class TestInterpretForParent:
    def test_returns_interpreted_output(self, sample_gaps, sample_mastery):
        result = interpret_for_parent("S1", sample_gaps, sample_mastery, use_llm=False)
        assert isinstance(result, InterpretedOutput)
        assert result.role == "parent"

    def test_has_student_id(self, sample_gaps, sample_mastery):
        result = interpret_for_parent("S1", sample_gaps, sample_mastery, use_llm=False)
        assert result.raw_data["student_id"] == "S1"

    def test_natural_language_simple(self, sample_gaps, sample_mastery):
        result = interpret_for_parent("S1", sample_gaps, sample_mastery, use_llm=False)
        nl = result.natural_language
        assert "mastery" not in nl.lower()
        assert "gap_depth" not in nl.lower()

    def test_empty_gaps(self):
        all_mastered = {f"M6.SKILL{i}": 0.8 for i in range(5)}
        result = interpret_for_parent("S1", [], all_mastered, use_llm=False)
        assert "tốt" in result.natural_language.lower() or "đạt" in result.natural_language.lower()

    def test_no_comparison(self, sample_gaps, sample_mastery):
        result = interpret_for_parent("S1", sample_gaps, sample_mastery, use_llm=False)
        nl = result.natural_language.lower()
        assert "so sánh" not in nl or "học sinh khác" not in nl


class TestInterpretDiagnoseStudent:
    def test_returns_interpreted_output(self, sample_gaps):
        result = interpret_diagnose_student(sample_gaps, use_llm=False)
        assert isinstance(result, InterpretedOutput)
        assert result.role == "student"

    def test_empty_gaps_celebration(self):
        result = interpret_diagnose_student([], use_llm=False)
        assert "chúc mừng" in result.natural_language.lower() or "đúng" in result.natural_language.lower()

    def test_has_gaps_info(self, sample_gaps):
        result = interpret_diagnose_student(sample_gaps, use_llm=False)
        assert "luyện tập" in result.natural_language.lower() or "chưa vững" in result.natural_language.lower()

    def test_student_friendly_tone(self, sample_gaps):
        result = interpret_diagnose_student(sample_gaps, use_llm=False)
        nl = result.natural_language.lower()
        assert "em" in nl


class TestInterpretedOutput:
    def test_dataclass_fields(self, sample_gaps, sample_mastery):
        result = interpret_for_teacher(sample_gaps, sample_mastery, use_llm=False)
        assert hasattr(result, "role")
        assert hasattr(result, "raw_data")
        assert hasattr(result, "natural_language")
