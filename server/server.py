"""
统一服务器 - 托管所有项目
- / -> my word (作品集)
- /ddz -> 斗地主游戏
- /hand-particles -> 手势粒子
- /xiuxian -> 鬼谷修仙录
"""

import os
import sys
import logging
import time
import gzip
from functools import wraps

from flask import Flask, send_from_directory, redirect, jsonify, request, g
from flask_socketio import SocketIO

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# 添加项目目录到路径（server.py 在 server/ 子目录，项目在父目录）
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 先导入 ddz 模块（使用 sys.path）
sys.path.insert(0, os.path.join(BASE_DIR, 'ddz'))
from doudizhu_db import init_db
from routes import register_routes
from ws_handlers import register_ws_handlers

# 再导入修仙游戏模块（作为包导入，避免与 ddz 的 routes.py 冲突）
sys.path.insert(0, BASE_DIR)
from xiuxian.xiuxian_db import init_db as init_xiuxian_db
from xiuxian.routes import register_routes as register_xiuxian_routes
from xiuxian.ws_handlers import register_ws_handlers as register_xiuxian_ws

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['START_TIME'] = time.time()
app.config['JSON_SORT_KEYS'] = False

# CORS 配置
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# ============================================
# 请求计时和安全头
# ============================================

@app.before_request
def before_request():
    g.start_time = time.time()

@app.after_request
def after_request(response):
    # 安全头
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'

    # 静态资源缓存
    if request.path.startswith(('/assets/', '/static/', '/style.css', '/script.js')):
        response.headers['Cache-Control'] = 'public, max-age=3600'  # 1小时缓存
    elif request.path.endswith(('.js', '.css')):
        response.headers['Cache-Control'] = 'public, max-age=86400'  # 24小时缓存

    # 请求计时日志
    if hasattr(g, 'start_time'):
        elapsed = time.time() - g.start_time
        if elapsed > 1.0:  # 超过1秒的请求记录警告
            logger.warning(f"Slow request: {request.method} {request.path} took {elapsed:.2f}s")

    return response

# ============================================
# 全局错误处理
# ============================================

@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/api/'):
        return jsonify(success=False, message="API不存在"), 404
    return jsonify(success=False, message="页面不存在"), 404

@app.errorhandler(500)
def server_error(e):
    logger.error(f"服务器错误: {e}", exc_info=True)
    return jsonify(success=False, message="服务器内部错误"), 500

@app.errorhandler(429)
def rate_limit_exceeded(e):
    return jsonify(success=False, message="请求过于频繁，请稍后再试"), 429

# ============================================
# 健康检查
# ============================================

@app.route('/health')
def health():
    return jsonify(
        status='ok',
        projects=['portfolio', 'ddz', 'hand-particles', 'xiuxian'],
        timestamp=time.time(),
        uptime=time.time() - app.config.get('START_TIME', time.time()),
    )

# ============================================
# 作品集路由
# ============================================

@app.route('/')
def home():
    return send_from_directory(os.path.join(BASE_DIR, 'my word'), 'index.html')


@app.route('/assets/<path:filename>')
def home_assets(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'my word', 'assets'), filename)


@app.route('/style.css')
def home_css():
    return send_from_directory(os.path.join(BASE_DIR, 'my word'), 'style.css')


@app.route('/script.js')
def home_js():
    return send_from_directory(os.path.join(BASE_DIR, 'my word'), 'script.js')


# ============================================
# 手势粒子路由
# ============================================

@app.route('/hand-particles')
def hand_redirect():
    return redirect('/hand-particles/')


@app.route('/hand-particles/')
def hand_index():
    return send_from_directory(os.path.join(BASE_DIR, 'hand-particles'), 'index.html')


@app.route('/hand-particles/<path:filename>')
def hand_static(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'hand-particles'), filename)


# ============================================
# 斗地主路由（从模块导入）
# ============================================

register_routes(
    app,
    templates_dir=os.path.join(BASE_DIR, 'ddz', 'templates'),
    static_dir=os.path.join(BASE_DIR, 'ddz', 'static'),
    prefix='/ddz'
)

# ============================================
# 修仙游戏路由（从模块导入）
# ============================================

register_xiuxian_routes(
    app,
    templates_dir=os.path.join(BASE_DIR, 'xiuxian', 'templates'),
    static_dir=os.path.join(BASE_DIR, 'xiuxian', 'static'),
    prefix='/xiuxian'
)

# ============================================
# WebSocket 事件（从模块导入）
# ============================================

register_ws_handlers(socketio)
register_xiuxian_ws(socketio)

# ============================================
# 启动
# ============================================

init_db()
init_xiuxian_db()
logger.info("数据库初始化完成")

if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("  项目统一服务器")
    print("=" * 50)
    print("  作品集:     http://127.0.0.1:8080/")
    print("  斗地主:     http://127.0.0.1:8080/ddz/")
    print("  手势粒子:   http://127.0.0.1:8080/hand-particles/")
    print("  修仙游戏:   http://127.0.0.1:8080/xiuxian/")
    print("  健康检查:   http://127.0.0.1:8080/health")
    print("=" * 50)
    print(f"  安全头:     已启用")
    print(f"  请求计时:   已启用")
    print(f"  日志级别:   {logging.getLevelName(logger.level)}")
    print("=" * 50 + "\n")

    socketio.run(app, debug=True, use_reloader=False, host='0.0.0.0', port=8080)
