from domain.bkt import (
    BKTParams,
    MasteryState,
    bayes_update,
    find_root_gaps,
    propagate_to_prerequisites,
)


class _FakeGraph:
    """Đồ thị tối giản A → B → C cho test, không phụ thuộc file JSON thật."""

    def __init__(self):
        self._prereqs = {"A": [], "B": ["A"], "C": ["B"]}
        self._depths = {"A": 0, "B": 1, "C": 2}

    def prerequisites_of(self, code):
        return self._prereqs.get(code, [])

    def depth(self, code):
        return self._depths[code]


def _params():
    return BKTParams(p_init=0.4, p_transit=0.1, p_slip=0.1, p_guess=0.2)


def test_correct_answer_increases_mastery():
    p = _params()
    posterior = bayes_update(0.4, True, p.p_slip, p.p_guess, p.p_transit)
    assert posterior > 0.4


def test_incorrect_answer_decreases_mastery():
    p = _params()
    posterior = bayes_update(0.4, False, p.p_slip, p.p_guess, p.p_transit)
    assert posterior < 0.4


def test_mastery_bounded_0_1():
    p = _params()
    prior = 0.4
    for i in range(50):
        prior = bayes_update(prior, i % 2 == 0, p.p_slip, p.p_guess, p.p_transit)
        assert 0.0 <= prior <= 1.0


def test_repeated_correct_converges_toward_mastered():
    p = _params()
    prior = 0.3
    for _ in range(10):
        prior = bayes_update(prior, True, p.p_slip, p.p_guess, p.p_transit)
    assert prior > 0.9


def test_single_incorrect_does_not_propagate():
    graph = _FakeGraph()
    params_by_skill = {"A": _params(), "B": _params(), "C": _params()}
    mastery = {
        "A": MasteryState(p_mastery=0.8),
        "B": MasteryState(p_mastery=0.3, attempts=1),
    }
    trace = propagate_to_prerequisites("B", graph, mastery, params_by_skill)
    assert trace == []
    assert mastery["A"].p_mastery == 0.8


def test_repeated_incorrect_propagates_to_prerequisite():
    graph = _FakeGraph()
    params_by_skill = {"A": _params(), "B": _params(), "C": _params()}
    mastery = {
        "A": MasteryState(p_mastery=0.8),
        "B": MasteryState(p_mastery=0.2, attempts=3),
    }
    trace = propagate_to_prerequisites("B", graph, mastery, params_by_skill)
    assert len(trace) >= 1
    assert mastery["A"].p_mastery < 0.8


def test_propagation_decays_with_depth():
    """Cùng mastery xuất phát cho A và B (loại yếu tố "prior khác nhau" gây nhiễu) —
    chỉ còn hệ số impact = PROPAGATION_DECAY**depth * evidence_strength quyết định độ
    lớn tác động, nên A (depth=1, xa C hơn) phải bị hạ ÍT hơn B (depth=0)."""
    graph = _FakeGraph()
    params_by_skill = {"A": _params(), "B": _params(), "C": _params()}
    mastery = {
        "A": MasteryState(p_mastery=0.2),
        "B": MasteryState(p_mastery=0.2, attempts=3),
        "C": MasteryState(p_mastery=0.1, attempts=3),
    }
    trace = propagate_to_prerequisites("C", graph, mastery, params_by_skill)
    by_skill = {e.skill_code: e for e in trace}
    drop_b = 0.2 - by_skill["B"].p_after
    drop_a = 0.2 - by_skill["A"].p_after
    assert drop_a < drop_b


def test_find_root_gaps_returns_deepest_unmastered_ancestor():
    graph = _FakeGraph()
    mastery = {
        "A": MasteryState(p_mastery=0.2),
        "B": MasteryState(p_mastery=0.3),
        "C": MasteryState(p_mastery=0.3),
    }
    roots = find_root_gaps(graph, mastery)
    assert roots == ["A"]


def test_root_gap_is_the_skill_itself_when_prerequisites_are_strong():
    graph = _FakeGraph()
    mastery = {
        "A": MasteryState(p_mastery=0.9),
        "B": MasteryState(p_mastery=0.9),
        "C": MasteryState(p_mastery=0.2),
    }
    roots = find_root_gaps(graph, mastery)
    assert roots == ["C"]
