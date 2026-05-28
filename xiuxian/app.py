"""
修仙游戏 - Flask应用（独立运行模式）
用法: cd "Claude code work" && python xiuxian/app.py
"""

import os
import sys
from flask import Flask, redirect
from flask_socketio import SocketIO

# 添加父目录到路径，使 xiuxian 包可以被导入
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
sys.path.insert(0, PARENT_DIR)

from xiuxian.xiuxian_db import init_db
from xiuxian.routes import register_routes
from xiuxian.ws_handlers import register_ws_handlers

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'xiuxian-dev-secret-key')
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

register_routes(
    app,
    templates_dir=os.path.join(BASE_DIR, 'templates'),
    static_dir=os.path.join(BASE_DIR, 'static'),
    prefix='/xiuxian'
)

register_ws_handlers(socketio)

@app.route('/')
def index_redirect():
    return redirect('/xiuxian/')

init_db()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print(f"\n{'='*40}")
    print(f"  修仙游戏服务器启动")
    print(f"  http://127.0.0.1:{port}")
    print(f"{'='*40}\n")
    socketio.run(app, debug=False, host='0.0.0.0', port=port)
