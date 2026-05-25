import sqlite3
import hashlib

# 连接数据库
conn = sqlite3.connect('database.db')
c = conn.cursor()

# 添加测试账号（账号：admin，密码：123456）
username = 'admin'
password = hashlib.sha256('123456'.encode()).hexdigest()

try:
    c.execute('INSERT INTO users (username, password) VALUES (?, ?)', 
              (username, password))
    conn.commit()
    print('✅ 测试账号添加成功！')
    print('   账号：admin')
    print('   密码：123456')
except:
    print('⚠️ 账号已存在，无需重复添加')

conn.close()
