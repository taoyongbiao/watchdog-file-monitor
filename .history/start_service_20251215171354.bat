@echo off
echo 正在启动文件监控服务...
echo 服务将在后台运行，按 Ctrl+C 可以停止服务
echo Web接口地址: http://localhost:8080
echo.
python file_monitor.py
pause