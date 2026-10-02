$f = "C:\Users\jjmax\Downloads\Control Gasolina\Control_Gasolina_Empresa.xlsx"
$xl = $null; $wb = $null
try {
    $xl = New-Object -ComObject Excel.Application
    $xl.Visible = $false
    $xl.DisplayAlerts = $false
    $wb = $xl.Workbooks.Open($f)
    $ws = $wb.Worksheets.Item("Resumen Mensual por Empleado")
    $xl.Calculate()
    foreach ($r in 4..8) {
        Write-Output ("fila " + $r + " mes=" + $ws.Cells.Item($r,1).Text + " | JOEL(D)=" + $ws.Cells.Item($r,4).Text + " | TOTAL(K)=" + $ws.Cells.Item($r,11).Text)
    }
    Write-Output ("TOTAL GENERAL fila 22 = " + $ws.Cells.Item(22,11).Text)
    $des = $wb.Worksheets.Item("DESPLAZAMIENTOS")
    Write-Output ("DESPLAZ total km=" + $des.Range("M4").Text + " | total a pagar=" + $des.Range("M5").Text)
    $pag = $wb.Worksheets.Item("PAGO GASOLINA")
    foreach ($r in 6..14) {
        $nom = $pag.Cells.Item($r,1).Text
        if ($nom -ne "") {
            Write-Output ("PAGO " + $nom + " | a pagar=" + $pag.Cells.Item($r,5).Text + " | dado=" + $pag.Cells.Item($r,6).Text + " | dif=" + $pag.Cells.Item($r,7).Text + " | " + $pag.Cells.Item($r,8).Text)
        }
    }
}
finally {
    if ($wb -ne $null) { $wb.Close($false) }
    if ($xl -ne $null) { $xl.Quit() }
    if ($wb -ne $null) { [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($wb) }
    if ($xl -ne $null) { [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl) }
    [GC]::Collect()
}
