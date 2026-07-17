"""Knowledge Graph cho môn Tiếng Anh (CT GDPT 2018).

Đồ thị có hướng: mỗi kỹ năng là một node, cạnh "prerequisites[skill] = [skill_trước]"
nghĩa là để nắm vững `skill` cần trước đó nắm vững các kỹ năng trong danh sách.

Việc truy tìm gốc rễ lỗ hổng (BKT Engine) duyệt ngược theo các cạnh này.
Dữ liệu lấy từ chương trình giáo dục phổ thông môn Tiếng Anh, sách Kết Nối Tri Thức.
"""

# skill_id -> { name, grade }
SKILLS = {
    # Lớp 3 (nền tảng)
    "as3.u1.l1": {"name": "School Vocabulary", "grade": 3},
    "as3.u3.l1": {"name": "Places Around Town", "grade": 3},
    "as3.u4.l1": {"name": "Food and Tableware", "grade": 3},
    # Lớp 3 - Ngữ pháp cơ bản
    "as3.u1.l3": {"name": "Present Simple vs Present Continuous", "grade": 3},
    "as3.u2.l3": {"name": "Adverbs of Frequency", "grade": 3},
    "as3.u3.l3": {"name": "To Be (Present and Past)", "grade": 3},
    "as3.u4.l3": {"name": "Some/Any with Countable/Uncountable Nouns", "grade": 3},
    "as3.u5.l3": {"name": "Past Simple Regular Verbs", "grade": 3},
    "as3.u6.l3": {"name": "Comparatives", "grade": 3},
    "as3.u7.l3": {"name": "Past Simple Irregular Verbs", "grade": 3},
    "as3.u8.l3": {"name": "There Was / There Were", "grade": 3},
    # Lớp 4 - mở rộng thì quá khứ & cấu trúc
    "as4.u1.l3": {"name": "Past Simple Question Forms", "grade": 4},
    "as4.u2.l3": {"name": "Verbs with To + Infinitive", "grade": 4},
    "as4.u3.l3": {"name": "Must / Mustn't", "grade": 4},
    "as4.u4.l3": {"name": "Be Going To (Future)", "grade": 4},
    "as4.u5.l3": {"name": "Can / Could (Ability)", "grade": 4},
    "as4.u6.l3": {"name": "Present Perfect (Intro)", "grade": 4},
    "as4.u7.l3": {"name": "Prepositions of Time & Place", "grade": 4},
    "as4.u8.l3": {"name": "Superlatives", "grade": 4},
    # Lớp 5 - tổng hợp & nâng cao
    "as5.u1.l3": {"name": "Future Simple (Will)", "grade": 5},
    "as5.u2.l3": {"name": "First Conditional", "grade": 5},
    "as5.u3.l3": {"name": "Passive Voice (Present)", "grade": 5},
    "as5.u4.l3": {"name": "Relative Clauses (Who/Which)", "grade": 5},
    "as5.u5.l3": {"name": "Reported Speech (Intro)", "grade": 5},
}

# skill_id -> list các kỹ năng tiên quyết (phải nắm trước)
PREREQUISITES = {
    "as3.u1.l3": ["as3.u1.l1", "as3.u3.l3"],          # Present Simple cần vốn từ & to be
    "as3.u2.l3": ["as3.u1.l3"],                         # Adverbs of frequency dùng với Present Simple
    "as3.u3.l3": ["as3.u1.l1"],                         # To Be cần vốn từ
    "as3.u4.l3": ["as3.u3.l3"],                         # Some/Any cần to be
    "as3.u5.l3": ["as3.u3.l3"],                         # Past Simple Regular cần to be (past)
    "as3.u6.l3": ["as3.u1.l3"],                         # Comparatives cần Present Simple
    "as3.u7.l3": ["as3.u3.l3", "as3.u5.l3"],            # Past Simple Irregular cần to be + past
    "as3.u8.l3": ["as3.u3.l3", "as3.u5.l3"],            # There was/were cần to be + past
    "as4.u1.l3": ["as3.u5.l3", "as3.u7.l3"],            # Past question cần Past Simple
    "as4.u2.l3": ["as3.u1.l3"],                         # To + infinitive cần Present Simple
    "as4.u3.l3": ["as3.u3.l3"],                         # Must cần to be
    "as4.u4.l3": ["as3.u1.l3", "as3.u5.l3"],            # Be going to cần present + past
    "as4.u5.l3": ["as3.u3.l3"],                         # Can/could cần to be
    "as4.u6.l3": ["as3.u5.l3", "as3.u7.l3"],            # Present Perfect cần Past Simple
    "as4.u7.l3": ["as3.u3.l3"],                         # Prepositions cần to be
    "as4.u8.l3": ["as3.u6.l3"],                         # Superlatives cần comparatives
    "as5.u1.l3": ["as3.u1.l3"],                         # Will cần present
    "as5.u2.l3": ["as3.u1.l3", "as3.u5.l3"],            # First conditional cần present + past
    "as5.u3.l3": ["as3.u1.l3", "as3.u5.l3"],            # Passive cần present + past
    "as5.u4.l3": ["as3.u1.l3"],                         # Relative clauses cần present
    "as5.u5.l3": ["as3.u5.l3", "as3.u7.l3"],            # Reported speech cần past
}


def get_skill_name(skill_id: str) -> str:
    return SKILLS.get(skill_id, {}).get("name", skill_id)


def get_prerequisites(skill_id: str) -> list:
    """Trả về danh sách kỹ năng tiên quyết của `skill_id` (rỗng nếu không có)."""
    return list(PREREQUISITES.get(skill_id, []))


def has_skill(skill_id: str) -> bool:
    return skill_id in SKILLS


def trace_root_causes(skill_id: str, mastery_map: dict, threshold: float = 0.5) -> list:
    """Truy ngược tìm gốc rễ lỗ hổng của `skill_id`.

    Duyệt đệ quy các kỹ năng tiên quyết: nếu một tiên quyết cũng dưới ngưỡng thì tiếp
    tục truy ngược. Trả về danh sách skill_id là "gốc" (tiên quyết của nó đã ổn hoặc
    không có tiên quyết, nhưng bản thân nó dưới ngưỡng).
    """
    if not has_skill(skill_id):
        return []

    prob = mastery_map.get(skill_id, {}).get("probability", 1.0)
    if prob >= threshold:
        return []  # kỹ năng này đã ổn, không phải lỗ hổng

    prereqs = get_prerequisites(skill_id)
    if not prereqs:
        return [skill_id]  # đã là gốc

    roots = []
    for p in prereqs:
        sub = trace_root_causes(p, mastery_map, threshold)
        if sub:
            roots.extend(sub)
        elif mastery_map.get(p, {}).get("probability", 1.0) < threshold:
            # tiên quyết dưới ngưỡng nhưng không truy ra gốc con -> chính nó là gốc
            roots.append(p)

    # loại trùng
    return list(dict.fromkeys(roots))
