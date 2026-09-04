@echo off
echo.
echo ============================================
echo   ECO STRUCT - Actualizar Dashboard
echo ============================================
echo.
echo [1/3] Regenerando dashboard...
echo.

python regenerar_dashboard.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: No se pudo regenerar el dashboard.
    echo Verifica que Python este instalado y accesible.
    echo.
    pause
    exit /b 1
)

echo.
echo OK: Dashboard actualizado correctamente.
echo.

echo [2/3] Regenerando Excel...
echo.

python crear_excel_completo.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: No se pudo regenerar el Excel.
    echo.
    pause
    exit /b 1
)

echo.
echo OK: Excel actualizado correctamente.
echo.

echo [3/3] Preguntando si quieres subir a GitHub...
echo.

set /p SUBIR="Quieres subir a GitHub Pages? (S/N): "
if /I "%SUBIR%"=="S" (
    call subir_a_github.bat
) else (
    echo.
    echo Abre dashboard.html en tu navegador para ver los cambios.
)

echo.
pause
