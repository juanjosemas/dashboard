@echo off
echo.
echo ============================================
echo   VISOR DE PRESUPUESTOS - PROVEEDORES
echo   ECO STRUCT
echo ============================================
echo.
echo Iniciando visor...
echo.

python "%~dp0ver_proveedores.py"

if errorlevel 1 (
    echo.
    echo ❌ Error al ejecutar. ¿Tienes Python instalado?
    echo    Descarga desde: https://www.python.org/downloads/
    echo.
    pause
)
