$f = "C:\Users\jjmax\Downloads\Control Gasolina\Control_Gasolina_Empresa.xlsx"
$xl = $null; $wb = $null
try {
    $xl = New-Object -ComObject Excel.Application
    $xl.Visible = $false
    $xl.DisplayAlerts = $false
    $wb = $xl.Workbooks.Open($f)
    $ws = $wb.Worksheets.Item("Resumen Mensual por Empleado")

    Write-Output "--- estado actual A3:K3 (edges 7..10) ---"
    foreach ($e in 7,8,9,10) {
        $b = $ws.Range("A3:K3").Borders.Item($e)
        Write-Output ("edge " + $e + ": line=" + $b.LineStyle + " weight=" + $b.Weight + " color=" + $b.Color)
    }
    Write-Output "--- intento poner edge 8 en medio y releer ---"
    $b8 = $ws.Range("A3:K3").Borders.Item(8)
    $b8.Weight = 3
    Write-Output ("tras set: line=" + $b8.LineStyle + " weight=" + $b8.Weight)
    $b8b = $ws.Range("A3:K3").Borders.Item(8)
    Write-Output ("releido objeto nuevo: line=" + $b8b.LineStyle + " weight=" + $b8b.Weight)
    Write-Output "--- pruebo weight=4 y weight=2 ---"
    $b8.Weight = 4
    Write-Output ("w4 -> " + $ws.Range("A3:K3").Borders.Item(8).Weight)
    $b8.Weight = 2
    Write-Output ("w2 -> " + $ws.Range("A3:K3").Borders.Item(8).Weight)
    $b8.Weight = 3
    Write-Output ("w3 -> " + $ws.Range("A3:K3").Borders.Item(8).Weight)
    Write-Output "--- interior horizontal A4:K5 edge12 ---"
    $i = $ws.Range("A4:K5").Borders.Item(12)
    Write-Output ("line=" + $i.LineStyle + " weight=" + $i.Weight)
    $wb.Save()
    Write-Output "SAVED"
}
finally {
    if ($wb -ne $null) { $wb.Close($false) }
    if ($xl -ne $null) { $xl.Quit() }
    if ($wb -ne $null) { [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($wb) }
    if ($xl -ne $null) { [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl) }
    [GC]::Collect()
}
