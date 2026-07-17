"""Load & truy vấn đồ thị tri thức tiên quyết từ domain/data/knowledge_graph.json."""
import json
from collections import defaultdict
from pathlib import Path

from domain.bkt import BKTParams

DATA_PATH = Path(__file__).parent / "data" / "knowledge_graph.json"


class CyclicGraphError(ValueError):
    pass


class KnowledgeGraph:
    def __init__(self, data: dict):
        self._skills = {s["code"]: s for s in data["skills"]}
        self._prerequisites: dict[str, list[str]] = defaultdict(list)
        self._dependents: dict[str, list[str]] = defaultdict(list)
        for edge in data["edges"]:
            self._prerequisites[edge["dependent"]].append(edge["prerequisite"])
            self._dependents[edge["prerequisite"]].append(edge["dependent"])
        self._check_acyclic()
        self._depth_cache: dict[str, int] = {}

    def _check_acyclic(self) -> None:
        visiting, visited = set(), set()

        def visit(code: str) -> None:
            if code in visited:
                return
            if code in visiting:
                raise CyclicGraphError(f"Đồ thị tri thức có chu trình tại '{code}'")
            visiting.add(code)
            for dep in self._dependents.get(code, []):
                visit(dep)
            visiting.remove(code)
            visited.add(code)

        for code in self._skills:
            visit(code)

    def skill_codes(self) -> list[str]:
        return list(self._skills.keys())

    def skill_name(self, code: str) -> str:
        return self._skills[code]["name_vi"]

    def skill(self, code: str) -> dict:
        return self._skills[code]

    def bkt_params(self, code: str) -> BKTParams:
        s = self._skills[code]
        return BKTParams(
            p_init=s["p_init"], p_transit=s["p_transit"], p_slip=s["p_slip"], p_guess=s["p_guess"]
        )

    def prerequisites_of(self, code: str) -> list[str]:
        return list(self._prerequisites.get(code, []))

    def dependents_of(self, code: str) -> list[str]:
        return list(self._dependents.get(code, []))

    def depth(self, code: str) -> int:
        """Số tầng từ node gốc (không tiên quyết) tới skill này — dùng để sort root gaps."""
        if code in self._depth_cache:
            return self._depth_cache[code]
        prereqs = self._prerequisites.get(code, [])
        d = 0 if not prereqs else 1 + max(self.depth(p) for p in prereqs)
        self._depth_cache[code] = d
        return d


def load_knowledge_graph(path: Path = DATA_PATH) -> KnowledgeGraph:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return KnowledgeGraph(data)
