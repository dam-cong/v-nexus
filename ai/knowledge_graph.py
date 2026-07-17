"""Knowledge Graph — đồ thị tri thức tiên quyết Toán 6-7 GDPT 2018.

Load từ JSON, query skill, traverse prerequisite chain.
"""
import json
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path


class SkillNotFoundError(Exception):
    """Raised khi skill_id không tồn tại trong graph."""

    def __init__(self, skill_id: str) -> None:
        self.skill_id = skill_id
        super().__init__(f"Skill '{skill_id}' không tồn tại trong knowledge graph.")


@dataclass(frozen=True)
class Skill:
    id: str
    code_gdpt: str
    name_vi: str
    name_en: str
    grade: int
    unit: str
    skill_type: str
    p_init: float
    p_transit: float
    p_slip: float
    p_guess: float
    prerequisites: tuple[str, ...] = ()


_DEFAULT_GRAPH_PATH = Path(__file__).parent / "knowledge_graph.json"


class KnowledgeGraph:
    """Đồ thị tri thức — load từ JSON, query và traverse prerequisite chain."""

    def __init__(self, graph_path: str | Path | None = None) -> None:
        path = Path(graph_path) if graph_path else _DEFAULT_GRAPH_PATH
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)

        self.subject: str = "Tiếng Anh"
        self.grades: list[int] = raw.get("grades_covered", [3, 4])
        self.curriculum: str = raw.get("description", "Academy Stars 3 & 4")

        # Map to collect prerequisites for each skill_id
        prereqs_map: dict[str, list[str]] = {}
        for edge in raw.get("edges", []):
            to_node = edge["to"]
            from_node = edge["from"]
            if to_node not in prereqs_map:
                prereqs_map[to_node] = []
            prereqs_map[to_node].append(from_node)

        self._skills: dict[str, Skill] = {}
        for s in raw.get("nodes", raw.get("skills", [])):
            sid = s.get("skill_id", s.get("id"))
            grade = s.get("grade", 3)
            unit = s.get("unit_name", s.get("unit", ""))
            name = s.get("lesson_title", s.get("name_vi", s.get("name_en", "")))
            
            # Determine skill type
            skill_type = s.get("skill_type", "vocabulary" if "vocabulary" in name.lower() else "grammar" if "grammar" in name.lower() else "other")
            
            skill = Skill(
                id=sid,
                code_gdpt=s.get("code_gdpt", sid),
                name_vi=name,
                name_en=s.get("name_en", name),
                grade=grade,
                unit=unit,
                skill_type=skill_type,
                p_init=s.get("p_init", 0.3),
                p_transit=s.get("p_transit", 0.3),
                p_slip=s.get("p_slip", 0.1),
                p_guess=s.get("p_guess", 0.2),
                prerequisites=tuple(prereqs_map.get(sid, s.get("prerequisites", []))),
            )
            self._skills[skill.id] = skill

        self._adjacency: dict[str, list[str]] = {
            sid: [] for sid in self._skills
        }
        for sid, skill in self._skills.items():
            for pre_id in skill.prerequisites:
                if pre_id in self._skills:
                    self._adjacency[pre_id].append(sid)

    def get_skill(self, skill_id: str) -> Skill:
        """Trả về skill theo ID. Nếu không tồn tại → raise SkillNotFoundError."""
        if skill_id not in self._skills:
            raise SkillNotFoundError(skill_id)
        return self._skills[skill_id]

    def get_all_skills(self) -> list[Skill]:
        """Trả về tất cả skills trong graph."""
        return list(self._skills.values())

    def get_skills_by_grade(self, grade: int) -> list[Skill]:
        """Lọc skills theo grade."""
        return [s for s in self._skills.values() if s.grade == grade]

    def get_prerequisites(self, skill_id: str) -> list[Skill]:
        """Trả về danh sách skill tiên quyết trực tiếp (1 level)."""
        skill = self.get_skill(skill_id)
        return [self._skills[pid] for pid in skill.prerequisites if pid in self._skills]

    def get_all_prerequisites(self, skill_id: str) -> list[Skill]:
        """Trả về TẤT CẢ skill tiên quyết (recursively, BFS up)."""
        visited: set[str] = set()
        result: list[Skill] = []
        queue = deque([skill_id])

        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)

            if current not in self._skills:
                continue

            skill = self._skills[current]
            for pre_id in skill.prerequisites:
                if pre_id not in visited and pre_id in self._skills:
                    result.append(self._skills[pre_id])
                    queue.append(pre_id)

        return result

    def get_dependents(self, skill_id: str) -> list[Skill]:
        """Trả về các skill phụ thuộc vào skill_id (downstream)."""
        self.get_skill(skill_id)
        return [self._skills[sid] for sid in self._adjacency.get(skill_id, [])]

    def traverse_up(self, skill_id: str) -> list[Skill]:
        """Suy ngược từ skill → tìm chain tiên quyết sâu nhất (topological order).

        Trả về list sắp xếp từ gốc sâu nhất → nông nhất (để BKT ưu tiên
        lấp lỗ hổng từ gốc lên).
        """
        self.get_skill(skill_id)
        all_prereqs = self.get_all_prerequisites(skill_id)
        if not all_prereqs:
            return []

        depth_map: dict[str, int] = {}
        queue: deque[tuple[str, int]] = deque()
        for pre in self.get_prerequisites(skill_id):
            queue.append((pre.id, 1))

        while queue:
            sid, depth = queue.popleft()
            if sid in depth_map:
                continue
            depth_map[sid] = depth
            skill = self._skills.get(sid)
            if skill:
                for pre_id in skill.prerequisites:
                    if pre_id not in depth_map and pre_id in self._skills:
                        queue.append((pre_id, depth + 1))

        sorted_prereqs = sorted(
            [self._skills[sid] for sid in depth_map],
            key=lambda s: depth_map[s.id],
            reverse=True,
        )
        return sorted_prereqs

    def __len__(self) -> int:
        return len(self._skills)

    def __contains__(self, skill_id: str) -> bool:
        return skill_id in self._skills
