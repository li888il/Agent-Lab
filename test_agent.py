from tools import TOOLS, get_grades, write_note, clear_history
import json
import os
from pathlib import Path
from agent import Agent

os.environ["DEEPSEEK_API_KEY"] = "sk-fake-key-just-for-test" # 强行塞个假钥匙

# 伪造一个假大模型的回复，专门用来骗过 API 请求
class FakeMessage:
    def __init__(self, content):
        self.content = content


class FakeChoice:
    def __init__(self, content):
        self.message = FakeMessage(content)


class FakeResponse:
    def __init__(self, content):
        self.choices = [FakeChoice(content)]


# 1. 模拟流式吐出的每一个“水滴”
class FakeStreamChunk:
    def __init__(self, content):
        # 模拟 delta 结构：chunk.choices[0].delta.content
        self.choices = [type('Choice', (), {'delta': type('Delta', (), {'content': content})})]

# 2. 假客户端（注意看 create 方法里的 yield）
class FakeClient:
    def __init__(self, fake_reply):
        self.fake_reply = fake_reply
        self.chat = self
        self.completions = self

    def create(self, *args, **kwargs):
        # 大白话：只要 agent.py 敢用 for 循环遍历，我就把一个长句子
        # 拆成一个个字，像挤牙膏一样 yield 出去。
        def stream_generator():
            for char in self.fake_reply:
                yield FakeStreamChunk(char)
        return stream_generator()



# 测核心逻辑：假大模型让存笔记，看代码有没有真存
def test_agent_reply_with_tool():
    # 1. 伪造大模型返回一段要调工具的 JSON
    fake_json = '{"tool": "write_note", "filename": "mock_test.txt", "content": "假AI写的"}'

    # 2. 实例化 Agent
    agent = Agent()

    # 3. 偷梁换柱：把真实的联网 client 换掉
    agent.client = FakeClient(fake_json)

    # 4. 触发回复
    # 核心：用 "".join() 把生成器里蹦出来的每一个字，重新拼成一整段话！
    result = "".join(agent.reply("帮我记个笔记"))

    # 然后再去断言
    assert "写入成功" in result
    # 5. 断言：看代码是不是真的执行了工具并返回了成功
    assert "写入成功" in result

# 1. 测注册表
def test_tools_registry_has_three_tools():
    assert "write_note" in TOOLS
    assert "get_grades" in TOOLS
    assert "clear_history" in TOOLS


# 2. 测查成绩
def test_get_grades():
    assert "67" in get_grades("张三", "数学")
    assert "查不到" in get_grades("王五", "数学")


# 3. 测写笔记
def test_write_note():
    result = write_note("test_file.txt", "这是一条测试")
    assert "写入成功" in result
    # 顺手删掉测试文件
    file_path = Path(__file__).resolve().parent / "notes" / "test_file.txt"
    if file_path.exists():
        file_path.unlink()


# 4. 测清空历史
def test_clear_history():
    # 先随便写点数据进 history.json
    history_path = Path(__file__).resolve().parent / "history.json"
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump([{"role": "user", "content": "假数据"}], f)

    result = clear_history()
    assert "已清空" in result

    # 检查是不是真的空了
    with open(history_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data == []