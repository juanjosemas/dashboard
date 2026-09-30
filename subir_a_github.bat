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

REM -- Paso 3: Añadir y commitear todos los archivos --
echo [3/4] Añadiendo archivos...
REM El .gitignore descarta el ZIP de copia de seguridad, las carpetas
REM temporales y __pycache__, asi que aqui se puede anadir todo el proyecto.
git add -A
git commit -m "Actualizacion del dashboard"
echo.

REM -- Paso 4: Subir a GitHub --
echo [4/4] Subiendo a GitHub...
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
