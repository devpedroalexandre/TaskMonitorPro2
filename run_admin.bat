@echo off
:: Arquivo: run_admin.bat

set SCRIPT=run.py
set PYTHON=%~dp0venv\Scripts\python.exe

:: Troca para o diretório deste .bat
cd /d "%~dp0"

net session >nul 2>&1
if %errorlevel% == 0 (
   goto admin
) else (
   echo Solicitando permissao de Administrador...
   powershell -Command "Start-Process '%PYTHON%' -ArgumentList '%SCRIPT%' -WorkingDirectory '%CD%' -Verb RunAs"
   exit /b
)

:admin
echo Rodando como Administrador...
"%PYTHON%" "%SCRIPT%"
pause
