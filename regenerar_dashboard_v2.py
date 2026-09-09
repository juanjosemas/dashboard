#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera dashboard_v2.html - Estilo corporativo oscuro moderno
Lee datos de datos_ecostruct.json (generado por extraer_datos.py)
"""
import json
import os
import re

BASE = r'C:\Users\jjmax\Downloads\1'

# Load data
with open(BASE + r'\datos_ecostruct.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

proyectos_data = data['proyectos_data']
sum_cert = data['sum_cert']
sum_directos = data['sum_directos']
sum_prorrateo = data['sum_prorrateo']
sum_mo = data['sum_mo']
sum_horas = data['sum_horas']
sum_coste = data['sum_coste']
sum_margen = data['sum_margen']
total_gastos_comunes = data['total_gastos_comunes']
gg_total = data['gg_total']
veh_total = data['veh_total']
gg_count = data['gg_count']
veh_count = data['veh_count']
total_facturas_dir = data['total_facturas_dir']
all_facturas_dir = data['all_facturas_dir']
gg_cat_map = data['gg_cat_map']
veh_cat_map = data['veh_cat_map']
top10_suppliers = data['top10_suppliers']
top10_proj = data['top10_proj']
mano_obra_all = data['mano_obra_all']
available_years = data['available_years']
yp_data = data['yp_data']
logo_b64 = data['logo_b64']

# Format helpers
def fmt(val):
    if val < 0: return "-" + fmt(-val)
    s = "{:,.2f}".format(val)
    s = s.replace(',', 'X').replace('.', ',').replace('X', '.')
    return s

def fmt_short(val):
    if val < 0: return "-" + fmt_short(-val)
    s = "{:,.0f}".format(val)
    s = s.replace(',', 'X').replace('.', ',').replace('X', '.')
    return s

def mo_cost(m):
    if m['tarifa'] > 0:
        return m['horas'] * m['tarifa']
    return m['coste']

# Certified projects only (for charts)
cert_projects = [p for p in proyectos_data if p['has_cert']]
all_proj = [p for p in proyectos_data]

# Totals
projects_with_margin = len([p for p in cert_projects if p['margen'] > 0])
projects_with_loss = len([p for p in cert_projects if p['margen'] < 0])

# Color palette - corporate dark theme
C_BG = '#0f1923'
C_CARD = '#1a2632'
C_CARD2 = '#1e2d3d'
C_ACCENT = '#00d4aa'  # teal/green
C_ACCENT2 = '#3b82f6'  # blue
C_ORANGE = '#f97316'
C_RED = '#ef4444'
C_YELLOW = '#eab308'
C_PURPLE = '#a855f7'
C_CYAN = '#06b6d4'
C_TEXT = '#e2e8f0'
C_TEXT2 = '#94a3b8'
C_BORDER = '#2d3d4d'
C_SUCCESS = '#22c55e'

lines = []
lines.append('<!DOCTYPE html>')
lines.append('<html lang="es">')
lines.append('<head>')
lines.append('<meta charset="UTF-8">')
lines.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
lines.append('<title>ECO STRUCT - Panel Corporativo</title>')
lines.append('<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"></script>')
lines.append('<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>')
lines.append('<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">')
lines.append('<style>')
lines.append(':root{--bg:#0f1923;--card:#1a2632;--card2:#1e2d3d;--accent:#00d4aa;--accent2:#3b82f6;--orange:#f97316;--red:#ef4444;--yellow:#eab308;--purple:#a855f7;--cyan:#06b6d4;--text:#e2e8f0;--text2:#94a3b8;--border:#2d3d4d;--success:#22c55e;}')
lines.append('*{margin:0;padding:0;box-sizing:border-box;}')
lines.append("body{font-family:'Inter',sans-serif;background:var(--bg);color:var(--text);min-height:100vh;}")
lines.append('.header{background:linear-gradient(135deg,#0f1923 0%,#1a2f42 100%);padding:16px 32px;display:flex;justify-content:space-between;align-items:center;border-bottom:2px solid var(--accent);}')
lines.append('.header h1{font-size:1.3rem;font-weight:300;color:var(--text);letter-spacing:2px;text-transform:uppercase;}')
lines.append('.header h1 strong{font-weight:700;color:var(--accent);}')
lines.append('.header .subtitle{font-size:0.75rem;color:var(--text2);margin-top:2px;}')
lines.append('.container{max-width:1600px;margin:0 auto;padding:20px 24px;}')
lines.append('.kpi-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-bottom:20px;}')
lines.append('.kpi{background:var(--card);border-radius:10px;padding:16px 18px;border:1px solid var(--border);position:relative;overflow:hidden;transition:all .2s;cursor:pointer;}')
lines.append('.kpi:hover{border-color:var(--accent);transform:translateY(-2px);box-shadow:0 8px 24px rgba(0,212,170,0.15);}')
lines.append('.kpi .kpi-icon{position:absolute;top:12px;right:14px;width:36px;height:36px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:1.1rem;}')
lines.append('.kpi .kpi-label{font-size:0.65rem;text-transform:uppercase;letter-spacing:1.5px;color:var(--text2);font-weight:500;margin-bottom:6px;}')
lines.append('.kpi .kpi-value{font-size:1.35rem;font-weight:700;color:var(--text);font-variant-numeric:tabular-nums;}')
lines.append('.kpi .kpi-sub{font-size:0.7rem;color:var(--text2);margin-top:4px;}')
lines.append('.kpi::before{content:"";position:absolute;top:0;left:0;right:0;height:3px;}')
lines.append('.tabs{display:flex;gap:2px;margin-bottom:16px;background:var(--card);border-radius:8px;padding:3px;border:1px solid var(--border);flex-wrap:wrap;}')
lines.append('.tab-btn{padding:9px 18px;border:none;border-radius:6px;cursor:pointer;font-size:0.78rem;font-weight:500;background:transparent;color:var(--text2);transition:all .2s;letter-spacing:0.3px;}')
lines.append('.tab-btn.active{background:var(--accent);color:#0f1923;font-weight:700;}')
lines.append('.tab-btn:hover:not(.active){color:var(--text);background:rgba(255,255,255,0.05);}')
lines.append('.tab-content{display:none;}.tab-content.active{display:block;}')
lines.append('.card{background:var(--card);border-radius:10px;padding:20px;margin-bottom:16px;border:1px solid var(--border);}')
lines.append('.card-title{font-size:0.82rem;font-weight:600;color:var(--text);text-transform:uppercase;letter-spacing:1px;margin-bottom:14px;display:flex;align-items:center;gap:8px;}')
lines.append('.card-title::before{content:"";width:3px;height:16px;background:var(--accent);border-radius:2px;}')
lines.append('.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:16px;}')
lines.append('.grid-3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;}')
lines.append('.chart-box{position:relative;height:340px;}')
lines.append('table{width:100%;border-collapse:collapse;font-size:0.78rem;}')
lines.append('thead th{background:var(--card2);color:var(--text2);padding:10px 12px;text-align:left;font-weight:600;font-size:0.7rem;text-transform:uppercase;letter-spacing:0.5px;border-bottom:2px solid var(--border);white-space:nowrap;}')
lines.append('thead th:first-child{border-radius:6px 0 0 0;}')
lines.append('thead th:last-child{border-radius:0 6px 0 0;}')
lines.append('tbody td{padding:9px 12px;border-bottom:1px solid rgba(255,255,255,0.04);white-space:nowrap;color:var(--text);}')
lines.append('tbody tr:hover{background:rgba(0,212,170,0.05);}')
lines.append('tbody tr:nth-child(even){background:rgba(255,255,255,0.02);}')
lines.append('.num{text-align:right;font-variant-numeric:tabular-nums;}')
lines.append('.pos{color:var(--success);font-weight:600;}')
lines.append('.neg{color:var(--red);font-weight:600;}')
lines.append('.total-row{font-weight:700;background:var(--card2) !important;border-top:2px solid var(--accent);}')
lines.append('.search-box{padding:8px 14px;border:1px solid var(--border);border-radius:6px;font-size:0.8rem;width:260px;outline:none;background:var(--card2);color:var(--text);transition:border-color .2s;}')
lines.append('.search-box:focus{border-color:var(--accent);}')
lines.append('.toolbar{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;flex-wrap:wrap;gap:8px;}')
lines.append('.progress-bar{background:var(--border);border-radius:4px;height:4px;overflow:hidden;width:100%;}')
lines.append('.progress-fill{height:100%;border-radius:4px;}')
lines.append('#projTable{font-size:0.72rem;}')
lines.append('#projTable thead th{padding:6px 4px;font-size:0.64rem;}')
lines.append('#projTable tbody td{padding:5px 4px;}')
lines.append('#projTable tbody td:first-child{white-space:normal;overflow:hidden;text-overflow:ellipsis;max-width:130px;}')
lines.append('#projTable .progress-bar{height:3px;margin-top:2px;}')
lines.append('.year-btn{padding:6px 14px;border:1px solid var(--border);border-radius:16px;cursor:pointer;font-size:0.75rem;font-weight:500;background:var(--card2);color:var(--text2);transition:all .2s;}')
lines.append('.year-btn.active{background:var(--accent);color:#0f1923;border-color:var(--accent);font-weight:700;}')
lines.append('.year-btn:hover:not(.active){border-color:var(--accent);color:var(--text);}')
lines.append('.switch-link{padding:8px 18px;border:1px solid var(--accent);border-radius:6px;cursor:pointer;font-size:0.75rem;font-weight:600;background:transparent;color:var(--accent);text-decoration:none;transition:all .2s;letter-spacing:0.5px;}')
lines.append('.switch-link:hover{background:var(--accent);color:#0f1923;}')
lines.append('.badge{display:inline-block;padding:2px 8px;border-radius:10px;font-size:0.65rem;font-weight:600;}')
lines.append('.badge-green{background:rgba(34,197,94,0.15);color:var(--success);}')
lines.append('.badge-red{background:rgba(239,68,68,0.15);color:var(--red);}')
lines.append('.badge-blue{background:rgba(59,130,246,0.15);color:var(--accent2);}')
lines.append('@media(max-width:900px){.grid-2,.grid-3{grid-template-columns:1fr;}.kpi-grid{grid-template-columns:repeat(2,1fr);}}')
lines.append('</style>')
lines.append('</head>')
lines.append('<body>')

# Header
lines.append('<div class="header">')
lines.append('  <div>')
lines.append('    <h1><strong>ECO STRUCT</strong> &mdash; Panel de Seguimiento</h1>')
lines.append('    <div class="subtitle">Panel de seguimiento de actividades de gestion de proyectos | Constructive Ecosen Spain 2.3</div>')
lines.append('  </div>')
lines.append('  <div style="display:flex;align-items:center;gap:16px">')
lines.append('    <a href="dashboard.html" class="switch-link" title="Cambiar a dashboard clasico">&#9776; Dashboard Clasico</a>')
lines.append('    <div style="display:flex;align-items:center;gap:10px"><img src="' + logo_b64 + '" alt="ECO STRUCT" style="height:42px;width:auto"><div style="text-align:right"><div style="font-size:0.9rem;font-weight:700;color:var(--text)">Constructive Ecosen</div><div style="font-size:0.75rem;color:var(--text2)">Spain 2.3</div></div></div>')
lines.append('  </div>')
lines.append('</div>')

lines.append('<div class="container">')

# KPI Row
margen_color = C_SUCCESS if sum_margen >= 0 else C_RED
efficiency = (sum_coste / sum_cert * 100) if sum_cert > 0 else 0

lines.append('<div class="kpi-grid">')
kpi_items = [
    (C_ACCENT2, '&#128202;', 'Certificaciones', fmt_short(sum_cert) + ' EUR', str(len(cert_projects)) + ' proyectos certificados', "showTab('certificaciones')"),
    (C_ORANGE, '&#128196;', 'Gastos Directos', fmt_short(sum_directos) + ' EUR', str(total_facturas_dir) + ' facturas por obra', "showTab('facturasObra')"),
    (C_YELLOW, '&#127968;', 'Gastos Comunes', fmt_short(total_gastos_comunes) + ' EUR', 'GG ' + fmt_short(gg_total) + ' + VEH ' + fmt_short(veh_total), "showTab('gastosGen')"),
    (C_PURPLE, '&#128119;', 'Mano de Obra', fmt_short(sum_mo) + ' EUR', '{:,}'.format(sum_horas) + ' horas', "showTab('manoObra')"),
    (margen_color, '&#128200;', 'Margen Total', fmt(sum_margen) + ' EUR', '{:.1f}%'.format(sum_margen/sum_cert*100 if sum_cert > 0 else 0) + ' sobre certificacion', ''),
]
for color, icon, label, value, sub, onclick in kpi_items:
    lines.append('  <div class="kpi" onclick="%s" style="--kc:%s"><div class="kpi-icon" style="color:%s">%s</div><div class="kpi-label">%s</div><div class="kpi-value" style="color:%s">%s</div><div class="kpi-sub">%s</div></div>' % (onclick, color, color, icon, label, color if 'margen' in label.lower() or 'Margen' in label else 'var(--text)', value, sub))
lines.append('</div>')

# Mini stats row
ben_pct = (projects_with_margin / len(cert_projects) * 100) if cert_projects else 0
lines.append('<div style="display:grid;grid-template-columns:repeat(6,1fr);gap:10px;margin-bottom:16px">')
lines.append('  <div style="background:var(--card);border:1px solid var(--border);border-radius:8px;padding:12px;text-align:center"><div style="font-size:0.6rem;color:var(--text2);text-transform:uppercase;letter-spacing:1px">Eficiencia</div><div style="font-size:1.1rem;font-weight:700;color:var(--accent)">{:.1f}%</div></div>'.format(100-efficiency))
lines.append('  <div style="background:var(--card);border:1px solid var(--border);border-radius:8px;padding:12px;text-align:center"><div style="font-size:0.6rem;color:var(--text2);text-transform:uppercase;letter-spacing:1px">Beneficio</div><div style="font-size:1.1rem;font-weight:700;color:var(--success)">%d / %d</div></div>' % (projects_with_margin, len(cert_projects)))
lines.append('  <div style="background:var(--card);border:1px solid var(--border);border-radius:8px;padding:12px;text-align:center"><div style="font-size:0.6rem;color:var(--text2);text-transform:uppercase;letter-spacing:1px">Perdida</div><div style="font-size:1.1rem;font-weight:700;color:var(--red)">%d / %d</div></div>' % (projects_with_loss, len(cert_projects)))
lines.append('  <div style="background:var(--card);border:1px solid var(--border);border-radius:8px;padding:12px;text-align:center"><div style="font-size:0.6rem;color:var(--text2);text-transform:uppercase;letter-spacing:1px">Facturas</div><div style="font-size:1.1rem;font-weight:700;color:var(--orange)">{:,}</div></div>'.format(total_facturas_dir))
lines.append('  <div style="background:var(--card);border:1px solid var(--border);border-radius:8px;padding:12px;text-align:center"><div style="font-size:0.6rem;color:var(--text2);text-transform:uppercase;letter-spacing:1px">Horas</div><div style="font-size:1.1rem;font-weight:700;color:var(--purple)">{:,}</div></div>'.format(sum_horas))
lines.append('  <div style="background:var(--card);border:1px solid var(--border);border-radius:8px;padding:12px;text-align:center"><div style="font-size:0.6rem;color:var(--text2);text-transform:uppercase;letter-spacing:1px">Obras</div><div style="font-size:1.1rem;font-weight:700;color:var(--cyan)">{}</div></div>'.format(len(cert_projects)))
lines.append('</div>')

# Tabs
lines.append('<div class="tabs">')
lines.append('  <button class="tab-btn active" onclick="showTab(\'resumen\')">Resumen General</button>')
lines.append('  <button class="tab-btn" onclick="showTab(\'certificaciones\')">Certificaciones</button>')
lines.append('  <button class="tab-btn" onclick="showTab(\'margen\')">Obras</button>')
lines.append('  <button class="tab-btn" onclick="showTab(\'prorrateo\')">Prorrateo</button>')
lines.append('  <button class="tab-btn" onclick="showTab(\'gastosGen\')">Gastos Comunes (%d+%d)</button>' % (gg_count, veh_count))
lines.append('  <button class="tab-btn" onclick="showTab(\'manoObra\')">Mano de Obra</button>')
lines.append('  <button class="tab-btn" onclick="showTab(\'facturasObra\')">Facturas por Obra (%d)</button>' % total_facturas_dir)
# Year selector + PDF
lines.append('  <div style="margin-left:auto;display:flex;align-items:center;gap:8px">')
lines.append('    <span style="font-size:0.65rem;color:var(--text2);text-transform:uppercase;letter-spacing:1px">Ano:</span>')
for _yr_btn in ['todos'] + available_years:
    act = ' active' if _yr_btn == 'todos' else ''
    label = 'Todos' if _yr_btn == 'todos' else _yr_btn
    lines.append('    <button class="year-btn%s" onclick="switchYear(\'%s\',this)">%s</button>' % (act, _yr_btn, label))
lines.append('  </div>')
lines.append('  <div style="margin-left:8px;display:flex;gap:6px;align-items:center">')
lines.append('    <select id="pdfProjectSelect" style="padding:6px 8px;border:1px solid var(--accent);border-radius:4px;font-size:0.75rem;background:var(--card2);color:var(--text);max-width:200px">')
lines.append('      <option value="">Todas las obras</option>')
for p in proyectos_data:
    lines.append('      <option value="%s">%s</option>' % (p['nombre'].replace('"', '&quot;'), p['nombre']))
lines.append('    </select>')
lines.append('    <button id="btnPDF" onclick="generatePDF()" style="background:var(--accent);color:#0f1923;border:none;border-radius:6px;padding:7px 16px;cursor:pointer;font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.5px">PDF</button>')
lines.append('  </div>')
lines.append('</div>')

# === RESUMEN TAB ===
lines.append('<div class="tab-content active" id="tab-resumen">')
lines.append('  <div class="grid-2">')
lines.append('    <div class="card"><div class="card-title">Composicion Global de Costes</div><div style="text-align:center"><canvas id="chartGlobalDonut" width="280" height="280"></canvas></div></div>')
lines.append('    <div class="card"><div class="card-title">Costes por Obra (clic para detalle)</div><div class="chart-box"><canvas id="chartCostStack"></canvas></div></div>')
lines.append('  </div>')
lines.append('  <div class="grid-2">')
lines.append('    <div class="card"><div class="card-title">Margen por Proyecto (clic para detalle)</div><div class="chart-box" style="height:400px"><canvas id="chartMargenBar"></canvas></div></div>')
lines.append('    <div class="card"><div class="card-title">Certificacion vs Coste Total</div><div class="chart-box" style="height:400px"><canvas id="chartComp"></canvas></div></div>')
lines.append('  </div>')
lines.append('</div>')

# === CERTIFICACIONES TAB ===
lines.append('<div class="tab-content" id="tab-certificaciones">')
lines.append('  <div class="card"><div class="card-title">Detalle de Certificaciones por Proyecto</div>')
lines.append('    <div class="chart-box" style="height:450px"><canvas id="chartCertBar"></canvas></div>')
lines.append('  </div>')
lines.append('  <div class="card"><div class="card-title">Tabla de Certificaciones</div>')
lines.append('    <table><thead><tr><th>Proyecto</th><th class="num">Certificacion (EUR)</th><th class="num">% del Total</th></tr></thead><tbody>')
for p in cert_projects:
    lines.append('  <tr><td>%s</td><td class="num">%s</td><td class="num">%.2f%%</td></tr>' % (p['nombre'], fmt(p['certificacion']), p['pct']*100))
lines.append('  <tr class="total-row"><td>TOTAL</td><td class="num">%s</td><td class="num">100.00%%</td></tr>' % fmt(sum_cert))
lines.append('    </tbody></table>')
lines.append('  </div>')
lines.append('</div>')

# === OBRAS TAB ===
lines.append('<div class="tab-content" id="tab-margen">')
lines.append('  <div class="card" id="obra-detail-panel" style="display:none;border:1px solid var(--accent)">')
lines.append('    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">')
lines.append('      <div class="card-title" style="margin:0" id="detail-title" data-nombre="">COMPOSICION</div>')
lines.append('      <div style="display:flex;gap:6px;align-items:center">')
lines.append('        <button onclick="pdfFromDetail()" style="background:var(--accent);color:#0f1923;border:none;border-radius:4px;padding:4px 10px;cursor:pointer;font-size:0.7rem;font-weight:700">PDF Obra</button>')
lines.append('        <button onclick="closeDetail()" style="background:var(--red);color:white;border:none;border-radius:50%;width:28px;height:28px;cursor:pointer;font-size:1rem">&times;</button>')
lines.append('      </div>')
lines.append('    </div>')
lines.append('    <div class="grid-2">')
lines.append('      <div style="text-align:center"><canvas id="detailDonut" width="300" height="300"></canvas></div>')
lines.append('      <div>')
lines.append('        <div id="detail-legend" style="margin-bottom:12px"></div>')
lines.append('        <div style="background:var(--card2);border:1px solid var(--border);border-radius:8px;padding:16px">')
lines.append('          <div id="detail-summary" style="font-size:0.85rem;line-height:1.8"></div>')
lines.append('        </div>')
lines.append('      </div>')
lines.append('    </div>')
lines.append('  </div>')
lines.append('  <div class="card">')
lines.append('    <div class="toolbar"><div class="card-title" style="margin:0">Detalle por Proyecto</div><input type="text" class="search-box" placeholder="Buscar proyecto..." oninput="filterTable(\'projTable\',this.value)"></div>')
lines.append('    <div style="overflow-x:hidden"><table id="projTable"><thead><tr><th>Proyecto</th><th class="num">Certif.</th><th class="num">G.Dir.</th><th class="num">Prorr.</th><th class="num">M.Obra</th><th class="num">TOTAL</th><th class="num">%C/C</th><th>Margen</th></tr></thead><tbody>')

# Obras rows
for p in proyectos_data:
    margen_class = "pos" if p['margen'] >= 0 else "neg"
    bar_width = min(abs(p['margen_pct']), 100)
    bar_color = C_SUCCESS if p['margen'] >= 0 else C_RED
    row_style = '' if p['has_cert'] else ' style="background:rgba(249,115,22,0.05)"'
    cert_label = fmt(p['certificacion']) if p['has_cert'] else '<span style="color:var(--text2)">-</span>'
    prorrateo_label = fmt(p['prorrateo']) if p['has_cert'] else '<span style="color:var(--text2)">-</span>'
    pct_label = '%.1f%%' % p['margen_pct'] if p['has_cert'] else '-'
    name_extra = '' if p['has_cert'] else ' <span style="font-size:0.6rem;color:var(--text2)">(s/c)</span>'
    _dn = p['nombre'][:26] + '..' if len(p['nombre']) > 28 else p['nombre']
    safe_name = p['nombre'].replace('"', '&quot;')
    lines.append('<tr%s><td title="%s"><strong>%s</strong>%s <button onclick="event.stopPropagation();generateObraPDF(\'%s\')" title="PDF" style="background:var(--accent);color:#0f1923;border:none;border-radius:3px;padding:1px 5px;cursor:pointer;font-size:0.6rem;font-weight:700;margin-left:3px">PDF</button></td>' % (row_style, p['nombre'], _dn, name_extra, safe_name))
    lines.append('<td class="num">%s</td><td class="num">%s</td><td class="num">%s</td><td class="num">%s</td><td class="num"><strong>%s</strong></td><td class="num">%s</td>' % (cert_label, fmt(p['gastos_directos']), prorrateo_label, fmt(p['mano_obra_coste']), fmt(p['total_coste']), pct_label))
    lines.append('<td><span class="%s">%s EUR</span><div class="progress-bar" style="margin-top:3px"><div class="progress-fill" style="width:%.0f%%;background:%s"></div></div></td></tr>' % (margen_class, fmt(p['margen']), bar_width, bar_color))

lines.append('<tr class="total-row"><td>TOTAL GENERAL (%d proyectos)</td><td class="num">%s</td><td class="num">%s</td><td class="num">%s</td><td class="num">%s</td><td class="num"><strong>%s</strong></td><td class="num"></td>' % (len(proyectos_data), fmt(sum_cert), fmt(sum_directos), fmt(sum_prorrateo), fmt(sum_mo), fmt(sum_coste)))
if sum_cert > 0:
    lines.append('<td><span class="pos">%s EUR (%.1f%%)</span></td></tr>' % (fmt(sum_margen), sum_margen/sum_cert*100))
else:
    lines.append('<td><span class="neg">%s EUR</span></td></tr>' % fmt(sum_margen))
lines.append('</tbody></table></div></div></div>')

# === PRORRATEO TAB ===
lines.append('<div class="tab-content" id="tab-prorrateo">')
lines.append('  <div class="card"><div class="card-title">Prorrateo de Gastos Comunes</div>')
lines.append('    <p style="font-size:0.8rem;color:var(--text2);margin-bottom:12px">Gastos Generales (<strong>%s EUR</strong>) + Vehiculos (<strong>%s EUR</strong>) = <strong>%s EUR</strong></p>' % (fmt(gg_total), fmt(veh_total), fmt(total_gastos_comunes)))
lines.append('    <div class="grid-2"><div><div class="chart-box"><canvas id="chartProrrBar"></canvas></div></div><div><div class="chart-box"><canvas id="chartProrrPie"></canvas></div></div></div>')
lines.append('  </div>')
lines.append('  <div class="card">')
lines.append('    <div class="toolbar"><div class="card-title" style="margin:0">Tabla de Prorrateo</div><input type="text" class="search-box" placeholder="Buscar..." oninput="filterTable(\'prorrTable\',this.value)"></div>')
lines.append('    <table id="prorrTable"><thead><tr><th>Proyecto</th><th class="num">Certificacion</th><th class="num">% del Total</th><th class="num">Gasto Prorrateado</th></tr></thead><tbody>')
for p in proyectos_data:
    lines.append('<tr><td>%s</td><td class="num">%s</td><td class="num">%.2f%%</td><td class="num">%s</td></tr>' % (p['nombre'], fmt(p['certificacion']), p['pct']*100, fmt(p['prorrateo'])))
lines.append('<tr class="total-row"><td>TOTAL</td><td class="num">%s</td><td class="num">100.00%%</td><td class="num">%s</td></tr>' % (fmt(sum_cert), fmt(total_gastos_comunes)))
lines.append('</tbody></table></div></div>')

# === GASTOS COMUNES TAB ===
lines.append('<div class="tab-content" id="tab-gastosGen">')
lines.append('  <div class="grid-2">')
lines.append('    <div class="card"><div class="card-title">Gastos Generales por Categoria</div><div class="chart-box"><canvas id="chartGG"></canvas></div></div>')
lines.append('    <div class="card"><div class="card-title">Vehiculos</div><div class="chart-box"><canvas id="chartVeh"></canvas></div></div>')
lines.append('  </div>')
# GG detail table
lines.append('  <div class="card"><div class="card-title">Detalle Gastos Generales (%d facturas = %s EUR)</div>' % (gg_count, fmt(gg_total)))
lines.append('    <div style="max-height:500px;overflow-y:auto"><table><thead><tr><th>Codigo</th><th>Fecha</th><th>Titulo</th><th>Cat.</th><th class="num">Importe</th><th>Proveedor</th></tr></thead><tbody>')
for row in all_facturas_dir:
    pass  # Will build from GG rows
# Re-read CSV for GG/VEH detail
import csv as _csv
import io as _io
csv_path = BASE + r'\dashboard\ECO_STRUCT_-_Workspace_Gastos.csv'
with open(csv_path, 'r', encoding='latin-1') as f:
    _c = f.read()
_reader = _csv.DictReader(_io.StringIO(_c), delimiter=';')
for _row in _reader:
    _proy = ''; _imp_str = '0'; _tit = ''; _prov = ''; _fec = ''; _cod = ''
    for _k, _v in _row.items():
        if _k is None: continue
        _kl = _k.lower(); _v = _v.strip() if _v else ''
        if 'proyecto' == _kl: _proy = _v.upper()
        elif 'importe' == _kl: _imp_str = _v
        elif 't' in _kl and 'tulo' in _kl: _tit = _v
        elif 'proveedor' in _kl and 'id' not in _kl: _prov = _v
        elif _kl == 'fecha': _fec = _v
        elif 'digo' in _kl or 'odigo' in _kl: _cod = _v
    _imp = 0.0
    _s = _imp_str.strip().replace('\u20ac', '').strip()
    if re.search(r',\d{1,2}$', _s): _s = _s.replace('.', '').replace(',', '.')
    elif re.search(r'\.\d{1,2}$', _s): _s = _s.replace(',', '')
    else: _s = _s.replace('.', '').replace(',', '')
    try: _imp = float(_s)
    except: _imp = 0.0
    if 'GASTOS GENERALES' in _proy:
        _imp_cls = 'num neg' if _imp < 0 else 'num'
        lines.append('<tr><td style="font-size:0.72rem">%s</td><td>%s</td><td>%s</td><td><span class="badge badge-blue">G.Generales</span></td><td class="%s">%s</td><td style="font-size:0.75rem">%s</td></tr>' % (_cod, _fec, _tit, _imp_cls, fmt(_imp), _prov[:40]))
lines.append('</tbody></table></div></div>')

# VEH detail
lines.append('  <div class="card"><div class="card-title">Detalle Vehiculos (%d facturas = %s EUR)</div>' % (veh_count, fmt(veh_total)))
lines.append('    <div style="max-height:400px;overflow-y:auto"><table><thead><tr><th>Codigo</th><th>Fecha</th><th>Titulo</th><th>Cat.</th><th class="num">Importe</th><th>Proveedor</th></tr></thead><tbody>')
with open(csv_path, 'r', encoding='latin-1') as f:
    _c = f.read()
_reader = _csv.DictReader(_io.StringIO(_c), delimiter=';')
for _row in _reader:
    _proy = ''; _imp_str = '0'; _tit = ''; _prov = ''; _fec = ''; _cod = ''
    for _k, _v in _row.items():
        if _k is None: continue
        _kl = _k.lower(); _v = _v.strip() if _v else ''
        if 'proyecto' == _kl: _proy = _v.upper()
        elif 'importe' == _kl: _imp_str = _v
        elif 't' in _kl and 'tulo' in _kl: _tit = _v
        elif 'proveedor' in _kl and 'id' not in _kl: _prov = _v
        elif _kl == 'fecha': _fec = _v
        elif 'digo' in _kl or 'odigo' in _kl: _cod = _v
    _imp = 0.0
    _s = _imp_str.strip().replace('\u20ac', '').strip()
    if re.search(r',\d{1,2}$', _s): _s = _s.replace('.', '').replace(',', '.')
    elif re.search(r'\.\d{1,2}$', _s): _s = _s.replace(',', '')
    else: _s = _s.replace('.', '').replace(',', '')
    try: _imp = float(_s)
    except: _imp = 0.0
    if 'VEHICULOS' in _proy or 'VEH\u00cdCULOS' in _proy:
        _imp_cls = 'num neg' if _imp < 0 else 'num'
        lines.append('<tr><td style="font-size:0.72rem">%s</td><td>%s</td><td>%s</td><td><span class="badge badge-red">Vehiculo</span></td><td class="%s">%s</td><td style="font-size:0.75rem">%s</td></tr>' % (_cod, _fec, _tit, _imp_cls, fmt(_imp), _prov[:40]))
lines.append('</tbody></table></div></div>')
lines.append('</div>')

# === MANO DE OBRA TAB ===
lines.append('<div class="tab-content" id="tab-manoObra">')
lines.append('  <div class="card"><div class="card-title">Mano de Obra - Desglose por Proyecto</div>')
lines.append('    <p style="font-size:0.8rem;color:var(--text2);margin-bottom:12px">Tarifa: 20 EUR/hora</p>')
lines.append('    <table><thead><tr><th>Proyecto</th><th class="num">Horas</th><th class="num">Tarifa</th><th class="num">Coste Total</th></tr></thead><tbody>')
mo_2026 = [m for m in mano_obra_all if m['year'] == 2026]
mo_2025 = [m for m in mano_obra_all if m['year'] == 2025]
for m in mo_2026:
    tarifa_str = '%d,00' % m['tarifa'] if m['tarifa'] > 0 else 'N/A'
    lines.append('<tr><td>%s</td><td class="num">%d</td><td class="num">%s</td><td class="num">%s</td></tr>' % (m['proyecto'], m['horas'], tarifa_str, fmt(mo_cost(m) if m['tarifa'] > 0 else m['coste'])))
h26 = sum(m['horas'] for m in mo_2026)
c26 = sum((m['horas'] * m['tarifa']) if m['tarifa'] > 0 else m['coste'] for m in mo_2026)
lines.append('<tr class="total-row"><td>SUBTOTAL 2026</td><td class="num">%d</td><td class="num"></td><td class="num">%s</td></tr>' % (h26, fmt(c26)))
if mo_2025:
    lines.append('<tr><td colspan="4" style="background:var(--card2);font-weight:600;padding-top:12px">ANO 2025</td></tr>')
    for m in mo_2025:
        tarifa_str = '%d,00' % m['tarifa'] if m['tarifa'] > 0 else 'N/A'
        lines.append('<tr><td>%s</td><td class="num">%d</td><td class="num">%s</td><td class="num">%s</td></tr>' % (m['proyecto'], m['horas'], tarifa_str, fmt(mo_cost(m) if m['tarifa'] > 0 else m['coste'])))
    h25 = sum(m['horas'] for m in mo_2025)
    c25 = sum((m['horas'] * m['tarifa']) if m['tarifa'] > 0 else m['coste'] for m in mo_2025)
    lines.append('<tr class="total-row"><td>SUBTOTAL 2025</td><td class="num">%d</td><td class="num"></td><td class="num">%s</td></tr>' % (h25, fmt(c25)))
    lines.append('<tr class="total-row" style="border-top:2px solid var(--accent)"><td>TOTAL COMBINADO</td><td class="num">%d</td><td class="num"></td><td class="num">%s</td></tr>' % (h26+h25, fmt(c26+c25)))
lines.append('</tbody></table></div></div>')

# === FACTURAS POR OBRA TAB ===
lines.append('<div class="tab-content" id="tab-facturasObra">')
lines.append('  <div class="grid-2">')
lines.append('    <div class="card"><div class="card-title">Top 10 Proveedores por Importe</div><div class="chart-box" style="height:350px"><canvas id="chartTopProv"></canvas></div></div>')
lines.append('    <div class="card"><div class="card-title">Distribucion por Proyecto (Top 10)</div><div class="chart-box" style="height:350px"><canvas id="chartTopProj"></canvas></div></div>')
lines.append('  </div>')
lines.append('  <div class="card">')
lines.append('    <div class="toolbar"><div class="card-title" style="margin:0">Listado de Facturas <span id="activeFilterBadge" style="display:none;background:var(--red);color:white;padding:2px 10px;border-radius:12px;font-size:0.7rem;margin-left:8px"></span></div><div style="display:flex;gap:6px;align-items:center"><button id="clearFilterBtn" onclick="clearChartFilter()" style="display:none;background:var(--red);color:white;border:none;padding:5px 12px;border-radius:4px;cursor:pointer;font-size:0.75rem">Limpiar</button><input type="text" class="search-box" placeholder="Buscar por proyecto, proveedor, titulo..." oninput="filterTable(\'facturasObraTable\',this.value)"></div></div>')
lines.append('    <div style="max-height:600px;overflow-y:auto"><table id="facturasObraTable"><thead><tr><th>Proyecto</th><th>Codigo</th><th>Fecha</th><th>Titulo</th><th>Proveedor</th><th>Estado</th><th class="num">Importe</th></tr></thead><tbody>')
for f in all_facturas_dir:
    imp_class = 'num neg' if f['importe'] < 0 else 'num'
    lines.append('<tr><td style="font-size:0.72rem">%s</td><td style="font-size:0.72rem">%s</td><td>%s</td><td style="font-size:0.75rem">%s</td><td style="font-size:0.75rem">%s</td><td>%s</td><td class="%s">%s</td></tr>' % (f['proyecto'][:50], f['codigo'], f['fecha'], f['titulo'][:35], f['proveedor'][:35], f['estado'], imp_class, fmt(f['importe'])))
lines.append('</tbody></table></div></div></div>')

lines.append('</div>')  # container end

# === JAVASCRIPT ===
lines.append('<script>')

# Embed year data
lines.append("var yearData=" + json.dumps({
    'sumCert': {k: yp_data[k]['cert'] for k in ['todos'] + available_years},
    'sumDirectos': {k: yp_data[k]['directos'] for k in ['todos'] + available_years},
    'sumProrrateo': {k: yp_data[k]['prorrateo'] for k in ['todos'] + available_years},
    'sumMO': {k: yp_data[k]['mo'] for k in ['todos'] + available_years},
    'sumHoras': {k: yp_data[k]['horas'] for k in ['todos'] + available_years},
    'sumCoste': {k: yp_data[k]['coste'] for k in ['todos'] + available_years},
    'sumMargen': {k: yp_data[k]['margen'] for k in ['todos'] + available_years},
    'ggTotal': {k: yp_data[k]['gg'] for k in ['todos'] + available_years},
    'vehTotal': {k: yp_data[k]['veh'] for k in ['todos'] + available_years},
    'ggCount': {k: yp_data[k]['gg_count'] for k in ['todos'] + available_years},
    'vehCount': {k: yp_data[k]['veh_count'] for k in ['todos'] + available_years},
    'totalFacturasDir': {k: yp_data[k]['nfacturas'] for k in ['todos'] + available_years},
    'proyectos': {k: yp_data[k]['proyectos'] for k in ['todos'] + available_years},
}, ensure_ascii=False, default=str) + ";")

# Chart data
lines.append("var projectData=%s;" % json.dumps([{
    'nombre': p['nombre'], 'certificacion': round(p['certificacion'], 2),
    'gastos_directos': round(p['gastos_directos'], 2), 'prorrateo': round(p['prorrateo'], 2),
    'mano_obra': round(p['mano_obra_coste'], 2), 'total_coste': round(p['total_coste'], 2),
    'margen': round(p['margen'], 2), 'margen_pct': round(p['margen_pct'], 1),
    'has_cert': p['has_cert'],
} for p in proyectos_data], ensure_ascii=False))
lines.append("var certProjects=%s;" % json.dumps([p['nombre'][:25] for p in cert_projects], ensure_ascii=False))
lines.append("var certValues=%s;" % json.dumps([round(p['certificacion'], 2) for p in cert_projects]))
lines.append("var directValues=%s;" % json.dumps([round(p['gastos_directos'], 2) for p in cert_projects]))
lines.append("var prorrValues=%s;" % json.dumps([round(p['prorrateo'], 2) for p in cert_projects]))
lines.append("var moValues=%s;" % json.dumps([round(p['mano_obra_coste'], 2) for p in cert_projects]))
lines.append("var margenValues=%s;" % json.dumps([round(p['margen'], 2) for p in cert_projects]))
lines.append("var margenColors=%s;" % json.dumps([C_SUCCESS if p['margen'] >= 0 else C_RED for p in cert_projects]))
lines.append("var ggLabels=%s;" % json.dumps(list(gg_cat_map.keys())))
lines.append("var ggValues=%s;" % json.dumps(list(gg_cat_map.values())))
lines.append("var vehLabels=%s;" % json.dumps(list(veh_cat_map.keys())))
lines.append("var vehValues=%s;" % json.dumps(list(veh_cat_map.values())))
lines.append("var topProvFull=%s;" % json.dumps([s['name'] for s in top10_suppliers], ensure_ascii=False))
lines.append("var topProjFull=%s;" % json.dumps([p['name'] for p in top10_proj], ensure_ascii=False))

# Chart colors for dark theme
CHART_COLORS = [C_ACCENT2, C_ORANGE, C_ACCENT, C_PURPLE, C_CYAN, C_YELLOW, C_RED, '#64748b', '#818cf8', '#f472b6']

# Tab switching
lines.append("function showTab(id){document.querySelectorAll('.tab-content').forEach(function(t){t.classList.remove('active');});document.querySelectorAll('.tab-btn').forEach(function(b){b.classList.remove('active');});var el=document.getElementById('tab-'+id);if(el)el.classList.add('active');if(event&&event.target&&event.target.classList)event.target.classList.add('active');}")

# Filter
lines.append("function filterTable(tid,q){var rows=document.getElementById(tid).querySelectorAll('tbody tr');q=q.toLowerCase();rows.forEach(function(r){r.style.display=r.textContent.toLowerCase().indexOf(q)>=0?'':'none';});}")

# Detail panel
lines.append("var detailChart=null;")
lines.append("function showDetail(idx){var p=projectData[idx];var panel=document.getElementById('obra-detail-panel');panel.style.display='block';panel.scrollIntoView({behavior:'smooth'});document.getElementById('detail-title').setAttribute('data-nombre',p.nombre);document.getElementById('detail-title').textContent='COMPOSICION \u2014 '+p.nombre;if(detailChart){detailChart.destroy();}var ctx=document.getElementById('detailDonut').getContext('2d');detailChart=new Chart(ctx,{type:'doughnut',data:{labels:['Mano de obra','Facturas','Prorrateo'],datasets:[{data:[p.mano_obra,p.gastos_directos,p.prorrateo],backgroundColor:['%s','%s','%s'],borderWidth:3,borderColor:'%s'}]},options:{responsive:false,cutout:'55%%',plugins:{legend:{display:false}}}});var legendHtml='<div style=\"display:flex;gap:14px;flex-wrap:wrap;margin-bottom:8px\">';legendHtml+='<div><span style=\"display:inline-block;width:10px;height:10px;background:%s;border-radius:2px;margin-right:4px\"></span>Mano de obra: '+p.mano_obra.toLocaleString('es-ES',{minimumFractionDigits:2})+' \u20ac</div>';legendHtml+='<div><span style=\"display:inline-block;width:10px;height:10px;background:%s;border-radius:2px;margin-right:4px\"></span>Facturas: '+p.gastos_directos.toLocaleString('es-ES',{minimumFractionDigits:2})+' \u20ac</div>';legendHtml+='<div><span style=\"display:inline-block;width:10px;height:10px;background:%s;border-radius:2px;margin-right:4px\"></span>Prorrateo: '+p.prorrateo.toLocaleString('es-ES',{minimumFractionDigits:2})+' \u20ac</div>';legendHtml+='</div>';document.getElementById('detail-legend').innerHTML=legendHtml;var mc=p.margen>=0?'%s':'%s';var cs=p.has_cert?p.certificacion.toLocaleString('es-ES',{minimumFractionDigits:2})+' \u20ac':'Sin certificacion';var h='<strong>CERTIFICADO</strong> '+cs+' \u2014 <strong>COSTE TOTAL</strong> '+p.total_coste.toLocaleString('es-ES',{minimumFractionDigits:2})+' \u20ac';h+='<br><span style=\"color:'+mc+';font-size:1.2rem;font-weight:700\">'+(p.margen>=0?'+':'')+p.margen.toLocaleString('es-ES',{minimumFractionDigits:2})+' \u20ac</span>';h+='<br><span style=\"color:'+mc+'\">('+p.margen_pct+String.fromCharCode(37)+')</span>';document.getElementById('detail-summary').innerHTML=h;}" % (C_PURPLE, C_ACCENT2, C_ORANGE, C_BG, C_PURPLE, C_ACCENT2, C_ORANGE, C_SUCCESS, C_RED))
lines.append("function closeDetail(){document.getElementById('obra-detail-panel').style.display='none';}")
lines.append("document.addEventListener('DOMContentLoaded',function(){var rows=document.getElementById('projTable').querySelectorAll('tbody tr');rows.forEach(function(row,i){if(!row.classList.contains('total-row')){row.style.cursor='pointer';row.addEventListener('click',function(){showDetail(i);});row.addEventListener('mouseenter',function(){row.style.background='rgba(0,212,170,0.08)';});row.addEventListener('mouseleave',function(){row.style.background='';});}});});")

# Chart filter
lines.append("function filterByChart(type,idx){var val=type=='prov'?topProvFull[idx]:topProjFull[idx];var table=document.getElementById('facturasObraTable');var rows=table.querySelectorAll('tbody tr');var colIdx=type=='prov'?4:0;var shown=0;rows.forEach(function(row){var cells=row.querySelectorAll('td');if(cells.length>colIdx){var txt=cells[colIdx].textContent.toLowerCase();if(txt.indexOf(val.toLowerCase())>=0){row.style.display='';shown++;}else{row.style.display='none';}}});var badge=document.getElementById('activeFilterBadge');badge.style.display='inline';badge.textContent=type=='prov'?'Proveedor: '+val:'Proyecto: '+val;document.getElementById('clearFilterBtn').style.display='inline';document.getElementById('facturasObra').scrollIntoView({behavior:'smooth',block:'center'});}")
lines.append("function clearChartFilter(){var rows=document.getElementById('facturasObraTable').querySelectorAll('tbody tr');rows.forEach(function(row){row.style.display='';});document.getElementById('activeFilterBadge').style.display='none';document.getElementById('clearFilterBtn').style.display='none';document.querySelector('.search-box').value='';}")

# Charts initialization
_chart_bg = json.dumps(CHART_COLORS[:len(cert_projects)])
lines.append("var gdChart=new Chart(document.getElementById('chartGlobalDonut'),{type:'doughnut',data:{labels:['Gastos Directos','Prorrateo','Mano de Obra'],datasets:[{data:[%s,%s,%s],backgroundColor:['%s','%s','%s'],borderWidth:3,borderColor:'%s'}]},options:{responsive:false,cutout:'60%%',plugins:{legend:{position:'bottom',labels:{color:'#94a3b8',font:{size:12},padding:14}}}}});" % (round(sum_directos,2), round(sum_prorrateo,2), round(sum_mo,2), C_ACCENT2, C_ORANGE, C_PURPLE, C_BG))
lines.append("new Chart(document.getElementById('chartCostStack'),{type:'bar',data:{labels:certProjects,datasets:[{label:'Facturas directas',data:directValues,backgroundColor:'%s'},{label:'Prorrateo',data:prorrValues,backgroundColor:'%s'},{label:'Mano de Obra',data:moValues,backgroundColor:'%s'}]},options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,scales:{x:{stacked:true,ticks:{color:'#94a3b8',callback:function(v){return v.toLocaleString('es-ES')}}},y:{stacked:true,ticks:{color:'#94a3b8'}}},plugins:{legend:{position:'top',labels:{color:'#94a3b8'}}}}});" % (C_ACCENT2, C_ORANGE, C_PURPLE))
lines.append("new Chart(document.getElementById('chartMargenBar'),{type:'bar',data:{labels:certProjects,datasets:[{label:'Margen (EUR)',data:margenValues,backgroundColor:margenColors}]},options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{ticks:{color:'#94a3b8',callback:function(v){return v.toLocaleString('es-ES')}}},y:{ticks:{color:'#94a3b8'}}},onClick:function(e,els){if(els.length>0){showDetail(els[0].index);}}}});")
lines.append("new Chart(document.getElementById('chartComp'),{type:'bar',data:{labels:certProjects,datasets:[{label:'Certificacion',data:certValues,backgroundColor:'%s'},{label:'Coste Total',data:certValues.map(function(c,i){return directValues[i]+prorrValues[i]+moValues[i];}),backgroundColor:'%s'}]},options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'top',labels:{color:'#94a3b8'}}},scales:{x:{ticks:{color:'#94a3b8'}},y:{ticks:{color:'#94a3b8'}}}}});" % (C_ACCENT2, C_ORANGE))
lines.append("new Chart(document.getElementById('chartCertBar'),{type:'bar',data:{labels:certProjects,datasets:[{label:'Certificacion (EUR)',data:certValues,backgroundColor:certProjects.map(function(_,i){return ['%s','%s','%s','%s','%s','%s','%s','%s','%s','%s'][i%%10]}),borderWidth:0}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{ticks:{color:'#94a3b8',maxRotation:45}},y:{ticks:{color:'#94a3b8',callback:function(v){return v.toLocaleString('es-ES')}}}}}});" % tuple(CHART_COLORS[:10]))
lines.append("new Chart(document.getElementById('chartProrrBar'),{type:'bar',data:{labels:certProjects,datasets:[{label:'Prorrateo (EUR)',data:prorrValues,backgroundColor:'%s'}]},options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{ticks:{color:'#94a3b8'}},y:{ticks:{color:'#94a3b8'}}}}});" % C_ORANGE)
lines.append("new Chart(document.getElementById('chartProrrPie'),{type:'pie',data:{labels:certProjects,datasets:[{data:prorrValues,backgroundColor:['%s','%s','%s','%s','%s','%s','%s','%s','%s','%s']}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'right',labels:{color:'#94a3b8',font:{size:10}}}}}});" % tuple(CHART_COLORS[:10]))
lines.append("new Chart(document.getElementById('chartGG'),{type:'doughnut',data:{labels:ggLabels,datasets:[{data:ggValues,backgroundColor:['%s','%s','%s','%s','%s','%s','%s','%s','%s']}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'right',labels:{color:'#94a3b8'}}}}});" % tuple(CHART_COLORS[:9]))
lines.append("new Chart(document.getElementById('chartVeh'),{type:'doughnut',data:{labels:vehLabels,datasets:[{data:vehValues,backgroundColor:['%s','%s','%s','%s','%s','%s','%s']}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'right',labels:{color:'#94a3b8'}}}}});" % tuple(CHART_COLORS[:7]))

# Top 10 charts
top_prov_labels = json.dumps([s['name'][:30] for s in top10_suppliers], ensure_ascii=False)
top_prov_values = json.dumps([s['total'] for s in top10_suppliers])
top_proj_labels = json.dumps([p['name'][:30] for p in top10_proj], ensure_ascii=False)
top_proj_values = json.dumps([p['total'] for p in top10_proj])
lines.append("new Chart(document.getElementById('chartTopProv'),{type:'bar',data:{labels:%s,datasets:[{label:'Importe Total',data:%s,backgroundColor:['%s','%s','%s','%s','%s','%s','%s','%s','%s','%s']}]},options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},onClick:function(e,els){if(els.length>0){filterByChart('prov',els[0].index);}},scales:{x:{ticks:{color:'#94a3b8'}},y:{ticks:{color:'#94a3b8'}}}}});" % (top_prov_labels, top_prov_values, *CHART_COLORS[:10]))
lines.append("new Chart(document.getElementById('chartTopProj'),{type:'bar',data:{labels:%s,datasets:[{label:'Gastos Directos',data:%s,backgroundColor:['%s','%s','%s','%s','%s','%s','%s','%s','%s','%s']}]},options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},onClick:function(e,els){if(els.length>0){filterByChart('proj',els[0].index);}},scales:{x:{ticks:{color:'#94a3b8'}},y:{ticks:{color:'#94a3b8'}}}}});" % (top_proj_labels, top_proj_values, *CHART_COLORS[:10]))

# Year switching
# Year switching JS - read from external file to avoid escaping issues
with open(BASE + r'\switchYear.js', 'r', encoding='utf-8') as _f:
    _switch_js = _f.read()
for _jl in _switch_js.split('\n'):
    if _jl.strip():
        lines.append(_jl)
_js_lines_done = True

# PDF generation (extracts JS from regenerar_dashboard.py)
import ast as _ast, re as _re, os as _os
_v1_path = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), 'regenerar_dashboard.py')
with open(_v1_path, 'r', encoding='utf-8') as _f:
    _v1_lines = _f.readlines()
for _pl in _v1_lines[1085:1320]:
    _s = _pl.strip()
    if not _s or _s.startswith('#'):
        continue
    _m = _re.match(r"lines\.append\((.+)\)", _s)
    if _m:
        try:
            _content = _ast.literal_eval(_m.group(1))
            lines.append(_content)
        except:
            pass

lines.append('</script>')
lines.append('</body>')
lines.append('</html>')

html = '\n'.join(lines)
with open(BASE + r'\dashboard_v2.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("dashboard_v2.html generado correctamente")
print("  Estilo: Corporativo oscuro moderno")
print("  Certificaciones: {:,.2f} EUR".format(sum_cert))
print("  Gastos Directos: {:,.2f} EUR".format(sum_directos))
print("  Gastos Comunes:  {:,.2f} EUR".format(total_gastos_comunes))
print("  Mano de Obra:    {:,.2f} EUR ({} horas)".format(sum_mo, sum_horas))
print("  MARGEN:          {:,.2f} EUR ({:.1f}%)".format(sum_margen, sum_margen/sum_cert*100 if sum_cert > 0 else 0))
