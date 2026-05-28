# 斗地主 (ddz)

在线斗地主游戏，Flask + WebSocket 实时对战。

## 项目结构
- `app.py` — 独立运行入口（在本目录运行：`python app.py`）
- `game_engine.py` — 扑克牌发牌、出牌逻辑
- `routes.py` — Flask 路由（使用 sys.path 导入，非包模式）
- `doudizhu_db.py` — SQLite 数据库模块，DB 文件在本目录
- `ws_handlers.py` — WebSocket 对战事件
- `static/` — 前端资源
- `templates/` — HTML 模板

## 运行方式
- 统一服务器：`cd "E:\Claude code work" && python server.py`（端口 8080，路径 /ddz/）
- 独立运行：`cd "E:\Claude code work\ddz" && python app.py`（端口 5000）

## 技术栈
- Flask + Flask-SocketIO (eventlet)
- SQLite（database.db）
- bcrypt 密码加密

## 注意事项
- ddz 通过 sys.path 导入（非 Python 包），与 xiuxian 的包导入方式不同
- DB 路径使用绝对路径，确保无论从哪里运行都指向本目录的 database.db
