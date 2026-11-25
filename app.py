import requests
from stream_utils import decode_utf8_chunks

from dotenv import load_dotenv
load_dotenv()  # 强行让网页环境也去读一下 .env 文件

import streamlit as st

import sqlite3
from pathlib import Path

# 侧边栏清空按钮
st.sidebar.title("控制面板")
if st.sidebar.button("清空对话记录"):
    st.session_state.messages = []
    # 调用工具清空本地文件
    from tools import clear_history
    clear_history()
    st.rerun() # 强制刷新网页

# 侧边栏数据库统计
conn = sqlite3.connect(Path(__file__).parent / "grades.db")
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM scores")
count = cursor.fetchone()[0]
conn.close()
st.sidebar.write(f"当前成绩库记录数：**{count}** 条")
# 设置网页标题
st.title("AI Agent 控制台")

# 使用 cache_resource 防止 Streamlit 每次刷新网页时都重新实例化 Agent 导致历史记录丢失
#接入fastapi故删去

# 初始化聊天记录（专门给网页用的）
if "messages" not in st.session_state:
    st.session_state.messages = []

# 把历史聊天记录显示在网页上
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 接收用户输入
if prompt := st.chat_input("请输入你的问题..."):
    # 1. 把用户的话存进网页历史并显示
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # 2. 调用你真正的 Agent
    with st.chat_message("assistant"):
        payload = {"message": prompt}
        res = requests.post("http://127.0.0.1:8000/chat", json=payload, stream=True)


        # 核心修改：写个小生成器，把字节流解码成中文字符串


        response = st.write_stream(decode_utf8_chunks(res.iter_content(chunk_size=None)))

        # 把解码后的水管子交给网页

    # 把 AI 完整回复存进网页的历史记录里
    st.session_state.messages.append({"role": "assistant", "content": response})