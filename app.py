from dotenv import load_dotenv
load_dotenv()  # 强行让网页环境也去读一下 .env 文件


# ... 下面保持你的代码不变 ...
import streamlit as st
from agent import Agent
# 设置网页标题
st.title("🤖 我的 AI Agent 控制台")

# 使用 cache_resource 防止 Streamlit 每次刷新网页时都重新实例化 Agent 导致历史记录丢失
@st.cache_resource
def get_agent():
    return Agent()

agent = get_agent()
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
        with st.spinner("AI 思考中..."):
            # 这里调用的就是 agent.py 里的 reply 方法
            reply = agent.reply(prompt)
            # 把回复显示在网页上
            st.write(reply)

    # 3. 把 AI 的回复也存进网页历史
    st.session_state.messages.append({"role": "assistant", "content": reply})