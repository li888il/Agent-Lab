 from streamlit.testing.v1 import AppTest


def test_能拿到输入框():
    at = AppTest.from_file("app.py").run()
    assert not at.exception
    assert len(at.chat_input) > 0
