"""Adaptive Test — Computerized Adaptive Testing (CAT).

Sau mỗi câu, chọn câu tiếp theo nhắm vào skill có entropy cao nhất
(trong phân phối mastery) → ít câu hơn, chẩn đoán chính xác hơn.

Giống cơ chế TOEFL/GRE.
"""
from __future__ import annotations

import logging
import math
import random
from dataclasses import dataclass, field

from ai.bkt_engine import BKTEngine, MASTERY_THRESHOLD
from ai.knowledge_graph import KnowledgeGraph
from tools.question_bank import QuestionBank, Question

logger = logging.getLogger(__name__)


@dataclass
class TestSession:
    student_id: str
    skills_to_test: list[str]
    answers: list[dict] = field(default_factory=list)
    current_skill: str | None = None
    current_question: Question | None = None
    is_complete: bool = False
    total_questions: int = 0
    max_questions: int = 15


@dataclass
class CATResult:
    student_id: str
    total_questions: int
    skills_assessed: list[str]
    mastery_snapshot: dict[str, float]
    gaps_found: list[dict]
    efficiency_ratio: float


class AdaptiveTestEngine:
    """CAT Engine — chọn câu tiếp theo dựa trên entropy của mastery distribution."""

    def __init__(
        self,
        engine: BKTEngine,
        kg: KnowledgeGraph,
        bank: QuestionBank,
    ) -> None:
        self.engine = engine
        self.kg = kg
        self.bank = bank
        self._sessions: dict[str, TestSession] = {}

    def _calculate_entropy(self, mastery: float) -> float:
        """Tính entropy của Bernoulli distribution với p = mastery.

       Entropy cao → nhiều bất định nhất → cần hỏi thêm.
        """
        p = max(mastery, 0.001)
        q = 1.0 - p
        q = max(q, 0.001)
        return -(p * math.log2(p) + q * math.log2(q))

    def _select_next_skill(self, student_id: str, tested_skills: set[str]) -> str | None:
        """Chọn skill có entropy cao nhất chưa test."""
        mastery_map = self.engine.get_all_mastery(student_id)

        candidates = []
        for skill_id, mastery in mastery_map.items():
            if skill_id in tested_skills:
                continue
            if self.bank.get_by_skill(skill_id):
                entropy = self._calculate_entropy(mastery)
                candidates.append((skill_id, entropy))

        if not candidates:
            all_skills = [s.id for s in self.kg.get_all_skills() if self.bank.get_by_skill(s.id)]
            untested = [s for s in all_skills if s not in tested_skills]
            if untested:
                return untested[0]
            return None

        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]

    def _select_question(self, skill_id: str) -> Question | None:
        """Chọn câu hỏi phù hợp cho skill."""
        mastery = self.engine.get_mastery("temp", skill_id)
        if mastery < 0.3:
            difficulty = 1
        elif mastery < 0.6:
            difficulty = 2
        else:
            difficulty = 3

        questions = self.bank.get_by_skill(skill_id, difficulty)
        if not questions:
            questions = self.bank.get_by_skill(skill_id)

        if not questions:
            return None

        asked_ids = set()
        available = [q for q in questions if q.id not in asked_ids]
        if not available:
            return questions[0]

        return random.choice(available)

    def start_session(
        self,
        student_id: str,
        skills_to_test: list[str] | None = None,
        max_questions: int = 15,
    ) -> TestSession:
        """Bắt đầu phiên test mới."""
        if skills_to_test is None:
            skills_to_test = [s.id for s in self.kg.get_all_skills() if self.bank.get_by_skill(s.id)]

        session = TestSession(
            student_id=student_id,
            skills_to_test=skills_to_test,
            max_questions=max_questions,
        )
        self._sessions[student_id] = session
        return session

    def get_next_question(self, student_id: str) -> dict | None:
        """Lấy câu hỏi tiếp theo trong phiên test."""
        session = self._sessions.get(student_id)
        if not session:
            return None

        if session.total_questions >= session.max_questions:
            session.is_complete = True
            return None

        tested_skills = {a["skill_id"] for a in session.answers}
        next_skill = self._select_next_skill(student_id, tested_skills)

        if not next_skill:
            session.is_complete = True
            return None

        question = self._select_question(next_skill)
        if not question:
            session.is_complete = True
            return None

        session.current_skill = next_skill
        session.current_question = question

        return {
            "question_id": question.id,
            "skill_id": question.skill_id,
            "content": question.content,
            "options": list(question.options),
            "question_number": session.total_questions + 1,
            "max_questions": session.max_questions,
        }

    def submit_answer(
        self,
        student_id: str,
        question_id: str,
        selected_option: int,
    ) -> dict:
        """Gửi câu trả lời và nhận kết quả."""
        session = self._sessions.get(student_id)
        if not session:
            return {"error": "Không tìm thấy phiên test."}

        if not session.current_question:
            return {"error": "Không có câu hỏi hiện tại."}

        if question_id != session.current_question.id:
            return {"error": "question_id không khớp với câu hỏi hiện tại."}

        correct = selected_option == session.current_question.correct_answer
        skill_id = session.current_question.skill_id

        self.engine.update(student_id, skill_id, correct)

        session.answers.append({
            "question_id": question_id,
            "skill_id": skill_id,
            "correct": correct,
            "selected_option": selected_option,
        })
        session.total_questions += 1

        if session.total_questions >= session.max_questions:
            session.is_complete = True

        return {
            "correct": correct,
            "correct_answer": session.current_question.correct_answer,
            "correct_option": session.current_question.options[session.current_question.correct_answer],
            "mastery_after": self.engine.get_mastery(student_id, skill_id),
            "is_complete": session.is_complete,
            "questions_remaining": session.max_questions - session.total_questions,
        }

    def finish_session(self, student_id: str) -> CATResult | None:
        """Kết thúc phiên test và trả về kết quả tổng hợp."""
        session = self._sessions.get(student_id)
        if not session:
            return None

        session.is_complete = True
        mastery_snapshot = self.engine.get_all_mastery(student_id)

        tested_skills = list({a["skill_id"] for a in session.answers})
        gaps = []
        for skill_id in tested_skills:
            mastery = mastery_snapshot.get(skill_id, 0.5)
            if mastery < MASTERY_THRESHOLD:
                try:
                    skill = self.kg.get_skill(skill_id)
                    gaps.append({
                        "skill_id": skill_id,
                        "skill_name": skill.name_vi,
                        "mastery": mastery,
                    })
                except Exception:
                    gaps.append({
                        "skill_id": skill_id,
                        "skill_name": skill_id,
                        "mastery": mastery,
                    })

        correct_count = sum(1 for a in session.answers if a["correct"])
        efficiency = correct_count / session.total_questions if session.total_questions > 0 else 0

        return CATResult(
            student_id=student_id,
            total_questions=session.total_questions,
            skills_assessed=tested_skills,
            mastery_snapshot=mastery_snapshot,
            gaps_found=gaps,
            efficiency_ratio=round(efficiency, 2),
        )

    def get_session(self, student_id: str) -> TestSession | None:
        return self._sessions.get(student_id)
