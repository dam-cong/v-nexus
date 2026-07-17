"""Tests cho KnowledgeGraph và BKTEngine."""
import pytest

from ai.knowledge_graph import KnowledgeGraph, Skill, SkillNotFoundError
from ai.bkt_engine import BKTEngine, GapResult, MASTERY_THRESHOLD


@pytest.fixture
def kg() -> KnowledgeGraph:
    return KnowledgeGraph()


@pytest.fixture
def engine(kg: KnowledgeGraph) -> BKTEngine:
    return BKTEngine(kg)


# ─── KnowledgeGraph Tests ────────────────────────────────────────────────────


class TestKnowledgeGraphLoad:
    def test_load_knowledge_graph(self, kg: KnowledgeGraph):
        assert len(kg) > 0
        assert kg.subject == "Tiếng Anh"
        assert 3 in kg.grades
        assert 4 in kg.grades

    def test_all_skills_have_required_fields(self, kg: KnowledgeGraph):
        for skill in kg.get_all_skills():
            assert skill.id
            assert skill.code_gdpt
            assert skill.name_vi
            assert skill.grade in (3, 4)
            assert 0 < skill.p_init < 1
            assert 0 < skill.p_transit < 1
            assert 0 < skill.p_slip < 1
            assert 0 < skill.p_guess < 1


class TestKnowledgeGraphQuery:
    def test_get_skill_exists(self, kg: KnowledgeGraph):
        skill = kg.get_skill("as3.welcome.l1")
        assert skill.name_vi
        assert skill.grade == 3

    def test_get_skill_not_exists(self, kg: KnowledgeGraph):
        with pytest.raises(SkillNotFoundError) as exc_info:
            kg.get_skill("NONEXISTENT_SKILL")
        assert "NONEXISTENT_SKILL" in str(exc_info.value)

    def test_get_all_skills(self, kg: KnowledgeGraph):
        skills = kg.get_all_skills()
        assert len(skills) == 156

    def test_get_skills_by_grade_3(self, kg: KnowledgeGraph):
        skills = kg.get_skills_by_grade(3)
        assert len(skills) > 0
        assert all(s.grade == 3 for s in skills)

    def test_get_skills_by_grade_4(self, kg: KnowledgeGraph):
        skills = kg.get_skills_by_grade(4)
        assert len(skills) > 0
        assert all(s.grade == 4 for s in skills)

    def test_get_skills_by_grade_empty(self, kg: KnowledgeGraph):
        skills = kg.get_skills_by_grade(8)
        assert skills == []

    def test_contains(self, kg: KnowledgeGraph):
        assert "as3.welcome.l1" in kg
        assert "NONEXISTENT" not in kg


class TestKnowledgeGraphPrerequisites:
    def test_get_prerequisites_direct(self, kg: KnowledgeGraph):
        pres = kg.get_prerequisites("as3.welcome.l2")
        assert len(pres) == 1
        assert pres[0].id == "as3.welcome.l1"

    def test_get_prerequisites_multiple(self, kg: KnowledgeGraph):
        from ai.knowledge_graph import Skill
        mock_skill = Skill(
            id="mock.skill.multiple",
            code_gdpt="mock.skill.multiple",
            name_vi="Mock",
            name_en="Mock",
            grade=3,
            unit="Mock",
            skill_type="grammar",
            p_init=0.3,
            p_transit=0.3,
            p_slip=0.1,
            p_guess=0.2,
            prerequisites=("as3.welcome.l1", "as3.welcome.l2")
        )
        kg._skills[mock_skill.id] = mock_skill
        pres = kg.get_prerequisites("mock.skill.multiple")
        pre_ids = {p.id for p in pres}
        assert "as3.welcome.l1" in pre_ids
        assert "as3.welcome.l2" in pre_ids

    def test_get_prerequisites_no_prereq(self, kg: KnowledgeGraph):
        pres = kg.get_prerequisites("as3.welcome.l1")
        assert pres == []

    def test_get_prerequisites_not_exists(self, kg: KnowledgeGraph):
        with pytest.raises(SkillNotFoundError):
            kg.get_prerequisites("NONEXISTENT")

    def test_get_all_prerequisites_chain(self, kg: KnowledgeGraph):
        all_pres = kg.get_all_prerequisites("as3.u1.l3")
        pre_ids = {p.id for p in all_pres}
        assert "as3.u1.l2" in pre_ids
        assert "as3.u1.l1" in pre_ids
        assert "as3.welcome.l1" in pre_ids

    def test_get_dependents(self, kg: KnowledgeGraph):
        deps = kg.get_dependents("as3.welcome.l1")
        dep_ids = {d.id for d in deps}
        assert "as3.welcome.l2" in dep_ids


class TestKnowledgeGraphTraversal:
    def test_traverse_up_no_prereqs(self, kg: KnowledgeGraph):
        result = kg.traverse_up("as3.welcome.l1")
        assert result == []

    def test_traverse_up_one_level(self, kg: KnowledgeGraph):
        result = kg.traverse_up("as3.welcome.l2")
        assert len(result) == 1
        assert result[0].id == "as3.welcome.l1"

    def test_traverse_up_multi_level(self, kg: KnowledgeGraph):
        result = kg.traverse_up("as3.u1.l3")
        result_ids = [s.id for s in result]
        assert "as3.u1.l2" in result_ids
        assert "as3.u1.l1" in result_ids
        assert "as3.welcome.l1" in result_ids
        idx_04 = result_ids.index("as3.u1.l2")
        idx_03 = result_ids.index("as3.u1.l1")
        idx_01 = result_ids.index("as3.welcome.l1")
        assert idx_01 < idx_03 < idx_04

    def test_traverse_up_not_exists(self, kg: KnowledgeGraph):
        with pytest.raises(SkillNotFoundError):
            kg.traverse_up("NONEXISTENT")


# ─── BKTEngine Tests ──────────────────────────────────────────────────────────


class TestBKTEngineMastery:
    def test_initial_mastery(self, engine: BKTEngine):
        mastery = engine.get_mastery("s1", "as3.welcome.l1")
        skill = engine.kg.get_skill("as3.welcome.l1")
        assert mastery == skill.p_init

    def test_initial_mastery_consistent(self, engine: BKTEngine):
        m1 = engine.get_mastery("s1", "as3.welcome.l1")
        m2 = engine.get_mastery("s1", "as3.welcome.l1")
        assert m1 == m2

    def test_get_all_mastery(self, engine: BKTEngine):
        mastery_map = engine.get_all_mastery("s1")
        assert len(mastery_map) > 0
        for skill_id, prob in mastery_map.items():
            assert 0 < prob < 1


class TestBKTEngineUpdate:
    def test_update_correct_increases_mastery(self, engine: BKTEngine):
        initial = engine.get_mastery("s1", "as3.welcome.l1")
        updated = engine.update("s1", "as3.welcome.l1", correct=True)
        assert updated > initial

    def test_update_wrong_decreases_mastery(self, engine: BKTEngine):
        initial = engine.get_mastery("s1", "as3.welcome.l1")
        updated = engine.update("s1", "as3.welcome.l1", correct=False)
        assert updated < initial

    def test_multiple_correct_increases_towards_1(self, engine: BKTEngine):
        mastery = engine.get_mastery("s1", "as3.welcome.l1")
        for _ in range(20):
            mastery = engine.update("s1", "as3.welcome.l1", correct=True)
        assert mastery > 0.9

    def test_multiple_wrong_decreases_towards_0(self, engine: BKTEngine):
        mastery = engine.get_mastery("s1", "as3.welcome.l1")
        for _ in range(20):
            mastery = engine.update("s1", "as3.welcome.l1", correct=False)
        assert mastery < 0.1

    def test_mastery_stays_in_bounds(self, engine: BKTEngine):
        for _ in range(50):
            engine.update("s1", "as3.welcome.l1", correct=True)
        mastery = engine.get_mastery("s1", "as3.welcome.l1")
        assert 0 < mastery < 1

    def test_update_skill_not_exists(self, engine: BKTEngine):
        with pytest.raises(SkillNotFoundError):
            engine.update("s1", "NONEXISTENT", correct=True)

    def test_batch_update(self, engine: BKTEngine):
        answers = [
            {"skill_id": "as3.welcome.l1", "correct": True},
            {"skill_id": "as3.welcome.l1", "correct": True},
            {"skill_id": "as3.welcome.l1", "correct": False},
        ]
        result = engine.batch_update("s1", answers)
        assert "as3.welcome.l1" in result


class TestBKTFormula:
    def test_bayes_correct_formula(self, engine: BKTEngine):
        skill = engine.kg.get_skill("as3.welcome.l1")
        mastery = 0.5
        p_correct_L = 1.0 - skill.p_slip
        p_correct_not_L = skill.p_guess
        p_correct = p_correct_L * mastery + p_correct_not_L * (1.0 - mastery)
        expected = (p_correct_L * mastery) / p_correct
        result = engine._bayes_update_correct(skill, mastery)
        assert abs(result - expected) < 1e-6

    def test_bayes_incorrect_formula(self, engine: BKTEngine):
        skill = engine.kg.get_skill("as3.welcome.l1")
        mastery = 0.5
        p_incorrect_L = skill.p_slip
        p_incorrect_not_L = 1.0 - skill.p_guess
        p_incorrect = p_incorrect_L * mastery + p_incorrect_not_L * (1.0 - mastery)
        expected = (p_incorrect_L * mastery) / p_incorrect
        result = engine._bayes_update_incorrect(skill, mastery)
        assert abs(result - expected) < 1e-6


class TestBKTDiagnose:
    def test_diagnose_no_gap_when_mastered(self, engine: BKTEngine):
        skill = engine.kg.get_skill("as3.welcome.l1")
        engine._mastery["s1"] = {"as3.welcome.l1": 0.9}
        result = engine.diagnose_root_cause("s1", "as3.welcome.l1")
        assert result == []

    def test_diagnose_finds_gap(self, engine: BKTEngine):
        engine._mastery["s1"] = {
            "as3.welcome.l1": 0.2,
            "as3.u1.l1": 0.1,
            "as3.u1.l2": 0.3,
        }
        result = engine.diagnose_root_cause("s1", "as3.u1.l2")
        assert len(result) > 0
        gap_ids = [g.skill_id for g in result]
        assert "as3.u1.l1" in gap_ids
        assert "as3.welcome.l1" in gap_ids

    def test_diagnose_empty_student_uses_pinit(self, engine: BKTEngine):
        result = engine.diagnose_root_cause("new_student", "as3.welcome.l2")
        assert isinstance(result, list)

    def test_diagnose_sorted_by_depth_desc(self, engine: BKTEngine):
        engine._mastery["s1"] = {
            "as3.welcome.l1": 0.2,
            "as3.u1.l1": 0.2,
            "as3.u1.l2": 0.2,
        }
        result = engine.diagnose_root_cause("s1", "as3.u1.l3")
        depths = [g.gap_depth for g in result]
        assert depths == sorted(depths, reverse=True)

    def test_diagnose_gap_has_explanation(self, engine: BKTEngine):
        engine._mastery["s1"] = {"as3.welcome.l1": 0.1}
        result = engine.diagnose_root_cause("s1", "as3.welcome.l2")
        for gap in result:
            assert gap.explanation
            assert gap.recommended_action

    def test_diagnose_gap_result_fields(self, engine: BKTEngine):
        engine._mastery["s1"] = {"as3.welcome.l1": 0.1}
        result = engine.diagnose_root_cause("s1", "as3.welcome.l2")
        assert len(result) == 1
        gap = result[0]
        assert gap.skill_id == "as3.welcome.l1"
        assert gap.skill_name
        assert 0 < gap.mastery_prob < 1
        assert gap.gap_depth == 1
        assert gap.grade == 3

    def test_diagnose_skill_not_exists(self, engine: BKTEngine):
        with pytest.raises(SkillNotFoundError):
            engine.diagnose_root_cause("s1", "NONEXISTENT")

    def test_diagnose_no_prereqs(self, engine: BKTEngine):
        result = engine.diagnose_root_cause("s1", "as3.welcome.l1")
        assert result == []


class TestBKTHistory:
    def test_history_recorded(self, engine: BKTEngine):
        engine.update("s1", "as3.welcome.l1", correct=True)
        history = engine.get_student_history("s1")
        assert len(history) == 1
        assert history[0]["skill_id"] == "as3.welcome.l1"
        assert history[0]["correct"] is True

    def test_reset_student(self, engine: BKTEngine):
        engine.update("s1", "as3.welcome.l1", correct=True)
        engine.reset_student("s1")
        history = engine.get_student_history("s1")
        assert len(history) == 0


class TestBKTEngineEdgeCases:
    def test_diagnose_deep_chain(self, engine: BKTEngine):
        for sid in ["as3.welcome.l1", "as3.u1.l1", "as3.u1.l2", "as3.u1.l3"]:
            engine._mastery["s1"] = engine._mastery.get("s1", {})
            engine._mastery["s1"][sid] = 0.1
        result = engine.diagnose_root_cause("s1", "as3.u1.l3")
        assert len(result) > 0
        depths = [g.gap_depth for g in result]
        assert max(depths) > 1

    def test_diagnose_multiple_students_independent(self, engine: BKTEngine):
        engine.update("s1", "as3.welcome.l1", correct=False)
        engine.update("s2", "as3.welcome.l1", correct=True)
        m1 = engine.get_mastery("s1", "as3.welcome.l1")
        m2 = engine.get_mastery("s2", "as3.welcome.l1")
        assert m1 < m2
