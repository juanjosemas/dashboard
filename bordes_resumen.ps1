$f = "C:\Users\jjmax\Downloads\Control Gasolina\Control_Gasolina_Empresa.xlsx"
$backup = "C:\Users\jjmax\Downloads\Control Gasolina\Copias\Control_Gasolina_Empresa_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".xlsx"
Copy-Item -Path $f -Destination $backup
Write-Output ("BACKUP: " + $backup)

$xl = $null; $wb = $null
try {
    $xl = New-Object -ComObject Excel.Application
    $xl.Visible = $false
    $xl.DisplayAlerts = $false
    $wb = $xl.Workbooks.Open($f)
    $ws = $wb.Worksheets.Item("Resumen Mensual por Empleado")

    # XlBordersIndex: 7=Left 8=Top 9=Bottom 10=Right 11=InsideVertical 12=InsideHorizontal
    # XlBorderWeight: 2=Thin 3=Medium   XlLineStyle: 1=Continuous

    # 1) Rejilla fina en toda la tabla (cabecera fila 3 + meses 4-21 + total fila 22)
    $tbl = $ws.Range("A3:K22")
    foreach ($e in 7,8,9,10,11,12) {
        $b = $tbl.Borders.Item($e)
        $b.LineStyle = 1
        $b.Weight = 2
    }

    # 2) Cabecera: linea media arriba y abajo
    foreach ($e in 8,9) {
        $b = $ws.Range("A3:K3").Borders.Item($e)
        $b.LineStyle = 1
        $b.Weight = 3
    }

    # 3) Fila TOTAL GENERAL: linea media arriba y abajo
    foreach ($e in 8,9) {
        $b = $ws.Range("A22:K22").Borders.Item($e)
        $b.LineStyle = 1
        $b.Weight = 3
    }

    # 4) Separador vertical grueso tras la columna Mes (A)
    $sep = $ws.Range("A3:A22").Borders.Item(10)
    $sep.LineStyle = 1
    $sep.Weight = 3

    # 5) Separador vertical grueso antes de la columna TOTAL (K)
    $sepK = $ws.Range("K3:K22").Borders.Item(7)
    $sepK.LineStyle = 1
    $sepK.Weight = 3

    $wb.Save()
    Write-Output "GUARDADO"

    # ---- Verificación ----
    function Chk($rng, $edge, $name) {
        $b = $ws.Range($rng).Borders.Item($edge)
        Write-Output ($rng + " " + $name + ": line=" + $b.LineStyle + " weight=" + $b.Weight)
    }
    Chk "A4:K5" 12 "interior horizontal (entre meses)"
    Chk "B4:C5" 11 "interior vertical (entre columnas)"
    Chk "A3:K3" 8  "cabecera arriba"
    Chk "A3:K3" 9  "cabecera abajo"
    Chk "A22:K22" 8 "total arriba"
    Chk "A22:K22" 9 "total abajo"
    Chk "A3:A22" 10 "separador columna Mes"
    Chk "K3:K22" 7  "separador columna TOTAL"
}
finally {
    if ($wb -ne $null) { $wb.Close($false) }
    if ($xl -ne $null) { $xl.Quit() }
    if ($wb -ne $null) { [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($wb) }
    if ($xl -ne $null) { [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl) }
    [GC]::Collect()
}
