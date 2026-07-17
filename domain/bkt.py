"""Bayesian Knowledge Tracing thuần (không DB/async) — lõi chẩn đoán tường minh.

Đây KHÔNG phải nơi LLM đoán gap. Mọi kết luận đều là công thức Bayes in ra được từng
bước, để tránh đúng cái bẫy "gọi LLM cho mọi thứ" (xem docs/PHAN_TICH_DE_ADAPTIVE_TUTORING.md).
"""
from dataclasses import dataclass, field

MASTERED_THRESHOLD = 0.6
FAIL_THRESHOLD = 0.5
MIN_ATTEMPTS_FOR_PROPAGATION = 2
PROPAGATION_DECAY = 0.6
MAX_PROPAGATION_DEPTH = 3


@dataclass
class BKTParams:
    p_init: float = 0.4
    p_transit: float = 0.1
    p_slip: float = 0.1
    p_guess: float = 0.2


@dataclass
class MasteryState:
    p_mastery: float
    attempts: int = 0
    correct_count: int = 0


@dataclass
class PropagationEvent:
    skill_code: str
    p_before: float
    p_after: float
    reason_skill_code: str
    depth: int


def bayes_update(
    p_prior: float, is_correct: bool, p_slip: float, p_guess: float, p_transit: float
) -> float:
    """Cập nhật xác suất nắm vững 1 kỹ năng theo 1 câu trả lời (Corbett & Anderson)."""
    if is_correct:
        p_evidence = (p_prior * (1 - p_slip)) / (
            p_prior * (1 - p_slip) + (1 - p_prior) * p_guess
        )
    else:
        p_evidence = (p_prior * p_slip) / (
            p_prior * p_slip + (1 - p_prior) * (1 - p_guess)
        )
    p_posterior = p_evidence + (1 - p_evidence) * p_transit
    return min(max(p_posterior, 0.0), 1.0)


def propagate_to_prerequisites(
    skill_code: str,
    graph,
    mastery: dict[str, MasteryState],
    params_by_skill: dict[str, BKTParams],
    depth: int = 0,
    trace: list[PropagationEvent] | None = None,
    evidence_strength: float | None = None,
) -> list[PropagationEvent]:
    """Lan truyền ngược: học sinh hổng dai dẳng ở 1 skill → hạ mastery của tiên quyết.

    Heuristic giải thích được, không phải mạng Bayes đầy đủ — chủ động thu gọn phạm vi
    cho hackathon 48h (xem lý do trong docs/KE_HOACH_TRIEN_KHAI.md).

    `evidence_strength` được tính DUY NHẤT 1 lần từ skill gốc gây lan truyền, rồi chỉ
    suy giảm theo `PROPAGATION_DECAY ** depth` qua các tầng — KHÔNG tính lại từ mastery
    (đã bị hạ) của từng tổ tiên trung gian, tránh compounding kép khiến tổ tiên xa lại
    bị hạ mạnh hơn tổ tiên gần (đã phát hiện qua test, xem tests/test_bkt.py).
    """
    trace = trace if trace is not None else []
    state = mastery.get(skill_code)
    if state is None:
        return trace

    if evidence_strength is None:
        # Lệnh gọi gốc: gate theo chính skill vừa được trả lời.
        if state.attempts < MIN_ATTEMPTS_FOR_PROPAGATION or state.p_mastery >= FAIL_THRESHOLD:
            return trace
        evidence_strength = (FAIL_THRESHOLD - state.p_mastery) / FAIL_THRESHOLD

    if depth >= MAX_PROPAGATION_DEPTH:
        return trace

    for prereq_code in graph.prerequisites_of(skill_code):
        prereq_state = mastery.setdefault(
            prereq_code, MasteryState(p_mastery=params_by_skill[prereq_code].p_init)
        )
        params = params_by_skill[prereq_code]
        posterior_if_wrong = bayes_update(
            prereq_state.p_mastery,
            is_correct=False,
            p_slip=params.p_slip,
            p_guess=params.p_guess,
            p_transit=0.0,
        )
        impact = (PROPAGATION_DECAY**depth) * evidence_strength
        p_before = prereq_state.p_mastery
        p_after = p_before + impact * (posterior_if_wrong - p_before)
        prereq_state.p_mastery = p_after

        trace.append(
            PropagationEvent(
                skill_code=prereq_code,
                p_before=p_before,
                p_after=p_after,
                reason_skill_code=skill_code,
                depth=depth,
            )
        )
        propagate_to_prerequisites(
            prereq_code,
            graph,
            mastery,
            params_by_skill,
            depth + 1,
            trace,
            evidence_strength=evidence_strength,
        )
    return trace


def find_root_gaps(
    graph, mastery: dict[str, MasteryState], threshold: float = MASTERED_THRESHOLD
) -> list[str]:
    """Trả về skill hổng sâu nhất mà tiên quyết của nó KHÔNG hổng (frontier of failing subgraph)."""
    weak = {code for code, state in mastery.items() if state.p_mastery < threshold}
    roots = [
        code
        for code in weak
        if not any(p in weak for p in graph.prerequisites_of(code))
    ]
    return sorted(roots, key=lambda code: (mastery[code].p_mastery, -graph.depth(code)))


def explain_trace(trace: list[PropagationEvent], graph) -> list[str]:
    """Sinh câu giải thích tiếng Việt từ propagation trace — không phải LLM đoán."""
    lines = []
    for event in trace:
        skill_name = graph.skill_name(event.skill_code)
        reason_name = graph.skill_name(event.reason_skill_code)
        lines.append(
            f"Hổng lặp lại ở '{reason_name}' → hạ mastery '{skill_name}' từ "
            f"{event.p_before:.2f} xuống {event.p_after:.2f}."
        )
    return lines
