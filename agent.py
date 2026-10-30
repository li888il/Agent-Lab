import os
import time
import openai
from dotenv import load_dotenv
import json
from openai import OpenAI
from tools import TOOLS
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent


load_dotenv()  # 自动去读同目录下的 .env 文件，把里面的变量塞进环境


# ================= 1. 本地工具函数 =================

#已搬走至tools.py


# ================= 2. 历史记忆函数 =================
def load_history():
    history_path = BASE_DIR / "history.json"
    if history_path.exists():
        try:
            with open(history_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_history(history):
    history_path = BASE_DIR / "history.json "
    with open(history_path, "w", encoding="utf-8") as f:
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

        #测试截断，代替了原先展现message_to_send的详细内容
        print(f"[系统]已发送{len(messages_to_send)}")
        # B. 调模型
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages_to_send,
                stream=True
            )
            # 换成流式遍历
            ai_reply = ""
            print("Agent: ", end="", flush=True)
            for chunk in response:
                content = chunk.choices[0].delta.content
                if content:
                    ai_reply += content
                    print(content, end="", flush=True)
            print()  # 打印完换行

        # 网络断了的错误恢复
        #原先都为except Exception as e,未作划分
        #以下进行精确错位置定位升级
        except openai.AuthenticationError:
            print("[异常]: 鉴权失败，API Key 填错了！")
            self.history.pop()
            return "抱歉，系统配置有误，请联系管理员（Key错误）。"

        except openai.RateLimitError:
            print("[异常]: 额度不足或请求频率过高。")
            self.history.pop()
            return "抱歉，AI 大脑今天太累了，请稍后再试（欠费/限流）。"

        except openai.APIConnectionError:
            print("[异常]: 网络断了。")
            self.history.pop()
            return "抱歉，网络连接失败，请检查您的网络。"

        except Exception as e:
            print(f"[未知错误]: {e}")
            self.history.pop()
            return "系统开小差了，请稍后再试。"
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

            #模型瞎编了个不存在的工具名（幻觉），也是json格式，需要else兜住
            else:final_answer = ai_reply

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
            print()
        except Exception as e:
            print(f"[报错]: {e}\n")
