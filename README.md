#  Python AI Agent Lab

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![OpenAI](https://img.shields.io/badge/API-DeepSeek-green)
![Tests](https://img.shields.io/badge/Tests-5%20passed-brightgreen)
![License](https://img.shields.io/badge/License-MIT-orange)

一个基于 DeepSeek API 的纯软件 AI Agent 骨架。包含大模型交互、本地工具调用、数据库持久化与 Web 端流式交互。

## 核心特性

- **智能路由**：自动解析大模型返回的 JSON，基于 `TOOLS` 注册表实现动态参数解包与工具分发。
- **持久化记忆**：支持多轮对话上下文截断（滑动窗口），防止 Token 爆炸。
- **真实数据库接入**：基于 SQLite 存储工具数据，包含防死锁的 `try-finally` 保护与防路径穿越拦截。
- **流式输出**：支持 `stream=True`，并在 Web 端实现逐字打字机效果。
- **全栈异常恢复**：精准捕获网络断开、鉴权失败、限流及参数缺失，自动回滚无效提问。
- **自动化测试**：基于 Pytest 与 Mock 技术覆盖核心路由逻辑，包含 Streamlit `AppTest` 网页端交互测试。

## 项目结构

```text
Agent-Lab/
├── agent.py           # 核心 Agent 类、路由与 LLM 交互
├── tools.py           # 本地工具函数与注册表
├── init_db.py         # SQLite 数据库初始化脚本
├── app.py             # Streamlit Web 交互界面
├── test_agent.py      # 核心逻辑单元测试（含 Mock）
├── test_app.py        # Streamlit 网页端自动化测试
├── requirements.txt   # 依赖清单
└── .env.example       # 环境变量模板
