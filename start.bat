@echo off
chcp 65001 >nul
echo =============================================
echo   AI 中文文本情绪分析系统 启动脚本
echo =============================================
echo.

REM 检查依赖
echo [1/2] 检查Python依赖...
pip install flask flask-cors snownlp jieba wordcloud pandas numpy -q

REM 启动后端
echo [2/2] 启动后端服务...
start "Sentiment Backend" cmd /c "cd /d %~dp0backend && python app.py"

timeout /t 3 /nobreak >nul

REM 打开前端
echo 正在打开前端页面...
start "" "%~dp0frontend\index.html"

echo.
echo =============================================
echo   后端: http://localhost:5000
echo   前端已自动打开
echo   按任意键关闭后端...
echo =============================================
pause >nul
taskkill /FI "WINDOWTITLE eq Sentiment Backend" /F 2>nul
