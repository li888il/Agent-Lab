import os
import json
from openai import OpenAI


# ================= 1. 本地工具函数 =================

def write_note(filename, content):
    """把 AI 提取出的内容写入 notes/ 目录，返回写入结果"""
    os.makedirs("../../notes", exist_ok=True)
    safe_name = os.path.basename(filename)
    path = os.path.join("../../notes", safe_name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"写入成功: {path}"

# 👇 get_grades 就在这，紧挨着上面 👇
MOCK_GRADES = {
    "张三": {"数学": 90, "英语": 85},
    "李四": {"数学": 78, "英语": 92}
}

def get_grades(name, subject):
    try:
        score = MOCK_GRADES[name][subject]
        return f"{name}的{subject}成绩是：{score}分"
    except KeyError:
        return f"查不到{name}的{subject}成绩。"
# 👆 到这里结束 👆
def clear_history():
    with open("history.json", "w", encoding="utf-8") as f:
        json.dump([],f)
    return "历史记录已清空"
# 👇 然后是注册表 👇
TOOLS = {
    "write_note": write_note,
    "get_grades": get_grades,
    "clear_history": clear_history  # 新增的
}

# ================= 2. 历史记忆函数 =================
def load_history():
    if os.path.exists("history.json"):
        try:
            with open("history.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_history(history):
    with open("history.json", "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

# ================= 3. Agent 核心类 =================
class Agent:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.environ.get('DEEPSEEK_API_KEY'),
            base_url="https://api.deepseek.com"
        )


        self.system_prompt = """
你是一个智能助手。你有两个工具可以使用。
如果用户要记笔记，输出 JSON: {"tool": "write_note", "filename": "xx.txt", "content": "xx"}
如果用户要查成绩，输出 JSON: {"tool": "get_grades", "name": "xx", "subject": "xx"}
如果用户要求清空/重置记忆，输出 JSON: {"tool": "clear_history"}
如果是普通聊天，直接中文回答。
注意：调工具必须严格输出 JSON，不要带 ```json 标记。
"""


        # 读历史
        self.history = load_history()

        # 关键修复：无论历史是否为空，都强制把 system 放到第一条
        # 防止旧 history.json 里残留旧 prompt，导致新 prompt 永远不生效
        if not self.history or self.history[0].get("role") != "system":
            self.history.insert(0, {"role": "system", "content": self.system_prompt})
        else:
            self.history[0] = {"role": "system", "content": self.system_prompt}

    def reply(self, user_text):
        # A. 用户消息入历史
        self.history.append({"role": "user", "content": user_text})

        # 👇 这是今天新加的截断逻辑（5行代码） 👇
        # 只保留最近的 5 轮对话（10条消息），防止历史无限膨胀
        if len(self.history) > 11:  # 1条system + 10条最新的对话
            system_msg = self.history[0]
            recent_msgs = self.history[-10:]  # 取最后10条，保持原顺序
            messages_to_send = [system_msg] + recent_msgs
        else:
            messages_to_send = self.history

        # 👆 截断逻辑结束 👆

        print("=== 我要发出去的包裹 ===")
        for msg in messages_to_send:
            print(f"[{msg['role']}] {msg['content']}")
        print("========================")

        # B. 调模型
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages_to_send,
                stream=False
            )
            ai_reply = response.choices[0].message.content
        except Exception as e:
            # 网络断了的错误恢复
            final_answer = "抱歉，网络连接失败，请再说一遍。"
            self.history.pop()
            print(f"[网络异常]: {e}")
            return final_answer
        # C. 路由：JSON 工具指令 or 普通聊天
        text = ai_reply.strip()                 # 去首尾空白，防解析失败
        try:
            data = json.loads(text)

            # 1. 先看大模型要用哪个工具
            tool_name = data.get("tool")

            # 2. 如果这个工具在我们的注册表里
            if tool_name in TOOLS:
                func = TOOLS[tool_name]
                try:

                    if tool_name == "write_note":
                        result = func(data["filename"], data["content"])
                    elif tool_name == "get_grades":
                        result = func(data["name"], data["subject"])
                    elif tool_name == "clear_history":
                        result = func()  # 不需要传任何参数

                        # 【核心坑位】：立刻清空内存里的 self.history，只保留 system！
                        # 否则走到最后一步 D 存盘时，又把这个对话存进去了
                        self.history = [{"role": "system", "content": self.system_prompt}]

                    final_answer = f"[系统提示] {result}"
                except KeyError as e:
                    # 【反馈型·不抹】请求已发、user 有效，不 pop；
                    # 只把失败原因留给 D 步写成 assistant，给模型下轮修正的依据
                    print(f"[工具参数缺失]: {e}")
                    final_answer = f"工具执行失败：大模型漏掉了必要的参数 {e}"

        except json.JSONDecodeError:
            final_answer = ai_reply
        # D. 回复入历史 + 落盘
        self.history.append({"role": "assistant", "content": final_answer})
        save_history(self.history)
        return final_answer


# ================= 4. 启动 =================
if __name__ == "__main__":
    agent = Agent()
    print("Agent 已启动（输入 exit 退出）。")

    while True:
        user_input = input("你: ")
        if user_input == "exit":
            break
        try:
            reply = agent.reply(user_input)
            print(f"Agent: {reply}\n")
        except Exception as e:
            print(f"[报错]: {e}\n")
