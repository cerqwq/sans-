"""
修仙游戏 WebSocket 事件处理
所有事件使用 xiuxian_ 前缀避免与 ddz 冲突
"""
from flask_socketio import emit

def register_ws_handlers(socketio):

    @socketio.on('xiuxian_ping')
    def handle_xiuxian_ping(data):
        emit('xiuxian_pong', {'time': data.get('time', 0)})
