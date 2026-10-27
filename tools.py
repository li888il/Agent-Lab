import json
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent#获得绝对路径

#对tool进行分离，移动至当前文件夹
# 👇 get_grades 就在这，紧挨着上面 👇
MOCK_GRADES = {
    "张三": {"数学": 90, "英语": 85},
    "李四": {"数学": 78, "英语": 92}
}


# 1. 以前用 os.path.join("notes", filename) 拼字符串容易错，现在直接用斜杠 / 拼接，清爽直观。
# 2. os 还要管 Windows 的反斜杠 \，现在 pathlib 自动适配全平台，写一个 / 走天下。
# 3. 以前判断文件得写 os.path.exists()，现在是面向对象，直接调属性 history_path.exists()。
# os 是散装函数，pathlib 是面向对象，代码短且防炸裂

def write_note(filename, content):
    # 用 pathlib 直接拼接路径，mkdir 建目录，open 直接传对象
    notes_dir = BASE_DIR / "notes"
    notes_dir.mkdir(exist_ok=True)
    file_path = notes_dir / filename
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"写入成功: {file_path}"


def get_grades(name, subject):
    try:
        score = MOCK_GRADES[name][subject]
        return f"{name}的{subject}成绩是：{score}分"
    except KeyError:
        return f"查不到{name}的{subject}成绩。"
# 👆 到这里结束 👆
def clear_history():
    history_path = BASE_DIR / "history.json"
    with open(history_path, "w", encoding="utf-8") as f:
        json.dump([], f)
    return "历史记录已清空"
# 👇 然后是注册表 👇
TOOLS = {
    "write_note": write_note,
    "get_grades": get_grades,
    "clear_history": clear_history  # 新增的
}
