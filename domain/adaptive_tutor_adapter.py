"""Domain Adapter cho Adaptive Tutoring — V-Nexus Tutor.

Thay sme_innovation_adapter.py. Nối Knowledge Graph + BKT Engine + 4 Tools
vào Planner Agent.
"""
from __future__ import annotations

from pathlib import Path

from ai.bkt_engine import BKTEngine
from ai.knowledge_graph import KnowledgeGraph
from domain.adapter import DomainAdapter
from tools.base import Tool
from tools.diagnose_gap import diagnose_gap_tool, set_engine as set_diagnose_engine
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
from tools.question_bank import QuestionBank

_PROMPTS_DIR = Path(__file__).parent / "prompts"


def _load_prompt(name: str) -> str:
    path = _PROMPTS_DIR / name
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


class AdaptiveTutorAdapter(DomainAdapter):
    """Domain Adapter cho gia sư thích ứng Toán 6-7."""

    def __init__(self) -> None:
        self._kg = KnowledgeGraph()
        self._engine = BKTEngine(self._kg)
        self._bank = QuestionBank()

        set_diagnose_engine(self._engine)
        set_pp_deps(self._engine, self._kg, self._bank)

        self._class_students: dict[str, list[str]] = {}
        self._parent_student_map: dict[str, list[str]] = {}
        set_td_deps(self._engine, self._kg, self._class_students)
        set_pd_deps(self._engine, self._kg, self._parent_student_map)

    @property
    def engine(self) -> BKTEngine:
        return self._engine

    @property
    def knowledge_graph(self) -> KnowledgeGraph:
        return self._kg

    @property
    def question_bank(self) -> QuestionBank:
        return self._bank

    def set_class_students(self, mapping: dict[str, list[str]]) -> None:
        self._class_students = mapping
        set_td_deps(self._engine, self._kg, self._class_students)

    def set_parent_student_map(self, mapping: dict[str, list[str]]) -> None:
        self._parent_student_map = mapping
        set_pd_deps(self._engine, self._kg, self._parent_student_map)

    def system_prompt(self) -> str:
        base = _load_prompt("system.md")
        return base

    def tools(self) -> list[Tool]:
        return [
            diagnose_gap_tool,
            generate_practice_path_tool,
            teacher_dashboard_tool,
            parent_dashboard_tool,
        ]
