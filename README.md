# 🤖 Python AI Agent Lab

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![OpenAI](https://img.shields.io/badge/API-DeepSeek-green)
![Tests](https://img.shields.io/badge/Tests-5%20passed-brightgreen)
![License](https://img.shields.io/badge/License-MIT-orange)

一个纯软件、轻量级的本地 AI Agent 骨架。基于大语言模型（LLM），具备本地工具调用（Tool Calling）、上下文记忆管理与异常容错恢复能力。

## ✨ 核心特性

- **🧠 智能路由机制**：自动解析 LLM 返回的 JSON 结构，精准分发本地工具指令。
- **🛠️ 可扩展的工具注册表**：通过简单的字典映射即可无限扩展本地能力（当前内置：写笔记、查成绩、清空记忆）。
- **💾 持久化记忆**：支持 `history.json` 持久化多轮对话，内置滑动窗口截断机制（防 Token 爆炸）。
- **🛡️ 工业级异常恢复**：
  - 网络异常/断流：自动回滚上下文（Pop），防止记忆断层。
  - 鉴权/限流分类捕获：精准区分 Key 错误与余额不足，拒绝笼统报错。
  - 工具参数缺失：不丢弃上下文，转为系统反馈重新引导大模型。
- **🔒 沙箱级安全隔离**：基于工具注册表（`TOOLS`）实现白名单机制，从架构层面杜绝了未经授权的数据库写入或篡改风险。
- **🧪 单元测试覆盖**：纯本地隔离测试，通过 Mock 客户端切断真实网络请求。
- **🗄️ 真实数据库接入**：弃用内存假字典，全面接入 SQLite 数据库持久化存储。
- **🌊 流式输出体验**：支持 `stream=True`，终端实现类似 ChatGPT 的逐字打印效果。
## 📂 项目结构

```text
Agent-Lab/
├── agent.py           # 核心 Agent 类、主循环、LLM 交互逻辑
├── tools.py           # 本地工具函数（查成绩、写笔记等）与注册表
├── test_agent.py      # Pytest 单元测试用例（包含 Mock 逻辑）
├── history.json       # 自动生成的对话历史（已忽略）
├── requirements.txt   # 依赖清单
├── .env.example       # 环境变量模板
└── .gitignore         # Git 忽略规则