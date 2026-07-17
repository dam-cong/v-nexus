import pytest

from domain.knowledge_graph import CyclicGraphError, KnowledgeGraph, load_knowledge_graph


def test_load_graph_from_json():
    graph = load_knowledge_graph()
    codes = graph.skill_codes()
    assert len(codes) == 8
    assert "TA3.U5.GRAM_HOWMANY" in codes
    assert "TA3.U5.LISTEN_HOWMANY" in codes


def test_prerequisites_of_returns_expected_parents():
    graph = load_knowledge_graph()
    prereqs = set(graph.prerequisites_of("TA3.U5.GRAM_HOWMANY"))
    assert prereqs == {
        "TA3.PRE.NUM0110",
        "TA3.PRE.NOUN_PLURAL",
        "TA3.U5.VOCAB_TOYS_PLURAL",
    }


def test_graph_is_acyclic():
    data = {
        "skills": [
            {"code": "X", "name_vi": "x", "name_en": "x", "grade": 3, "unit": "U1",
             "skill_type": "vocab", "p_init": 0.4, "p_transit": 0.1, "p_slip": 0.1, "p_guess": 0.2},
            {"code": "Y", "name_vi": "y", "name_en": "y", "grade": 3, "unit": "U1",
             "skill_type": "vocab", "p_init": 0.4, "p_transit": 0.1, "p_slip": 0.1, "p_guess": 0.2},
        ],
        "edges": [
            {"prerequisite": "X", "dependent": "Y", "weight": 1.0},
            {"prerequisite": "Y", "dependent": "X", "weight": 1.0},
        ],
    }
    with pytest.raises(CyclicGraphError):
        KnowledgeGraph(data)
