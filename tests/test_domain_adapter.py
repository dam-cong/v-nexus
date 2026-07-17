"""Tests cho AdaptiveTutorAdapter + Prompts."""
import pytest

from domain.adaptive_tutor_adapter import AdaptiveTutorAdapter, _load_prompt
from ai.knowledge_graph import KnowledgeGraph
from ai.bkt_engine import BKTEngine


@pytest.fixture
def adapter() -> AdaptiveTutorAdapter:
    return AdaptiveTutorAdapter()


class TestAdaptiveTutorAdapter:
    def test_adapter_initialization(self, adapter: AdaptiveTutorAdapter):
        assert adapter.knowledge_graph is not None
        assert adapter.engine is not None
        assert adapter.question_bank is not None

    def test_system_prompt_not_empty(self, adapter: AdaptiveTutorAdapter):
        prompt = adapter.system_prompt()
        assert len(prompt) > 0

    def test_system_prompt_contains_key_content(self, adapter: AdaptiveTutorAdapter):
        prompt = adapter.system_prompt()
        assert "V-Nexus Tutor" in prompt
        assert "tool" in prompt.lower()
        assert "tiếng Việt" in prompt

    def test_tools_list_has_4_tools(self, adapter: AdaptiveTutorAdapter):
        tools = adapter.tools()
        assert len(tools) == 4

    def test_tool_names(self, adapter: AdaptiveTutorAdapter):
        tool_names = {t.name for t in adapter.tools()}
        expected = {
            "diagnose_gap",
            "generate_practice_path",
            "teacher_dashboard_query",
            "parent_dashboard_query",
        }
        assert tool_names == expected

    def test_tool_schemas_are_valid(self, adapter: AdaptiveTutorAdapter):
        for tool in adapter.tools():
            schema = tool.input_schema
            assert "type" in schema
            assert "properties" in schema
            assert "required" in schema

    def test_knowledge_graph_has_skills(self, adapter: AdaptiveTutorAdapter):
        kg = adapter.knowledge_graph
        assert len(kg) > 0

    def test_engine_uses_same_kg(self, adapter: AdaptiveTutorAdapter):
        assert adapter.engine.kg is adapter.knowledge_graph

    def test_set_class_students(self, adapter: AdaptiveTutorAdapter):
        mapping = {"CLASS01": ["S1", "S2"]}
        adapter.set_class_students(mapping)
        assert adapter._class_students == mapping

    def test_set_parent_student_map(self, adapter: AdaptiveTutorAdapter):
        mapping = {"P1": ["S1"]}
        adapter.set_parent_student_map(mapping)
        assert adapter._parent_student_map == mapping


class TestPrompts:
    def test_system_prompt_exists(self):
        prompt = _load_prompt("system.md")
        assert len(prompt) > 0

    def test_diagnose_explain_exists(self):
        prompt = _load_prompt("diagnose_explain.md")
        assert len(prompt) > 0

    def test_parent_explain_exists(self):
        prompt = _load_prompt("parent_explain.md")
        assert len(prompt) > 0

    def test_teacher_explain_exists(self):
        prompt = _load_prompt("teacher_explain.md")
        assert len(prompt) > 0

    def test_system_prompt_keywords(self):
        prompt = _load_prompt("system.md")
        assert "tool" in prompt.lower()
        assert "student_id" in prompt
        assert "class_id" in prompt

    def test_diagnose_explain_keywords(self):
        prompt = _load_prompt("diagnose_explain.md")
        assert "mastery" in prompt.lower() or "lỗ hổng" in prompt

    def test_parent_explain_keywords(self):
        prompt = _load_prompt("parent_explain.md")
        assert "phụ huynh" in prompt or "tại nhà" in prompt

    def test_teacher_explain_keywords(self):
        prompt = _load_prompt("teacher_explain.md")
        assert "lớp" in prompt or "heatmap" in prompt.lower()

    def test_load_nonexistent_prompt(self):
        prompt = _load_prompt("nonexistent.md")
        assert prompt == ""


class TestAdapterIntegration:
    def test_adapter_diagnose_flow(self, adapter: AdaptiveTutorAdapter):
        engine = adapter.engine
        engine.update("test_student", "as3.u1.l1", correct=False)
        engine.update("test_student", "as3.welcome.l1", correct=False)
        gaps = engine.diagnose_root_cause("test_student", "as3.u1.l1")
        assert len(gaps) > 0

    def test_adapter_tools_are_callable(self, adapter: AdaptiveTutorAdapter):
        for tool in adapter.tools():
            assert callable(tool.func)

    def test_adapter_has_engine_reference(self, adapter: AdaptiveTutorAdapter):
        assert adapter.engine is not None
        assert isinstance(adapter.engine, BKTEngine)

    def test_adapter_has_kg_reference(self, adapter: AdaptiveTutorAdapter):
        assert adapter.knowledge_graph is not None
        assert isinstance(adapter.knowledge_graph, KnowledgeGraph)
