@echo off
REM Script de instalação do CertMonitor Agent como serviço no Windows
REM Requer NSSM (Non-Sucking Service Manager)

echo ========================================
echo CertMonitor Agent - Instalador Windows
echo ========================================
echo.

REM Verifica se está rodando como administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERRO: Execute este script como Administrador!
    pause
    exit /b 1
)

REM Define variáveis
set SERVICE_NAME=CertMonitorAgent
set PYTHON_PATH=python
set SCRIPT_PATH=%~dp0agent.py
set NSSM_URL=https://nssm.cc/release/nssm-2.24.zip

echo Verificando Python...
%PYTHON_PATH% --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ERRO: Python não encontrado! Instale Python 3.8+ primeiro.
    pause
    exit /b 1
)

echo Python encontrado!
echo.

echo Instalando dependências...
%PYTHON_PATH% -m pip install -r requirements.txt
echo.

echo ========================================
echo Instalação Manual do Serviço
echo ========================================
echo.
echo Para instalar como serviço Windows, use uma das opções:
echo.
echo OPÇÃO 1 - Task Scheduler (Recomendado):
echo 1. Abra o Task Scheduler
echo 2. Crie uma nova tarefa
echo 3. Configure para executar: %PYTHON_PATH% %SCRIPT_PATH%
echo 4. Configure para iniciar no boot
echo 5. Execute com privilégios de sistema
echo.
echo OPÇÃO 2 - NSSM (Avançado):
echo 1. Baixe NSSM de: %NSSM_URL%
echo 2. Execute: nssm install %SERVICE_NAME% %PYTHON_PATH% %SCRIPT_PATH%
echo 3. Execute: nssm start %SERVICE_NAME%
echo.
echo OPÇÃO 3 - Executar manualmente:
echo Execute: %PYTHON_PATH% %SCRIPT_PATH%
echo.

pause
