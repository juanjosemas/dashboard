@echo off
echo.
echo ============================================
echo   ECO STRUCT - Subir Dashboard a GitHub
echo ============================================
echo.

REM -- Paso 1: Regenerar dashboard --
echo [1/6] Regenerando dashboard...
python regenerar_dashboard.py
if %errorlevel% neq 0 (
    echo ERROR: No se pudo regenerar el dashboard.
    pause
    exit /b 1
)
echo OK: Dashboard regenerado correctamente.
echo.

REM -- Paso 2: Regenerar Excel --
echo [2/6] Regenerando Excel...
python crear_excel_completo.py
if %errorlevel% neq 0 (
    echo ERROR: No se pudo regenerar el Excel.
    pause
    exit /b 1
)
echo OK: Excel regenerado correctamente.
echo.

REM -- Paso 3: Verificar repositorio git --
echo [3/6] Verificando repositorio git...
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

REM -- Paso 4: Configurar remote si no existe --
echo [4/6] Verificando conexion con GitHub...
git remote get-url origin >nul 2>&1
if %errorlevel% neq 0 (
    git remote add origin https://github.com/juanjosemas/dashboard.git
    echo OK: Conectado a GitHub.
) else (
    echo OK: Conectado a GitHub.
)
echo.

REM -- Paso 5: Añadir archivos --
echo [5/6] Preparando archivos para subir...
git add dashboard.html
git add logo_ecostruct.png 2>nul
git add README.md 2>nul
git add ECO_STRUCT_Datos.xlsx 2>nul
git commit -m "Actualizacion del dashboard"
echo OK: Cambios preparados.
echo.

REM -- Paso 6: Subir a GitHub --
echo [6/6] Subiendo a GitHub...
echo Sincronizando con GitHub...
git pull --rebase origin main
if %errorlevel% neq 0 (
    echo ERROR: No se pudo sincronizar. Comprueba tu conexion a internet.
    pause
    exit /b 1
)
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
