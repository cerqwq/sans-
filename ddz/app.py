"""
斗地主 - Flask应用（独立运行模式）
使用 routes.py 和 ws_handlers.py 共享逻辑
"""

import os
from flask import Flask, redirect
from flask_socketio import SocketIO

from doudizhu_db import init_db
from routes import register_routes
from ws_handlers import register_ws_handlers

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'ddz-dev-secret-key-change-in-production')
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 注册路由（独立运行也使用 /ddz 前缀，与模板路径一致）
register_routes(
    app,
    templates_dir=os.path.join(BASE_DIR, 'templates'),
    static_dir=os.path.join(BASE_DIR, 'static'),
    prefix='/ddz'
)

# 注册 WebSocket 处理器
register_ws_handlers(socketio)

# 根路径重定向到 /ddz/
@app.route('/')
def index_redirect():
    return redirect('/ddz/')

# 启动
init_db()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"\n{'='*40}")
    print(f"  斗地主服务器启动")
    print(f"  http://127.0.0.1:{port}")
    print(f"{'='*40}\n")
    socketio.run(app, debug=False, host='0.0.0.0', port=port)
