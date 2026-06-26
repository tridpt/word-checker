@echo off
REM Dong goi Word Checker thanh 1 file .exe chay doc lap (web app).
REM Yeu cau: pip install pyinstaller
REM Ket qua nam o thu muc dist\WordChecker.exe

pyinstaller --noconfirm --onefile --name WordChecker ^
  --icon "assets/icon.ico" ^
  --add-data "web;web" ^
  --add-data "assets;assets" ^
  --add-data "dictionaries;dictionaries" ^
  launch.py

echo.
echo Da xong. File chay nam tai: dist\WordChecker.exe
