import sqlite3

# 连接数据库
conn = sqlite3.connect('database.db')
c = conn.cursor()

print("=" * 60)
print("📋 用户账号信息")
print("=" * 60)

# 查询用户表
c.execute('SELECT id, username, email, created_at FROM users')
users = c.fetchall()

if users:
    print(f"{'ID':<5} {'用户名':<15} {'邮箱':<25} {'注册时间'}")
    print("-" * 60)
    for user in users:
        email = user[2] if user[2] else '(未填写)'
        print(f"{user[0]:<5} {user[1]:<15} {email:<25} {user[3]}")
else:
    print("暂无用户数据")

print()
print("=" * 60)
print("🃏 斗地主游戏数据")
print("=" * 60)

# 查询斗地主数据表
c.execute('''
    SELECT id, username, coins, wins, losses, draws, total_games, created_at 
    FROM doudizhu_data
    ORDER BY coins DESC
''')
game_data = c.fetchall()

if game_data:
    print(f"{'ID':<5} {'用户名':<15} {'金币':<8} {'胜':<5} {'负':<5} {'平':<5} {'总场次':<8} {'注册时间'}")
    print("-" * 80)
    for data in game_data:
        print(f"{data[0]:<5} {data[1]:<15} {data[2]:<8} {data[3]:<5} {data[4]:<5} {data[5]:<5} {data[6]:<8} {data[7]}")
else:
    print("暂无斗地主数据")

conn.close()
