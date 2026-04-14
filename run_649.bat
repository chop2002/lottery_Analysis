@echo off
chcp 65001 >nul
title 大樂透 預測系統

cd /d C:\Users\chop1\OneDrive\Lottery_project
call .venv\Scripts\activate

echo ========================================
echo 大樂透 預測系統 - 一鍵執行
echo ========================================
echo.

python -m main_649

if errorlevel 1 (
    echo.
    echo [失敗] 大樂透 執行失敗
    pause
    exit /b 1
)

echo.
echo ========================================
echo [完成] 大樂透 執行完成
echo [輸出位置] data\649\output
echo ========================================
pause