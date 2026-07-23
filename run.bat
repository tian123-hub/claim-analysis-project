@echo off
chcp 65001 >nul
title 保险理赔数据分析项目

echo ============================================
echo   保险理赔数据分析项目 - 一键运行
echo ============================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Python！请先安装Python
    echo 下载地址：https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)
echo [OK] Python 已安装

REM 安装依赖
echo.
echo [步骤] 正在安装依赖库...
pip install -r requirements.txt -q
if %errorlevel% neq 0 (
    echo [提示] pip安装失败，尝试使用镜像源...
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt -q
)
echo [OK] 依赖安装完成

REM 第一步：生成数据
echo.
echo [步骤 1/2] 生成模拟理赔数据（10万条）
python generate_data.py
if %errorlevel% neq 0 (
    echo [错误] 数据生成失败！
    pause
    exit /b 1
)
echo.

REM 第二步：运行分析
echo.
echo [步骤 2/2] 运行数据分析引擎
python analysis.py
if %errorlevel% neq 0 (
    echo [错误] 分析运行失败！
    pause
    exit /b 1
)

REM 完成
echo.
echo ============================================
echo   项目运行完成！
echo.
echo   生成文件：
echo     1. 图表文件: output\top10_policies_chart.png
echo     2. 分析报告: output\analysis_report.txt
echo.
echo ============================================
echo.
pause
