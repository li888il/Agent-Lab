import requests

# 这是你后端 API 的地址
url = "http://127.0.0.1:8000/chat"

# 这是前端要发给后端的数据（JSON格式）
payload = {"message": "帮我查一下张三的数学成绩"}

print("正在向后端发送请求...\n")

# 发送 POST 请求，并开启 stream=True 接收流式数据
response = requests.post(url, json=payload, stream=True)

# 逐行读取后端返回的流式内容并打印
for chunk in response.iter_content(chunk_size=None):
    if chunk:
        # 解码并打印，end="" 保证不换行
        print(chunk.decode('utf-8'), end="", flush=True)

print("\n\n=== 接收完毕 ===")