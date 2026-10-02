$f = "C:\Users\jjmax\Downloads\Control Gasolina\Control_Gasolina_Empresa.xlsx"
$backupDir = "C:\Users\jjmax\Downloads\Control Gasolina\Copias"
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backup = Join-Path $backupDir ("Control_Gasolina_Empresa_" + $stamp + ".xlsx")
Copy-Item -Path $f -Destination $backup
Write-Output ("BACKUP: " + $backup)

$xl = $null; $wb = $null
try {
    $xl = New-Object -ComObject Excel.Application
    $xl.Visible = $false
    $xl.DisplayAlerts = $false
    $wb = $xl.Workbooks.Open($f)

    $reg = $wb.Worksheets.Item("Registro Gasolina")
    # Comprobaciones de seguridad antes de borrar
    $d5  = $reg.Cells.Item(5,1).Value2
    $d52 = $reg.Cells.Item(52,1).Value2
    $d53 = $reg.Cells.Item(53,1).Value2
    if ($d5 -eq $null -or $d52 -ne $null) { throw "Fila 5 o 52 inesperadas; aborto sin tocar nada" }
    $limite = [datetime]::FromOADate([double]$d53)
    if ($limite -lt [datetime]"2026-09-28") { throw "La fila 53 no es >= 28/09/2026; aborto" }
    $dt5 = [datetime]::FromOADate([double]$d5)
    if ($dt5 -ge [datetime]"2026-09-28") { throw "La fila 5 ya es >= 28/09; nada que borrar" }
    Write-Output ("Borro filas 5:52 de Registro Gasolina (fila 5 = " + $dt5.ToString("dd/MM/yyyy") + ", fila 53 = " + $limite.ToString("dd/MM/yyyy") + ")")
    $reg.Rows("5:52").Delete()

    $rs = $wb.Worksheets.Item("Resumen Mensual por Empleado")
    $rs.Range("A4").Formula = "=DATE(2026,9,1)"

    $xl.Calculate()
    $wb.Save()
    Write-Output "GUARDADO"

    # ---- Verificación ----
    $reg2 = $wb.Worksheets.Item("Registro Gasolina")
    $last = 0
    for ($r = 5; $r -le 40; $r++) { if ($reg2.Cells.Item($r,1).Text -ne "") { $last = $r } }
    Write-Output ("Registro: primera=" + $reg2.Cells.Item(5,1).Text + " ultima=" + $reg2.Cells.Item($last,1).Text + " (fila " + $last + ")")
    # fila TOTAL
    for ($r = $last; $r -le 40; $r++) { if ($reg2.Cells.Item($r,5).Text -eq "TOTAL") { Write-Output ("TOTAL fila " + $r + ": litros=" + $reg2.Cells.Item($r,6).Text + " importe=" + $reg2.Cells.Item($r,7).Text) } }
    $nold = 0
    for ($r = 5; $r -le $last; $r++) {
        $v = $reg2.Cells.Item($r,1).Value2
        if ($v -ne $null) {
            $d = [datetime]::FromOADate([double]$v)
            if ($d -lt [datetime]"2026-09-28") { $nold++ }
        }
    }
    Write-Output ("Registros anteriores al 28/09 restantes: " + $nold)

    Write-Output "--- Resumen Mensual (mes | JOEL | TOTAL) ---"
    foreach ($r in 4..22) {
        $mes = $rs.Cells.Item($r,1).Text
        if ($mes -ne "") { Write-Output ("fila " + $r + ": " + $mes + " | D=" + $rs.Cells.Item($r,4).Text + " | TOTAL=" + $rs.Cells.Item($r,11).Text) }
    }
    $re = $wb.Worksheets.Item("Resumen por Empleado")
    Write-Output ("Resumen por Empleado TOTAL GENERAL: rep=" + $re.Cells.Item(14,2).Text + " litros=" + $re.Cells.Item(14,3).Text + " importe=" + $re.Cells.Item(14,4).Text)
    $des = $wb.Worksheets.Item("DESPLAZAMIENTOS")
    Write-Output ("DESPLAZAMIENTOS: km=" + $des.Range("M4").Text + " a pagar=" + $des.Range("M5").Text)
    $pag = $wb.Worksheets.Item("PAGO GASOLINA")
    foreach ($r in 6..14) {
        $nom = $pag.Cells.Item($r,1).Text
        if ($nom -ne "") { Write-Output ("PAGO " + $nom + " | pagar=" + $pag.Cells.Item($r,5).Text + " dado=" + $pag.Cells.Item($r,6).Text + " dif=" + $pag.Cells.Item($r,7).Text + " " + $pag.Cells.Item($r,8).Text) }
    }
}
finally {
    if ($wb -ne $null) { $wb.Close($false) }
    if ($xl -ne $null) { $xl.Quit() }
    if ($wb -ne $null) { [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($wb) }
    if ($xl -ne $null) { [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl) }
    [GC]::Collect()
}
