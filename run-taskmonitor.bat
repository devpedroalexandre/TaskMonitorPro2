@echo off
REM Muda para o diretório do projeto
cd /d "C:\node projects\VIRTUAL\TaskMonitorPro2"

REM Verifica se o arquivo run.py existe
if not exist "run.py" (
    echo ERRO: Arquivo run.py nao encontrado!
    echo Certifique-se de que o caminho no .bat esta correto.
    echo Caminho atual: %cd%
    pause
    exit /b 1
)

REM Ativa o ambiente virtual
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

REM Verifica se o Python está disponível
python --version
if errorlevel 1 (
    echo ERRO: Python nao encontrado!
    pause
    exit /b 1
)

REM Executa o projeto
echo.
echo Iniciando TaskMonitor Pro...
echo.
python run.py

REM Mantém a janela aberta em caso de erro
pause
