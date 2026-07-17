"""Frontend V-Nexus Tutor — đăng nhập + luồng theo vai trò (student/teacher/parent).

Style tham khảo docs/UI/teacher_dashboard_mockup.html (tông tím/indigo, stat card,
badge trạng thái, heatmap) — CSS tiêm vào Streamlit, tương tác thật vẫn qua widget
Streamlit chuẩn (form/nút bấm), không đổi stack.
"""
import os

import requests
import streamlit as st

GATEWAY_URL = os.environ.get("GATEWAY_URL", "http://localhost:8000")

st.set_page_config(page_title="V-Nexus Tutor", layout="wide")

CSS = """
<style>
:root {
  --indigo: #4f46e5; --indigo-dark: #4338ca; --indigo-soft: #eef2ff;
  --orange: #f97316; --yellow: #eab308; --dark: #1e1b2e; --red: #dc2626;
  --muted: #8a8fa3; --border: #ececf3;
}
.stApp { background: #f4f5fa; }
[data-testid="stSidebar"] { background: var(--indigo); }
[data-testid="stSidebar"] * { color: #f5f4ff !important; }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,.2); }

h1, h2, h3 { color: #1f2430 !important; }

.vn-stat-row { display: flex; gap: 14px; margin-bottom: 16px; flex-wrap: wrap; }
.vn-stat {
  flex: 1; min-width: 160px; background: #fff; border: 1px solid var(--border);
  border-radius: 14px; padding: 14px 16px; display: flex; align-items: center; gap: 12px;
}
.vn-stat-icon {
  width: 40px; height: 40px; border-radius: 12px; display: flex; align-items: center;
  justify-content: center; font-size: 18px; color: #fff; flex-shrink: 0;
}
.vn-stat-label { font-size: 12px; color: var(--muted); }
.vn-stat-value { font-size: 20px; font-weight: 700; color: #1f2430; }

.vn-card {
  background: #fff; border: 1px solid var(--border); border-radius: 14px;
  padding: 16px 18px; margin-bottom: 14px;
}

.vn-badge { display: inline-block; padding: 3px 10px; border-radius: 999px; font-size: 11.5px; font-weight: 700; }
.vn-badge-danger { background: #fee2e2; color: #b91c1c; }
.vn-badge-warn { background: #fef3c7; color: #92400e; }
.vn-badge-ok { background: #dcfce7; color: #166534; }

.vn-alert { padding: 10px 12px; border-radius: 10px; background: #fff7ed; border: 1px solid #fed7aa; margin-bottom: 8px; }
.vn-alert-critical { background: #fef2f2; border-color: #fecaca; }
.vn-alert-title { font-weight: 600; font-size: 13px; }
.vn-alert-pct { font-weight: 700; color: #b91c1c; float: right; }

.vn-chip {
  display: inline-flex; gap: 6px; align-items: center; font-size: 12px;
  background: var(--indigo-soft); color: var(--indigo-dark); padding: 4px 10px;
  border-radius: 999px; font-weight: 600; margin: 2px;
}

.vn-row { display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid var(--border); }
.vn-avatar {
  width: 30px; height: 30px; border-radius: 50%; background: var(--indigo-soft); color: var(--indigo);
  display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 12px; flex-shrink: 0;
}
.vn-name { font-weight: 600; font-size: 13px; }
.vn-meta { font-size: 11.5px; color: var(--muted); }
.vn-bar { width: 90px; height: 6px; border-radius: 999px; background: #ece9ff; overflow: hidden; display: inline-block; vertical-align: middle; }
.vn-bar > div { height: 100%; background: var(--indigo); }

.stButton > button { background: var(--indigo); color: #fff; border-radius: 9px; border: none; font-weight: 700; }
.stButton > button:hover { background: var(--indigo-dark); color: #fff; }
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)

STAT_COLORS = {"indigo": "#4f46e5", "orange": "#f97316", "yellow": "#eab308", "dark": "#1e1b2e"}


def stat_row(items: list[tuple]) -> None:
    """items: list of (icon, color_key, label, value)"""
    html = '<div class="vn-stat-row">'
    for icon, color, label, value in items:
        html += (
            f'<div class="vn-stat"><div class="vn-stat-icon" style="background:{STAT_COLORS[color]}">'
            f'{icon}</div><div><div class="vn-stat-label">{label}</div>'
            f'<div class="vn-stat-value">{value}</div></div></div>'
        )
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def badge(level: str, text: str) -> str:
    return f'<span class="vn-badge vn-badge-{level}">{text}</span>'


def mastery_badge(p_mastery: float) -> str:
    if p_mastery < 0.3:
        return badge("danger", "Khẩn cấp")
    if p_mastery < 0.6:
        return badge("warn", "Cần chú ý")
    return badge("ok", "Tốt")


def initials(name: str) -> str:
    parts = name.split()
    return "".join(p[0] for p in parts[:2]).upper()


def _auth_headers() -> dict:
    return {"Authorization": f"Bearer {st.session_state.token}"}


def _api(method: str, path: str, **kwargs):
    response = requests.request(
        method, f"{GATEWAY_URL}{path}", headers=_auth_headers(), timeout=30, **kwargs
    )
    if response.status_code == 401:
        st.session_state.clear()
        st.error("Phiên đăng nhập hết hạn, vui lòng đăng nhập lại.")
        st.rerun()
    return response


def login_form() -> None:
    st.title("V-Nexus Tutor")
    st.caption("Mỗi em một lộ trình, cả trường cùng tiến bộ.")
    with st.form("login"):
        email = st.text_input("Email")
        password = st.text_input("Mật khẩu", type="password")
        submitted = st.form_submit_button("Đăng nhập")

    if submitted:
        resp = requests.post(
            f"{GATEWAY_URL}/auth/jwt/login",
            data={"username": email, "password": password},
            timeout=30,
        )
        if resp.status_code != 200:
            st.error("Sai email hoặc mật khẩu.")
            return

        token = resp.json()["access_token"]
        me = requests.get(
            f"{GATEWAY_URL}/users/me", headers={"Authorization": f"Bearer {token}"}, timeout=30
        ).json()

        st.session_state.token = token
        st.session_state.email = me["email"]
        st.session_state.role = me["role"]
        st.session_state.is_superuser = me["is_superuser"]
        st.rerun()


def student_view() -> None:
    st.header("Học sinh — Bài kiểm tra chẩn đoán & Luyện tập")
    tab_diag, tab_practice = st.tabs(["Bài kiểm tra chẩn đoán", "Lộ trình luyện tập"])

    with tab_diag:
        questions = _api("GET", "/diagnostic/questions").json()
        for q in questions:
            st.markdown('<div class="vn-card">', unsafe_allow_html=True)
            with st.form(f"q_{q['question_id']}"):
                st.write(f"**{q['content']}**")
                if q["options"]:
                    answer = st.radio(
                        "Chọn đáp án", q["options"], key=f"radio_{q['question_id']}"
                    )
                else:
                    answer = st.text_input("Câu trả lời", key=f"text_{q['question_id']}")
                if st.form_submit_button("Nộp câu trả lời"):
                    result = _api(
                        "POST",
                        "/diagnostic/submit-answer",
                        json={"question_id": q["question_id"], "student_answer": answer},
                    ).json()
                    if result["is_correct"]:
                        st.success("Đúng!")
                    else:
                        st.error("Chưa đúng.")
                    st.caption(
                        f"Mastery kỹ năng '{result['skill_code']}': "
                        f"{result['p_mastery_before']:.2f} → {result['p_mastery_after']:.2f}"
                    )
                    for line in result["explanations"]:
                        st.info(line)
            st.markdown("</div>", unsafe_allow_html=True)

        if st.button("Xem gap đã chẩn đoán"):
            complete = _api("POST", "/diagnostic/complete").json()
            st.markdown('<div class="vn-card">', unsafe_allow_html=True)
            st.write("**Lỗ hổng gốc đã phát hiện:**")
            for gap in complete["gaps"]:
                st.markdown(
                    f'<div class="vn-row"><div class="vn-avatar">{initials(gap["skill_name"])[:2]}</div>'
                    f'<div><div class="vn-name">{gap["skill_name"]}</div>'
                    f'<div class="vn-meta">Độ tin cậy {gap["confidence"]:.2f} · Lớp {gap["grade"]}</div></div></div>',
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)

    with tab_practice:
        path = _api("GET", "/practice/path").json()
        st.markdown('<div class="vn-card">', unsafe_allow_html=True)
        if not path:
            st.write("Chưa có gap nào cần luyện tập thêm — hãy làm bài chẩn đoán trước.")
        for item in path:
            st.write(f"**{item['skill_name']}** (độ khó {item['difficulty']}): {item['content']}")
        st.markdown("</div>", unsafe_allow_html=True)


def teacher_view() -> None:
    st.header("Giáo viên — Dashboard lớp học")
    class_id = st.number_input("Mã lớp (class_id)", min_value=1, value=1, step=1)
    if st.button("Tải dashboard"):
        data = _api("GET", f"/teacher/dashboard/{class_id}").json()

        stat_row(
            [
                ("👥", "indigo", "Sĩ số lớp", data["total_students"]),
                ("⚠", "orange", "Học sinh cần chú ý", len(data["priority_ranking"])),
                ("📉", "yellow", "Kỹ năng hổng diện rộng", len(data["class_alerts"])),
                ("✓", "dark", "Nhóm phụ đạo", len(data["groups_by_shared_gap"])),
            ]
        )

        col_heatmap, col_alerts = st.columns([1.3, 1])

        with col_heatmap:
            st.markdown('<div class="vn-card">', unsafe_allow_html=True)
            st.write("**Heatmap kỹ năng — % học sinh còn hổng**")
            st.bar_chart(data["heatmap"])
            st.markdown("</div>", unsafe_allow_html=True)

        with col_alerts:
            st.markdown('<div class="vn-card">', unsafe_allow_html=True)
            st.write("**Cảnh báo lỗ hổng diện rộng**")
            if not data["class_alerts"]:
                st.write("Không có cảnh báo diện rộng.")
            for alert in data["class_alerts"]:
                critical = " vn-alert-critical" if alert["pct_weak"] >= 50 else ""
                st.markdown(
                    f'<div class="vn-alert{critical}">'
                    f'<span class="vn-alert-title">{alert["skill_name"]}</span>'
                    f'<span class="vn-alert-pct">{alert["pct_weak"]}%</span></div>',
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="vn-card">', unsafe_allow_html=True)
        st.write("**Học sinh cần ưu tiên**")
        for row in data["priority_ranking"]:
            st.markdown(
                f'<div class="vn-row">'
                f'<div class="vn-avatar">{initials(row["student_name"])}</div>'
                f'<div style="flex:1"><div class="vn-name">{row["student_name"]}</div>'
                f'<div class="vn-meta">Gốc: {row["root_gap_skill_name"]}</div></div>'
                f'<div class="vn-bar"><div style="width:{row["p_mastery"]*100:.0f}%"></div></div>'
                f'<div class="vn-meta" style="width:70px">Kẹt {row["days_stuck"]}d</div>'
                f'<div>{mastery_badge(row["p_mastery"])}</div>'
                f"</div>",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="vn-card">', unsafe_allow_html=True)
        st.write("**Nhóm học sinh theo lỗ hổng chung**")
        for group in data["groups_by_shared_gap"]:
            chip = f'<span class="vn-chip">● {group["skill_name"]}</span>'
            st.markdown(
                f'{chip} <span class="vn-meta">{", ".join(group["students"])}</span>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)


def parent_view() -> None:
    st.header("Phụ huynh — Tiến độ của con")
    student_id = st.number_input("Mã học sinh (student_id)", min_value=1, value=1, step=1)
    if st.button("Xem tiến độ"):
        resp = _api("GET", f"/parent/dashboard/{student_id}")
        if resp.status_code == 403:
            st.error("Bạn không có quyền xem dữ liệu học sinh này.")
            return
        data = resp.json()

        st.markdown('<div class="vn-card">', unsafe_allow_html=True)
        st.write(f"### 👋 Chào phụ huynh của **{data['student_name']}**")
        if data["stuck_flag"]:
            st.warning(
                f"Con đang kẹt ở '{data['stuck_flag']['skill_name']}' "
                f"({data['stuck_flag']['days_stuck']} ngày)"
            )
        if data["suggested_home_activity"]:
            st.info(f"💡 Gợi ý tại nhà: {data['suggested_home_activity']}")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="vn-card">', unsafe_allow_html=True)
        st.write("**Mastery hiện tại theo kỹ năng**")
        st.bar_chart(data["mastery_snapshot"])
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="vn-card">', unsafe_allow_html=True)
        st.write("**Lịch sử luyện tập gần đây**")
        for entry in data["progress_timeline"][-10:]:
            st.markdown(
                f'<div class="vn-meta">{entry["answered_at"]} — {entry["skill_code"]} '
                f'→ mastery {entry["p_mastery_after"]:.2f}</div>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)


def chat_bubble() -> None:
    """Bong bóng chat nổi góc dưới-phải màn hình (st.popover), không chiếm layout chính."""
    st.markdown(
        """
        <style>
        div[data-testid="stPopover"] {
            position: fixed; bottom: 24px; right: 24px; z-index: 999;
        }
        div[data-testid="stPopover"] > div > button {
            border-radius: 50%; width: 56px; height: 56px; padding: 0;
            font-size: 22px; background: var(--indigo); color: #fff; border: none;
            box-shadow: 0 6px 18px rgba(0,0,0,.25);
        }
        div[data-testid="stPopoverBody"] { width: 340px; max-height: 460px; overflow-y: auto; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    if "history" not in st.session_state:
        st.session_state.history = []

    with st.popover("💬"):
        st.write("**Bot hỏi-đáp**")
        for turn in st.session_state.history:
            role = turn.get("role")
            content = turn.get("content")
            if role in ("user", "assistant") and isinstance(content, str):
                st.chat_message(role).write(content)

        with st.form("chat_bubble_form", clear_on_submit=True):
            message = st.text_input("Nhập câu hỏi...", label_visibility="collapsed")
            sent = st.form_submit_button("Gửi")

        if sent and message:
            history_before = st.session_state.history
            data = _api(
                "POST", "/chat", json={"message": message, "history": history_before}
            ).json()
            st.session_state.history = data["history"]
            st.rerun()


def main() -> None:
    if "token" not in st.session_state:
        login_form()
        return

    with st.sidebar:
        st.markdown("### V-Nexus Tutor")
        st.write(f"Đăng nhập: **{st.session_state.email}**")
        st.write(f"Vai trò: `{st.session_state.role}`")
        st.markdown("---")
        if st.button("Đăng xuất"):
            st.session_state.clear()
            st.rerun()

    role = st.session_state.role
    if role == "student":
        student_view()
    elif role == "teacher":
        teacher_view()
    elif role == "parent":
        parent_view()
    else:
        st.write(f"Chưa có giao diện riêng cho vai trò `{role}` (vd. school_admin).")

    chat_bubble()


main()
