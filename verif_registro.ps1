$f = "C:\Users\jjmax\Downloads\Control Gasolina\Control_Gasolina_Empresa.xlsx"
$xl = $null; $wb = $null
try {
    $xl = New-Object -ComObject Excel.Application
    $xl.Visible = $false
    $xl.DisplayAlerts = $false
    $wb = $xl.Workbooks.Open($f)
    $ws = $wb.Worksheets.Item("Registro Gasolina")
    $xl.Calculate()
    $last = $ws.UsedRange.Rows.Count
    Write-Output ("Usadas filas: " + $last)
    # cabecera fila 4? buscar última fila con dato en col A
    $lastData = 0
    for ($r = 5; $r -le $last; $r++) {
        if ($ws.Cells.Item($r,1).Text -ne "") { $lastData = $r }
    }
    Write-Output ("Última fila con fecha: " + $lastData)
    Write-Output "--- Últimos 8 registros (Fecha | Trabajador | Litros | Importe | ...) ---"
    $from = [Math]::Max(5, $lastData - 7)
    for ($r = $from; $r -le $lastData; $r++) {
        $line = @()
        foreach ($c in 1..8) { $line += $ws.Cells.Item($r,$c).Text }
        Write-Output ("fila " + $r + ": " + ($line -join " | "))
    }
    Write-Output "--- Registros con fecha de hoy 01/10/2026 ---"
    $hoy = 0
    for ($r = 5; $r -le $lastData; $r++) {
        $v = $ws.Cells.Item($r,1).Value2
        try {
            $d = [datetime]::FromOADate([double]$v)
            if ($d -ge [datetime]"2026-10-01" -and $d -lt [datetime]"2026-10-02") {
                $hoy++
                $line = @()
                foreach ($c in 1..8) { $line += $ws.Cells.Item($r,$c).Text }
                Write-Output ("fila " + $r + ": " + ($line -join " | "))
            }
        } catch { }
    }
    Write-Output ("Total registros hoy: " + $hoy)
    # resumen mensual filas 4-8 otra vez
    $rs = $wb.Worksheets.Item("Resumen Mensual por Empleado")
    Write-Output "--- Resumen mensual (mes | TOTAL) ---"
    foreach ($r in 4..22) {
        $mes = $rs.Cells.Item($r,1).Text
        if ($mes -ne "") { Write-Output ("fila " + $r + ": " + $mes + " | TOTAL=" + $rs.Cells.Item($r,11).Text) }
    }
}
finally {
    if ($wb -ne $null) { $wb.Close($false) }
    if ($xl -ne $null) { $xl.Quit() }
    if ($wb -ne $null) { [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($wb) }
    if ($xl -ne $null) { [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl) }
    [GC]::Collect()
}
