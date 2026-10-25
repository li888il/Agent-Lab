import os
import json
# 把需要用到的函数一次性全导入
from agent import TOOLS, get_grades, write_note, clear_history


# 1. 测注册表
def test_tools_registry_has_three_tools():
    assert "write_note" in TOOLS
    assert "get_grades" in TOOLS
    assert "clear_history" in TOOLS


# 2. 测查成绩（查得到）
def test_get_grades_hit():
    assert "90" in get_grades("张三", "数学")


# 3. 测查成绩（查不到）
def test_get_grades_miss():
    assert "查不到" in get_grades("王五", "数学")


# 4. 测写笔记
def test_write_note():
    filename = "test_file.txt"
    content = "这是一条测试笔记"
    result = write_note(filename, content)
    assert "写入成功" in result
    # 顺手清理一下刚才写进去的测试文件，保持目录干净
    if os.path.exists(os.path.join("../../notes", filename)):
        os.remove(os.path.join("../../notes", filename))


# 5. 测清空历史
def test_clear_history():
    # 先随便写点假数据进 history.json
    with open("history.json", "w", encoding="utf-8") as f:
        json.dump([{"role": "user", "content": "假数据"}], f)

    result = clear_history()

    assert "已清空" in result
    with open("history.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data == [] 