# 接续卡
## 当前主线
v2.1 收尾：测试对齐 + 拆前端直连 grades.db
## 上次做到哪
流式中文已跑通；正在把 decode_utf8_chunks 拆成独立文件并自己重写
11/26：闭卷重写成功（5分钟）；pytest 2 passed；对照实验已验证会变红
下一步：11/28 对齐 test_app.py
 app.py 里没有 status_code 检查（只有一处用到 res）。从来没检查过“这水管接出来的是不是错误信息”。