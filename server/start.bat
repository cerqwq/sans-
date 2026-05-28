@echo off
echo.
echo ========================================
echo   项目统一服务器
echo ========================================
echo.
echo   作品集:     http://127.0.0.1:8080/
echo   斗地主:     http://127.0.0.1:8080/ddz/
echo   手势粒子:   http://127.0.0.1:8080/hand-particles/
echo   修仙游戏:   http://127.0.0.1:8080/xiuxian/
echo.
echo ========================================
echo.

cd /d "%~dp0"
python server.py
pause
