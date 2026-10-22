@echo off
cd /d "%~dp0"
py -m pip install -q -r requirements.txt
py main.py
if errorlevel 1 pause
