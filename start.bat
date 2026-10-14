@echo off
chcp 65001 >nul
echo ========================================================
echo  Khởi động C_Data - Nền tảng tổng hợp việc làm Việt Nam
echo ========================================================
echo.

REM Thêm Node.js portable vào PATH
set "PATH=%~dp0node-bin\node-v20.18.0-win-x64;%PATH%"

echo [1/2] Đang khởi động Backend FastAPI (Port 8000)...
start "C_Data Backend API" cmd /k "cd /d %~dp0backend && .\venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

timeout /t 3 /nobreak >nul

echo [2/2] Đang khởi động Frontend Next.js (Port 3000)...
start "C_Data Frontend Web" cmd /k "cd /d %~dp0frontend && npm run dev -- -p 3000"

echo.
echo ========================================================
echo  Hệ thống đang chạy tại:
echo   - Website: http://localhost:3000
echo   - Backend API: http://127.0.0.1:8000
echo   - Tài liệu API: http://127.0.0.1:8000/docs
echo ========================================================
echo.
pause
