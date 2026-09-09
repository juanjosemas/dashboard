@echo off
echo.
echo ============================================
echo   ECO STRUCT - Subir Dashboard a GitHub
echo ============================================
echo.

REM -- Paso 1: Verificar repositorio git --
echo [1/4] Verificando repositorio git...
git status >nul 2>&1
if %errorlevel% neq 0 (
    echo No es un repositorio git. Inicializando...
    git init
    git branch -M main
    echo OK: Repositorio inicializado.
) else (
    echo OK: Repositorio git detectado.
)
echo.

REM -- Paso 2: Configurar remote si no existe --
echo [2/4] Verificando conexion con GitHub...
git remote get-url origin >nul 2>&1
if %errorlevel% neq 0 (
    git remote add origin https://github.com/juanjosemas/dashboard.git
    echo OK: Conectado a GitHub.
) else (
    echo OK: Conectado a GitHub.
)
echo.

REM -- Paso 3: Sincronizar con GitHub (pull antes de push) --
echo [3/4] Sincronizando con GitHub...
git stash >nul 2>&1
git pull --rebase origin main
git stash pop >nul 2>&1
echo OK: Sincronizado.
echo.

REM -- Paso 4: Añadir archivos, commitear y subir --
echo [4/4] Preparando archivos y subiendo...
git add dashboard.html
git add dashboard_v2.html
git add switchYear.js
git add logo_ecostruct.png
git add datos_ecostruct.json
git add ECO_STRUCT_Datos.xlsx
git add README.md
git commit -m "Actualizacion del dashboard"
git push -u origin main

if %errorlevel% neq 0 (
    echo.
    echo ERROR: No se pudo subir. Comprueba:
    echo   1. Que el repositorio "dashboard" existe en GitHub
    echo   2. Que tienes conexion a internet
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   LISTO! Todo actualizado en GitHub.
echo   Visible en 1-2 minutos en:
echo   https://juanjosemas.github.io/dashboard/dashboard.html
echo ============================================
echo.
pause
