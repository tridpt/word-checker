@echo off
REM Dong goi Word Checker thanh 1 file .exe chay doc lap (web app).
REM Yeu cau: pip install pyinstaller
REM Ket qua nam o thu muc dist\WordChecker.exe

pyinstaller --noconfirm --onefile --name WordChecker ^
  --icon "assets/icon.ico" ^
  --add-data "web;web" ^
  --add-data "assets;assets" ^
  --add-data "dictionaries;dictionaries" ^
  --exclude-module matplotlib --exclude-module numpy --exclude-module scipy ^
  --exclude-module pandas --exclude-module pygame --exclude-module PIL ^
  --exclude-module tkinter --exclude-module IPython --exclude-module jedi ^
  --exclude-module parso --exclude-module zmq --exclude-module notebook ^
  --exclude-module jupyter --exclude-module sympy --exclude-module sklearn ^
  --exclude-module PyQt5 --exclude-module PyQt6 --exclude-module PySide2 ^
  --exclude-module PySide6 --exclude-module wx --exclude-module cv2 ^
  --exclude-module torch --exclude-module tensorflow ^
  launch.py

echo.
echo Da xong. File chay nam tai: dist\WordChecker.exe
