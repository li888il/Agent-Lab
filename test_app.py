from streamlit.testing.v1 import AppTest

def test_app_sidebar_clear_button():
    # 1. 启动网页（此时会自动执行 app.py）
    at = AppTest.from_file("app.py").run()

    # 2. 检查网页有没有报错
    assert not at.exception

    # 3. 检查侧边栏有没有那个清空按钮
    assert len(at.sidebar.button) > 0
    clear_btn = at.sidebar.button[0]
    assert clear_btn.label == "清空对话记录"

    # 4. 模拟用户在网页的 session_state 里塞点假聊天记录
    at.session_state["messages"] = [{"role": "user", "content": "测试用的废话"}]

    # 5. 模拟用户点击这个按钮
    clear_btn.click()
    at.run()
    # 6. 按钮点击后，网页会自动重跑，检查记录是不是被清空了
    assert len(at.session_state["messages"]) == 0