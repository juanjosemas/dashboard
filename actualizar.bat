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

if exist INFORME_HUERFANAS.txt (
    echo ---
    echo REVISA EL INFORME DE FACTURAS HUERFANAS:
    findstr /C:"TOTAL:" INFORME_HUERFANAS.txt
    echo Detalle en INFORME_HUERFANAS.txt ^(obras con facturas sin certificacion^)
    echo ---
    echo.
)

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
python -c "f=open('dashboard.html','r',encoding='utf-8');c=f.read();f.close();s=c.find('function generatePDF(){');e=c.find('</script>',s);js=c[s:e];ls=[l.rstrip() for l in js.split(chr(10)) if l.strip()];open('pdf_func.js','w',encoding='utf-8').write(chr(10).join(ls));print('OK: pdf_func.js actualizado -',len(ls),'lineas')"

python regenerar_dashboard_v2.py

echo OK: Dashboard v2 actualizado.
echo.

echo [3/5] Regenerando Excel...
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

echo [4/5] Actualizando copia de seguridad...
echo.

python crear_copia_drive.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo AVISO: La copia local se ha creado, pero revise la sincronizacion con Google Drive.
    echo.
)

echo [5/5] Preguntando si quieres subir a GitHub...
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
