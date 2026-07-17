"""BKT Engine — Bayesian Knowledge Tracing.

Cập nhật mastery probability theo BKT formula, suy ngược qua Knowledge Graph
để tìm root cause của lỗ hổng kiến thức.

Lưu trữ: in-memory dict (primary) — PostgreSQL fallback khi cần persist.
"""
from __future__ import annotations

import logging
from collections import deque
from dataclasses import dataclass, field

from ai.knowledge_graph import KnowledgeGraph, Skill, SkillNotFoundError

logger = logging.getLogger(__name__)

MASTERY_THRESHOLD = 0.5


@dataclass
class GapResult:
    skill_id: str
    skill_name: str
    mastery_prob: float
    gap_depth: int
    grade: int
    explanation: str
    recommended_action: str


class BKTEngine:
    """Bayesian Knowledge Tracing engine.

    Lưu mastery probability từng skill cho từng học sinh,
    cập nhật theo công thức Bayes, và truy gốc qua prerequisite graph.
    """

    def __init__(self, kg: KnowledgeGraph) -> None:
        self.kg = kg
        self._mastery: dict[str, dict[str, float]] = {}
        self._history: dict[str, list[dict]] = {}

    def _init_student(self, student_id: str) -> None:
        if student_id not in self._mastery:
            self._mastery[student_id] = {}
            self._history[student_id] = []

    def get_mastery(self, student_id: str, skill_id: str) -> float:
        """Lấy mastery probability hiện tại. Nếu chưa có → trả p_init."""
        self._init_student(student_id)
        if skill_id not in self._mastery[student_id]:
            try:
                skill = self.kg.get_skill(skill_id)
                self._mastery[student_id][skill_id] = skill.p_init
                logger.debug(
                    "Student %s, skill %s: dùng p_init=%.2f (mới)",
                    student_id, skill_id, skill.p_init,
                )
            except SkillNotFoundError:
                raise
        return self._mastery[student_id][skill_id]

    def get_all_mastery(self, student_id: str) -> dict[str, float]:
        """Lấy mastery map của student (tất cả skills đã cập nhật)."""
        self._init_student(student_id)
        result: dict[str, float] = {}
        for skill in self.kg.get_all_skills():
            result[skill.id] = self.get_mastery(student_id, skill.id)
        return result

    def _bayes_update_correct(self, skill: Skill, mastery: float) -> float:
        """P(L | correct) = P(correct | L) * P(L) / P(correct).

        P(correct) = P(correct | L) * P(L) + P(correct | ¬L) * P(¬L)
        P(correct | L) = 1 - p_slip
        P(correct | ¬L) = p_guess
        """
        p_correct_given_L = 1.0 - skill.p_slip
        p_correct_given_not_L = skill.p_guess
        p_correct = p_correct_given_L * mastery + p_correct_given_not_L * (1.0 - mastery)
        if p_correct == 0:
            return mastery
        posterior = (p_correct_given_L * mastery) / p_correct
        return min(max(posterior, 0.001), 0.999)

    def _bayes_update_incorrect(self, skill: Skill, mastery: float) -> float:
        """P(L | incorrect) = P(incorrect | L) * P(L) / P(incorrect).

        P(incorrect) = P(incorrect | L) * P(L) + P(incorrect | ¬L) * P(¬L)
        P(incorrect | L) = p_slip
        P(incorrect | ¬L) = 1 - p_guess
        """
        p_incorrect_given_L = skill.p_slip
        p_incorrect_given_not_L = 1.0 - skill.p_guess
        p_incorrect = p_incorrect_given_L * mastery + p_incorrect_given_not_L * (1.0 - mastery)
        if p_incorrect == 0:
            return mastery
        posterior = (p_incorrect_given_L * mastery) / p_incorrect
        return min(max(posterior, 0.001), 0.999)

    def _apply_transit(self, skill: Skill, mastery: float) -> float:
        """Áp dụng transition probability: mastery mới = mastery + (1 - mastery) * p_transit.

        Mô hình: sau khi học, có p_transit probability chuyển từ ¬L → L.
        """
        new_mastery = mastery + (1.0 - mastery) * skill.p_transit
        return min(new_mastery, 0.999)

    def update(self, student_id: str, skill_id: str, correct: bool) -> float:
        """Cập nhật mastery của 1 skill. Trả về mastery probability mới.

        Args:
            student_id: ID học sinh
            skill_id: ID kỹ năng
            correct: True nếu trả lời đúng, False nếu sai

        Returns:
            Mastery probability sau khi cập nhật
        """
        skill = self.kg.get_skill(skill_id)
        current = self.get_mastery(student_id, skill_id)

        if correct:
            updated = self._bayes_update_correct(skill, current)
        else:
            updated = self._bayes_update_incorrect(skill, current)

        self._mastery[student_id][skill_id] = updated

        self._history[student_id].append({
            "skill_id": skill_id,
            "correct": correct,
            "mastery_before": current,
            "mastery_after": updated,
        })

        logger.debug(
            "Student %s, skill %s: %s → mastery %.4f (was %.4f)",
            student_id, skill_id,
            "đúng" if correct else "sai",
            updated, current,
        )
        return updated

    def batch_update(
        self, student_id: str, answers: list[dict]
    ) -> dict[str, float]:
        """Cập nhật nhiều câu trả lời một lúc.

        Args:
            student_id: ID học sinh
            answers: list of {"skill_id": str, "correct": bool}

        Returns:
            Mastery map sau khi cập nhật tất cả
        """
        for ans in answers:
            self.update(student_id, ans["skill_id"], ans["correct"])
        return self.get_all_mastery(student_id)

    def diagnose_root_cause(
        self,
        student_id: str,
        wrong_skill_id: str,
        threshold: float = MASTERY_THRESHOLD,
    ) -> list[GapResult]:
        """Truy gốc: từ skill sai → suy ngược graph → tìm root cause.

        Thuật toán BFS:
        1. Kiểm tra mastery của wrong_skill_id
        2. Nếu mastery >= threshold → skill này OK, trả về []
        3. BFS traverse UP qua prerequisites
        4. Với mỗi prerequisite: kiểm tra mastery, nếu < threshold → thêm vào gaps
        5. Sắp xếp theo gap_depth descending (sâu nhất đầu)
        6. Generate explanation và recommended_action
        """
        self._init_student(student_id)
        wrong_mastery = self.get_mastery(student_id, wrong_skill_id)

        if wrong_mastery >= threshold:
            logger.debug(
                "Skill %s mastery %.2f >= %.2f → không có gap",
                wrong_skill_id, wrong_mastery, threshold,
            )
            return []

        gap_depth_map: dict[str, int] = {}
        queue: deque[tuple[str, int]] = deque()

        wrong_skill = self.kg.get_skill(wrong_skill_id)
        for pre_id in wrong_skill.prerequisites:
            if pre_id in self.kg:
                queue.append((pre_id, 1))

        while queue:
            sid, depth = queue.popleft()
            if sid in gap_depth_map:
                continue

            mastery = self.get_mastery(student_id, sid)
            if mastery < threshold:
                gap_depth_map[sid] = depth
                skill = self.kg.get_skill(sid)
                for pre_id in skill.prerequisites:
                    if pre_id not in gap_depth_map and pre_id in self.kg:
                        queue.append((pre_id, depth + 1))

        if not gap_depth_map:
            return []

        results: list[GapResult] = []
        for sid, depth in sorted(gap_depth_map.items(), key=lambda x: x[1], reverse=True):
            skill = self.kg.get_skill(sid)
            mastery = self.get_mastery(student_id, sid)
            explanation = self._generate_explanation(
                student_id, sid, skill, mastery, depth, wrong_skill_id, wrong_mastery
            )
            recommended = self._generate_recommendation(sid, skill, mastery, depth)

            results.append(GapResult(
                skill_id=sid,
                skill_name=skill.name_vi,
                mastery_prob=round(mastery, 4),
                gap_depth=depth,
                grade=skill.grade,
                explanation=explanation,
                recommended_action=recommended,
            ))

        return results

    def _generate_explanation(
        self,
        student_id: str,
        skill_id: str,
        skill: Skill,
        mastery: float,
        depth: int,
        wrong_skill_id: str,
        wrong_mastery: float,
    ) -> str:
        """Tạo câu giải thích cho gap."""
        mastery_pct = round(mastery * 100)
        if depth == 0:
            return (
                f"Học sinh chưa nắm vững '{skill.name_vi}' "
                f"(chỉ đúng ~{mastery_pct}%)."
            )
        return (
            f"Sai ở '{self.kg.get_skill(wrong_skill_id).name_vi}' "
            f"vì chưa vững '{skill.name_vi}' (mastery ~{mastery_pct}%, "
            f"tiên quyết cấp {depth})."
        )

    def _generate_recommendation(
        self,
        skill_id: str,
        skill: Skill,
        mastery: float,
        depth: int,
    ) -> str:
        """Tạo gợi ý hành động tiếp theo."""
        mastery_pct = round(mastery * 100)
        if mastery_pct < 20:
            action = "cần học lại từ đầu"
        elif mastery_pct < 40:
            action = "cần luyện tập cơ bản"
        else:
            action = "cần luyện tập thêm để vững hơn"
        return (
            f"Ưu tiên {action} '{skill.name_vi}' "
            f"(chương {skill.unit}, lớp {skill.grade}) "
            f"trước khi luyện tập tiếp."
        )

    def get_student_history(self, student_id: str) -> list[dict]:
        """Lấy lịch sử cập nhật mastery của student."""
        self._init_student(student_id)
        return list(self._history[student_id])

    def reset_student(self, student_id: str) -> None:
        """Xóa toàn bộ mastery và history của student."""
        self._mastery.pop(student_id, None)
        self._history.pop(student_id, None)
