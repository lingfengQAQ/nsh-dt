@echo off
setlocal

REM Ensure we're in the script directory
cd /d "%~dp0"

REM Activate uv-managed virtualenv if present
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    echo [info] 未找到 .venv，直接使用系统 Python。
)

REM Install PyInstaller if missing
pyinstaller --version >nul 2>&1
if errorlevel 1 (
    echo [info] 正在安装 PyInstaller...
    python -m pip install --upgrade pip
    python -m pip install pyinstaller
)

REM 打包应用
pyinstaller ^
  --noconfirm ^
  --onedir ^
  --windowed ^
  --name NishuiHanAssistant ^
  --add-data "poetry.db;." ^
  --hidden-import=PIL._tkinter_finder ^
  --hidden-import=pytesseract ^
  --collect-all customtkinter ^
  --exclude-module matplotlib ^
  --exclude-module numpy ^
  --exclude-module pandas ^
  main.py

REM 提示结果位置
if exist dist\NishuiHanAssistant\NishuiHanAssistant.exe (
    echo.
    echo [done] 打包完成，文件位于 dist\NishuiHanAssistant\
    echo [info] 请将整个 NishuiHanAssistant 文件夹发布
    echo [info] 注意：poetry.db 数据库文件已包含在打包结果中
) else (
    echo.
    echo [error] 打包失败，请检查上方日志。
)

endlocal
