@echo off
setlocal enabledelayedexpansion
title LegalIQ Demo Launcher
cd /d "%~dp0"

echo ============================================================
echo   LegalIQ Demo Launcher  -  fully local (Ollama, no API key)
echo ============================================================

REM ---------- 1. Docker engine ----------
echo.
echo [1/6] Docker Desktop...
docker info >nul 2>&1
if errorlevel 1 (
    if exist "C:\Program Files\Docker\Docker\Docker Desktop.exe" (
        echo   starting Docker Desktop...
        start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    )
    set /a tries=0
    :waitdocker
    timeout /t 4 /nobreak >nul
    docker info >nul 2>&1
    if errorlevel 1 (
        set /a tries+=1
        if !tries! lss 30 goto waitdocker
        echo   ERROR: Docker engine did not start. Start it manually and re-run.
        pause
        exit /b 1
    )
)
echo   Docker engine OK.

REM ---------- 2. Database ----------
echo [2/6] PostgreSQL container...
docker compose up -d 2>&1 | findstr /i "Started running" >nul
timeout /t 5 /nobreak >nul
docker compose ps 2>&1 | findstr /i "legal_ai_db" >nul
if errorlevel 1 (
    echo   ERROR: legal_ai_db container is not healthy. Run: docker compose ps
    pause
    exit /b 1
)
echo   Database OK.

REM ---------- 3. Ollama server ----------
echo [3/6] Ollama server...
curl -s -m 3 http://localhost:11434/api/version >nul 2>&1
if errorlevel 1 (
    if exist "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" (
        echo   starting Ollama...
        start "" /min "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" serve
        timeout /t 6 /nobreak >nul
    )
)
curl -s -m 3 http://localhost:11434/api/version >nul 2>&1
if errorlevel 1 (
    echo   ERROR: Ollama is not reachable on :11434. Start Ollama and re-run.
    pause
    exit /b 1
)
echo   Ollama OK.

REM ---------- 4. Backend ----------
echo [4/6] FastAPI backend (:8000)...
netstat -ano | findstr ":8000" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    start "" /min cmd /c "cd /d "%~dp0backend" && .venv\Scripts\python.exe -m uvicorn app.main:app --port 8000 > "%~dp0backend_run.log" 2>&1"
    set /a tries=0
    :waitbackend
    timeout /t 3 /nobreak >nul
    curl -s -m 3 http://localhost:8000/api/health >nul 2>&1
    if errorlevel 1 (
        set /a tries+=1
        if !tries! lss 15 goto waitbackend
        echo   ERROR: backend did not come up. See backend_run.log
        pause
        exit /b 1
    )
) else (
    echo   already running.
)
echo   Backend OK.

REM ---------- 5. Frontend ----------
echo [5/6] Vite frontend (:5173)...
netstat -ano | findstr ":5173" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    start "" /min cmd /c "cd /d "%~dp0frontend" && npx vite --port 5173 > "%~dp0frontend_run.log" 2>&1"
    set /a tries=0
    :waitfront
    timeout /t 3 /nobreak >nul
    curl -s -m 3 -o nul http://localhost:5173/
    if errorlevel 1 (
        set /a tries+=1
        if !tries! lss 15 goto waitfront
        echo   ERROR: frontend did not come up. See frontend_run.log
        pause
        exit /b 1
    )
) else (
    echo   already running.
)
echo   Frontend OK.

REM ---------- 6. Prewarm models (loads them into VRAM for 2 hours) ----------
echo [6/6] Prewarming AI models - llama3.2:3b + nomic-embed-text (about a minute on first run)...
curl -s -m 240 http://localhost:11434/api/generate -d "{\"model\":\"llama3.2:3b\",\"prompt\":\"ok\",\"keep_alive\":\"2h\",\"stream\":false}" >nul 2>&1
curl -s -m 120 http://localhost:11434/api/embed -d "{\"model\":\"nomic-embed-text\",\"input\":[\"warmup\"],\"keep_alive\":\"2h\"}" >nul 2>&1
echo   Models warm (stay loaded for ~2 hours).

echo.
echo ============================================================
echo   ALL SYSTEMS GO
echo   App:      http://localhost:5173
echo   Login:    demo@legaliq.dev  /  demo12345
echo   API health: http://localhost:8000/api/health
echo   (logs: backend_run.log / frontend_run.log)
echo ============================================================
start "" "http://localhost:5173"
pause
