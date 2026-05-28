# 修仙游戏 (xiuxian)

鬼谷八荒风格文字修仙游戏，Flask + Canvas 前端。

## 项目结构
- `app.py` — 独立运行入口（从父目录运行：`python xiuxian/app.py`）
- `game_engine.py` — 纯游戏逻辑，无服务器依赖
- `routes.py` — Flask 路由（使用相对导入，必须作为包导入）
- `xiuxian_db.py` — SQLite 数据库模块，DB 文件在本目录
- `ws_handlers.py` — WebSocket 事件
- `static/game.js` — 前端 JS（Canvas 战斗渲染、anime.js 动画）
- `static/style.css` — 水墨仙侠风格 CSS
- `templates/index.html` — 单页应用 HTML

## 运行方式
- 统一服务器：`cd "E:\Claude code work" && python server.py`（端口 8080，路径 /xiuxian/）
- 独立运行：`cd "E:\Claude code work" && python xiuxian/app.py`（端口 5001）

## 技术栈
- Flask + Flask-SocketIO (eventlet)
- SQLite（xiuxian_data.db）
- Canvas 2D + anime.js 战斗动画
- Windows 系统字体（STKaiti, STXingkai, SimSun）

## 注意事项
- routes.py 使用相对导入（`from .xiuxian_db import ...`），必须作为 Python 包导入
- DB 路径使用 `os.path.dirname(os.path.abspath(__file__))` 确保无论从哪里运行都指向本目录
- 前端使用 Windows 系统中文字体，不依赖 Google Fonts
