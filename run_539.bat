@echo off
chcp 65001 >nul
title 539 預測系統

cd /d C:\Users\chop1\OneDrive\Lottery_project
call .venv\Scripts\activate

echo ========================================
echo 539 預測系統 - 一鍵執行
echo ========================================
echo.

python -m main

if errorlevel 1 (
    echo.
    echo [失敗] 539 執行失敗
    pause
    exit /b 1
)

echo.
echo ========================================
echo [完成] 539 執行完成
echo [輸出位置] data\539\output
echo ========================================
pause