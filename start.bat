@echo off
setlocal enabledelayedexpansion

echo ========================================
echo  CertMonitor - Servidor Central
echo ========================================
echo.

:: --- Pre-requisitos ---

docker --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ERRO: Docker nao encontrado.
    echo Instale o Docker Desktop: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

docker compose version >nul 2>&1
if %errorLevel% neq 0 (
    echo ERRO: 'docker compose' nao encontrado.
    echo Atualize o Docker Desktop para uma versao recente.
    pause
    exit /b 1
)

:: --- Arquivo .env ---

if not exist .env (
    copy .env.example .env >nul
    echo Arquivo .env criado. Preencha os campos antes de continuar:
    echo.
    echo   API_TOKEN         - token compartilhado com os agentes
    echo   ADMIN_PASSWORD    - senha do dashboard web
    echo   SECRET_KEY        - chave para cookies de sessao
    echo   POSTGRES_PASSWORD - senha do banco de dados
    echo.
    echo Abra o arquivo .env, preencha e salve.
    echo.
    notepad .env
    echo.
    pause
)

:: Valida campos obrigatorios
for /f "tokens=1,2 delims==" %%A in (.env) do (
    if "%%A"=="API_TOKEN"         set API_TOKEN=%%B
    if "%%A"=="ADMIN_PASSWORD"    set ADMIN_PASSWORD=%%B
    if "%%A"=="SECRET_KEY"        set SECRET_KEY=%%B
    if "%%A"=="POSTGRES_PASSWORD" set POSTGRES_PASSWORD=%%B
)

if "%API_TOKEN%"=="" (
    echo ERRO: API_TOKEN nao configurado no .env
    pause & exit /b 1
)
if "%ADMIN_PASSWORD%"=="" (
    echo ERRO: ADMIN_PASSWORD nao configurado no .env
    pause & exit /b 1
)
if "%SECRET_KEY%"=="" (
    echo ERRO: SECRET_KEY nao configurado no .env
    pause & exit /b 1
)
if "%POSTGRES_PASSWORD%"=="" (
    echo ERRO: POSTGRES_PASSWORD nao configurado no .env
    pause & exit /b 1
)

:: --- Sobe o stack ---

echo Subindo CertMonitor + PostgreSQL...
docker compose up -d --build
echo.

echo Aguardando banco de dados...
timeout /t 8 /nobreak >nul

curl -s -o nul -w "%%{http_code}" http://localhost:8000/health 2>nul | findstr "200" >nul
if %errorLevel% equ 0 (
    echo Servidor OK.
) else (
    echo Servidor ainda iniciando. Verifique com: docker compose logs -f certmonitor
)

echo.
echo ========================================
echo  Servidor pronto!
echo ========================================
echo.
echo   Dashboard:  http://localhost:8000
echo   Usuario:    admin
echo.

pause
