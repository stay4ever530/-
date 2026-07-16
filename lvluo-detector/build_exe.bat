@echo off
chcp 65001 >nul
echo =============================
echo   打包绿萝叶片检测系统
echo =============================
echo.
echo 正在安装 PyInstaller...
pip install pyinstaller -q
echo.
echo 正在打包为单文件 EXE...
pyinstaller --onefile --windowed --name "绿萝叶片检测系统" ^
    --add-data "best.pt;." ^
    --add-data "samples;samples" ^
    --hidden-import PyQt5 ^
    --hidden-import ultralytics ^
    --hidden-import cv2 ^
    --hidden-import numpy ^
    --hidden-import PIL ^
    main.py
echo.
echo =============================
echo   打包完成!
echo   EXE 在 dist\ 目录下
echo =============================
pause
