# 项目集合

统一服务器托管多个项目，基于 Flask + Flask-SocketIO。

## 快速启动

```bash
# 方式1: 双击 start.bat
# 方式2: 命令行运行
python server.py
```

访问 http://127.0.0.1:8080/

## 项目列表

| 路径 | 项目 | 说明 | 技术栈 |
|------|------|------|--------|
| `/` | 作品集 | 个人作品集网站 | HTML, CSS, JavaScript |
| `/ddz/` | 斗地主 | 在线斗地主（单人+联机） | Flask, SocketIO, SQLite |
| `/hand-particles/` | 手势粒子 | 手势识别粒子特效 | Canvas, MediaPipe |
| `/xiuxian/` | 鬼谷修仙录 | 文字修仙 RPG | Flask, Canvas 2D, anime.js |
| `auto-tool/` | 自动化工具 | 屏幕自动化（独立运行） | Python, pyautogui |

## 项目结构

```
├── server.py              # 统一服务器入口
├── start.bat              # 启动脚本
├── database.db            # 斗地主数据库
├── xiuxian_data.db        # 修仙游戏数据库
│
├── my word/               # 作品集网站
│   ├── index.html
│   ├── style.css
│   ├── script.js
│   └── assets/
│
├── ddz/                   # 斗地主游戏
│   ├── app.py             # 独立运行入口
│   ├── routes.py          # 路由模块
│   ├── ws_handlers.py     # WebSocket 模块
│   ├── game_engine.py     # 游戏引擎
│   ├── doudizhu_db.py     # 数据库模块
│   ├── templates/
│   └── static/
│
├── xiuxian/               # 鬼谷修仙录
│   ├── game_engine.py     # 游戏引擎（战斗/修炼/突破）
│   ├── routes.py          # API 路由
│   ├── xiuxian_db.py      # 数据库模块
│   ├── ws_handlers.py     # WebSocket 模块
│   ├── templates/
│   └── static/
│
├── hand-particles/        # 手势粒子特效
│   ├── index.html
│   ├── js/
│   └── vendor/            # MediaPipe 本地文件
│
└── auto-tool/             # 屏幕自动化工具
    ├── auto_tool.py
    ├── demo.py
    └── ocr_setup.md
```

## 访问地址

- 作品集: http://127.0.0.1:8080/
- 斗地主: http://127.0.0.1:8080/ddz/
- 手势粒子: http://127.0.0.1:8080/hand-particles/
- 修仙游戏: http://127.0.0.1:8080/xiuxian/
