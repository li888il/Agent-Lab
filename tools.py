import json
from pathlib import Path

from openai.types.graders import score_model_grader_param

BASE_DIR = Path(__file__).resolve().parent#获得绝对路径
import sqlite3

#对tool进行分离，移动至当前文件夹
# 👇 get_grades 就在这，紧挨着上面 👇

#引入数据库，去除假字典MOCK_GRADES

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
    conn =None    #【防崩护体】先占个坑，防止连库第一行就炸了，导致 finally 报错
                # 最后 finally 里找不到conn就会直接报 NameError 原地崩溃
    try:
        conn = sqlite3.connect(BASE_DIR /"grades.db")
        cursor = conn.cursor()

        cursor.execute("SELECT score FROM scores WHERE name=? AND subject=?", (name, subject))
        # 提取结果（返回的是个元组，比如 (67,)）
        result = cursor.fetchone()

        if result:
            return f"{name}的{subject}成绩是：{result[0]}分"
        else :
            return f"查不到{name}的{subject}成绩"
    except Exception as e:
        # 【大网眼兜底】别用 KeyError，数据库报错五花八门，用 Exception 全兜住，防程序崩溃

        return"数据库报错,请稍后再试"
    finally:
        if conn:
            #与条件判断逻辑不同，不存在就报错
            conn.close()
        #【防死锁铁律】不管上面是报错了还是成功，只要 conn 存在（连上了），走之前必须关门！
        #防止第一行就报错了，电脑突然没权限了，或者路径乱码了，导致根本没连上数据库


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
