@echo off
echo.
echo ============================================
echo   ECO STRUCT - Actualizar Dashboard
echo ============================================
echo.
echo [1/4] Extrayendo datos frescos...
echo.

python extraer_datos.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: No se pudieron extraer los datos.
echo.
    pause
    exit /b 1
)

echo OK: Datos extraidos correctamente.
echo.

echo [2/4] Regenerando dashboards...
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
echo OK: Dashboard v1 actualizado.
echo.

echo Generando pdf_func.js desde v1...
python -c "f=open('dashboard.html','r',encoding='utf-8');c=f.read();f.close();s=c.find('function generatePDF(){');e=c.find('</script>',s);so=c.rfind('<script>',0,s);js=c[so+8:e];ls=[l.rstrip() for l in js.split(chr(10)) if l.strip()];open('pdf_func.js','w',encoding='utf-8').write(chr(10).join(ls));print('OK: pdf_func.js actualizado -',len(ls),'lineas')"

python regenerar_dashboard_v2.py

echo OK: Dashboard v2 actualizado.
echo.

echo [3/4] Regenerando Excel...
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

echo [4/4] Preguntando si quieres subir a GitHub...
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
