@echo off
chcp 65001 > nul
echo ========================================================
echo   Thai TTS Benchmark & Testing Studio
echo   สตูดิโอทดสอบโมเดลสังเคราะห์เสียงภาษาไทยคุณภาพสูง
echo ========================================================
echo.
cd /d "%~dp0"

echo [1/2] กำลังตรวจสอบสภาพแวดล้อมระบบ...
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] ไม่พบ .venv\Scripts\python.exe
    pause
    exit /b 1
)

echo [2/2] กำลังเริ่มเปิดเซิร์ฟเวอร์ที่ http://127.0.0.1:8765 ...
start "" http://127.0.0.1:8765
.\.venv\Scripts\python.exe server.py
pause
