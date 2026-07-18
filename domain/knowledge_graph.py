"""Knowledge Graph cho môn Tiếng Anh (CT GDPT 2018).

Đồ thị có hướng: mỗi kỹ năng là một node, cạnh "prerequisites[skill] = [skill_trước]"
nghĩa là để nắm vững `skill` cần trước đó nắm vững các kỹ năng trong danh sách.

Việc truy tìm gốc rễ lỗ hổng (BKT Engine) duyệt ngược theo các cạnh này.

Dữ liệu lấy từ SGK Global Success lớp 3–4 (chương trình công lập), theo
`docs/V-Nexus_Content_Workbook_1.xlsx` (sheet NODE_INPUT). skill_id dùng thẳng
node_id của workbook (VD "G3U04-VOC") để khớp trực tiếp với ngân hàng câu hỏi
sinh từ sheet QUESTION_BANK — không dùng lại namespace Academy Stars (as3.*/as4.*)
cũ, vì hai giáo trình có thứ tự/chủ đề Unit khác nhau, không map 1-1 được.

Phạm vi hiện tại: 8 unit (4 lớp 3 + 4 lớp 4) đã có câu hỏi soạn sẵn trong
QUESTION_BANK (16 node VOC+PAT). 54 node còn lại của NODE_INPUT (gồm PHO/DLG)
chưa có câu hỏi — sẽ bổ sung sau khi content team soạn xong.
"""

# skill_id -> { name, grade }
SKILLS = {
    # Lớp 3
    "G3U04-VOC": {"name": "Bộ phận cơ thể (eyes, nose, hands...)", "grade": 3},
    "G3U04-PAT": {"name": "Touch your... / These are my...", "grade": 3},
    "G3U09-VOC": {"name": "Màu sắc (red, blue, green...)", "grade": 3},
    "G3U09-PAT": {"name": "What colour is it? - It's...", "grade": 3},
    "G3U11-VOC": {"name": "Gia đình (father, mother, brother...)", "grade": 3},
    "G3U11-PAT": {"name": "Who's that? - He's my father", "grade": 3},
    "G3U14-VOC": {"name": "Đồ vật phòng ngủ (bed, lamp, picture...)", "grade": 3},
    "G3U14-PAT": {"name": "Vị trí: in / on / under / behind", "grade": 3},
    # Lớp 4
    "G4U01-VOC": {"name": "Bạn bè & quốc tịch", "grade": 4},
    "G4U01-PAT": {"name": "Where are you from? - I'm from...", "grade": 4},
    "G4U02-VOC": {"name": "Thời gian & giờ", "grade": 4},
    "G4U02-PAT": {"name": "What time is it? - It's...o'clock", "grade": 4},
    "G4U03-VOC": {"name": "Ngày trong tuần & thói quen", "grade": 4},
    "G4U03-PAT": {"name": "What do you do on Mondays? - I...", "grade": 4},
    "G4U05-VOC": {"name": "Khả năng - Things we can do", "grade": 4},
    "G4U05-PAT": {"name": "Can you...? - Yes, I can / No, I can't", "grade": 4},
}

# skill_id -> list các kỹ năng tiên quyết (phải nắm trước)
#
# Quy tắc: (1) trong cùng unit, PAT (mẫu câu) cần VOC (từ vựng) của unit đó;
# (2) giữa các unit, theo đúng thứ tự dạy trong NODE_INPUT — chuỗi tuyến tính
# đơn giản hoá, chấp nhận được cho MVP khi chưa có chuyên gia rà soát quan hệ
# tiên quyết thật xuyên unit (cùng giả định mà bản dump knowledge-graph.json cũ
# đã ghi chú).
PREREQUISITES = {
    "G3U04-PAT": ["G3U04-VOC"],
    "G3U09-VOC": ["G3U04-PAT"],
    "G3U09-PAT": ["G3U09-VOC"],
    "G3U11-VOC": ["G3U09-PAT"],
    "G3U11-PAT": ["G3U11-VOC"],
    "G3U14-VOC": ["G3U11-PAT"],
    "G3U14-PAT": ["G3U14-VOC"],
    "G4U01-VOC": ["G3U14-PAT"],
    "G4U01-PAT": ["G4U01-VOC"],
    "G4U02-VOC": ["G4U01-PAT"],
    "G4U02-PAT": ["G4U02-VOC"],
    "G4U03-VOC": ["G4U02-PAT"],
    "G4U03-PAT": ["G4U03-VOC"],
    "G4U05-VOC": ["G4U03-PAT"],
    "G4U05-PAT": ["G4U05-VOC"],
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
