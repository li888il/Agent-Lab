import sqlite3

# 1. 连数据库
conn = sqlite3.connect("grades.db")
cursor = conn.cursor()

# 2. 建表
cursor.execute("CREATE TABLE IF NOT EXISTS scores (name TEXT, subject TEXT, score INTEGER)")

# 3. 插数据
cursor.execute("INSERT INTO scores VALUES (?,?,?)",('张三','数学',67))
cursor.execute("INSERT INTO scores VALUES (?,?,?)",('克神','英语',150))

# 插入检查代码：去 scores 表里把所有数据抽出来
cursor.execute("SELECT * FROM scores")
all_data = cursor.fetchall() # fetchall 意思是拿全部结果
print("当前数据库里的数据是：", all_data)

# 4. 保存
conn.commit()
conn.close()
print("数据库建好了！")