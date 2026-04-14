@echo off
chcp 65001 >nul
title 威力彩 預測系統

cd /d C:\Users\chop1\OneDrive\Lottery_project
call .venv\Scripts\activate

echo ========================================
echo 威力彩 預測系統 - 一鍵執行
echo ========================================
echo.

python -m main_power

if errorlevel 1 (
    echo.
    echo [失敗] 威力彩 執行失敗
    pause
    exit /b 1
)

echo.
echo ========================================
echo [完成] 威力彩 執行完成
echo [輸出位置] data\power\output
echo ========================================
pause