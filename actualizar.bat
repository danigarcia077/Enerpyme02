@echo off
set PYTHONUTF8=1
cd /d C:\Users\HP\Documents\EnerPyme
echo ===== %date% %time% ===== >> actualizacion.log
.venv\Scripts\python.exe actualizar_todo.py >> actualizacion.log 2>&1