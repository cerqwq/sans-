# 项目指南

## 项目概述

统一 Flask 服务器托管 5 个项目，端口 8080。

## 启动方式

```bash
python server.py
# 或双击 start.bat
```

## 项目列表

- `/` — 作品集（my word/）
- `/ddz/` — 斗地主（ddz/）
- `/hand-particles/` — 手势粒子（hand-particles/）
- `/xiuxian/` — 鬼谷修仙录（xiuxian/）
- `auto-tool/` — 自动化工具（独立运行，不通过服务器）

## 技术栈

- 后端: Python 3, Flask, Flask-SocketIO (eventlet), SQLite
- 前端: Vanilla JS, Canvas 2D, anime.js, MediaPipe
- 数据库: SQLite（xiuxian_data.db, database.db）

## 代码规范

- Python: 遵循 PEP 8，函数用 snake_case，类用 PascalCase
- JS: camelCase，使用 ES6+ 语法
- CSS: CSS 自定义属性（变量），BEM 命名风格
- 中文注释和文档

## 注意事项

- 不要删除根目录下的 .db 文件（数据库）
- ddz/ 和 xiuxian/ 都有 routes.py，导入时注意模块名冲突
- 修仙游戏通过 xiuxian.routes 导入（不是直接 routes）
- 修改游戏引擎后需要重启服务器
- Canvas 绘制不要加载外部图片，用代码绘制
