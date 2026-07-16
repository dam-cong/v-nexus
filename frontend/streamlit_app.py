"""Frontend chat đơn giản — gọi Gateway qua HTTP. Không cần đẹp, chỉ cần chạy được."""
import os

import requests
import streamlit as st

GATEWAY_URL = os.environ.get("GATEWAY_URL", "http://localhost:8000")

st.set_page_config(page_title="V-Nexus")
st.title("V-Nexus")

if "history" not in st.session_state:
    st.session_state.history = []

for turn in st.session_state.history:
    role = turn.get("role")
    content = turn.get("content")
    if role in ("user", "assistant") and isinstance(content, str):
        st.chat_message(role).write(content)

message = st.chat_input("Nhập tin nhắn...")
if message:
    st.chat_message("user").write(message)
    response = requests.post(
        f"{GATEWAY_URL}/chat",
        json={"message": message, "history": st.session_state.history},
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()
    st.session_state.history = data["history"]
    st.chat_message("assistant").write(data["reply"])
