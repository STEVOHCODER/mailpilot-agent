@echo off
cd /d "%~dp0"
if not exist logs mkdir logs
echo [%date% %time%] MailPilot supervisor started >> logs\supervisor.log
:loop
python main.py watch >> logs\watch.out 2>&1
echo [%date% %time%] watch exited (%errorlevel%), restarting in 10s >> logs\supervisor.log
timeout /t 10 /nobreak >nul
goto loop
