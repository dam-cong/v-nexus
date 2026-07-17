"""Kiểm thử BKT Engine (docs/ai-danh-gia.md §2.5)."""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from domain.bkt import (
    ROOT_THRESHOLD,
    PRIOR,
    compute_mastery,
    diagnose_gaps,
    update_probability,
)
from domain.knowledge_graph import trace_root_causes


def _mk_answers(skill_id, n_correct, n_wrong):
    ans = []
    for _ in range(n_correct):
        ans.append({"question_id": f"q_c_{skill_id}_{_}", "skill_id": skill_id, "correct": True})
    for _ in range(n_wrong):
        ans.append({"question_id": f"q_w_{skill_id}_{_}", "skill_id": skill_id, "correct": False})
    return ans


def test_correct_increases():
    p = PRIOR
    for _ in range(10):
        p = update_probability(p, True)
    assert p > 0.9, f"xác suất phải tiệm cận cao khi đúng liên tục, got {p}"


def test_wrong_decreases():
    p = PRIOR
    for _ in range(10):
        p = update_probability(p, False)
    # xác suất phải giảm rõ rệt so với prior (transit giữ nó không xuống sát 0)
    assert p < 0.4, f"xác suất phải giảm khi sai liên tục, got {p}"


def test_root_cause_tracing():
    # Học sinh làm sai as3.u8.l3 (There was/were) do yếu gốc as3.u3.l3 (To Be)
    mastery = compute_mastery(_mk_answers("as3.u8.l3", 0, 3))
    # To Be (as3.u3.l3) là tiên quyết, giả định cũng yếu (default prior)
    gaps = diagnose_gaps(mastery)
    gap_ids = {g["skill_id"] for g in gaps}
    assert "as3.u8.l3" in gap_ids
    # truy ngược phải chỉ ra as3.u3.l3 là gốc (vì prior < ROOT_THRESHOLD)
    assert "as3.u3.l3" in gap_ids


def test_no_gap_when_mastered():
    mastery = compute_mastery(_mk_answers("as3.u1.l3", 10, 0))
    gaps = diagnose_gaps(mastery)
    assert all(g["skill_id"] != "as3.u1.l3" for g in gaps)


def test_unknown_skill_fallback():
    mastery = compute_mastery(_mk_answers("xxx.unknown", 0, 1))
    gaps = diagnose_gaps(mastery)
    assert any(g["skill_id"] == "xxx.unknown" and g["status"] == "unknown" for g in gaps)


def test_trace_root_causes_empty_when_ok():
    mastery = {"as3.u8.l3": {"probability": 0.9}}
    assert trace_root_causes("as3.u8.l3", mastery) == []


if __name__ == "__main__":
    test_correct_increases()
    test_wrong_decreases()
    test_root_cause_tracing()
    test_no_gap_when_mastered()
    test_unknown_skill_fallback()
    test_trace_root_causes_empty_when_ok()
    print("All BKT tests passed.")
