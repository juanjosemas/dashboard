#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrae todos los datos de los 3 CSV a datos_ecostruct.json
Incluye datos por mes para filtrado mensual.
Solo trabaja con año 2026.
"""
import csv
import io
import re
import openpyxl
import collections
import json

def parse_euro_amount(s):
    if isinstance(s, (int, float)):
        return float(s)
    s = str(s).strip().replace('\u20ac', '').replace('\x80', '').strip()
    if re.search(r',\d{1,2}$', s):
        s = s.replace('.', '').replace(',', '.')
    elif re.search(r'\.\d{1,2}$', s):
        s = s.replace(',', '')
    else:
        s = s.replace('.', '').replace(',', '')
    try:
        return float(s)
    except:
        return 0.0

BASE = r'C:\Users\jjmax\Downloads\1'
DASH = BASE + r'\dashboard'

MONTH_NAMES = ['ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO',
               'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE']
MONTH_ES = {1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio',
            7: 'Julio', 8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}

# Current month - only count data up to this month
import datetime as _dt
CURRENT_MONTH = _dt.datetime.now().month  # e.g. 9 for September

# ===== 1. CERTIFICACIONES POR MESES 2026 =====
certificaciones = []
cert_by_month = {}  # {month_num: {name: amount}}
cert_xlsx_path = DASH + r'\CERTIFICACIONES POR MESES 2026.xlsx'
wb_cert = openpyxl.load_workbook(cert_xlsx_path, data_only=True)
ws_cert = wb_cert.active

for row_idx in range(4, ws_cert.max_row + 1):
    proyecto = str(ws_cert.cell(row_idx, 1).value or '').strip()
    if not proyecto:
        continue
    # Extract per-month values (columns 2-13), only up to current month
    meses = {}
    for mi in range(1, CURRENT_MONTH + 1):
        cell_val = ws_cert.cell(row_idx, mi + 1).value
        val = parse_euro_amount(cell_val) if cell_val is not None else 0
        if val > 0:
            meses[mi] = val
            if mi not in cert_by_month:
                cert_by_month[mi] = {}
            cert_by_month[mi][proyecto] = val
    
    # Use sum of months up to current month
    importe_filtrado = sum(meses.values())
    if importe_filtrado > 0 and proyecto:
        certificaciones.append({'nombre': proyecto, 'importe': importe_filtrado, 'year': '2026', 'meses': meses})
    elif proyecto:
        certificaciones.append({'nombre': proyecto, 'importe': 0, 'year': '2026', 'meses': {}})

# ===== 2. MANO DE OBRA POR MESES 2026 =====
mano_obra_all = []
mo_by_month = {}  # {month_num: [{proyecto, horas, tarifa, coste}]}
mo_xlsx_path = DASH + r'\GASTOS MANO DE OBRA POR MESES 2026.xlsx'
wb_mo = openpyxl.load_workbook(mo_xlsx_path, data_only=True)
ws_mo = wb_mo.active

for row_idx in range(4, ws_mo.max_row + 1):
    proyecto = str(ws_mo.cell(row_idx, 1).value or '').strip()
    if not proyecto:
        continue

    # Columns: 1=name, 15=PRECIO/HORA, 16=SUMA HORAS, 17=GASTO TOTAL
    tarifa_val = ws_mo.cell(row_idx, 15).value
    tarifa = parse_euro_amount(tarifa_val) if tarifa_val is not None else 0
    horas_val = ws_mo.cell(row_idx, 16).value
    horas_total = int(parse_euro_amount(horas_val)) if horas_val is not None else 0
    coste_val = ws_mo.cell(row_idx, 17).value
    coste_total = parse_euro_amount(coste_val) if coste_val is not None else 0

    # Extract per-month hours (columns 2-13), only up to current month
    meses = {}
    for mi in range(1, CURRENT_MONTH + 1):
        cell_val = ws_mo.cell(row_idx, mi + 1).value
        h = int(parse_euro_amount(cell_val)) if cell_val is not None else 0
        if h > 0:
            meses[mi] = h
            if mi not in mo_by_month:
                mo_by_month[mi] = []
            mo_coste_m = h * tarifa if tarifa > 0 else 0
            mo_by_month[mi].append({'proyecto': proyecto, 'horas': h, 'tarifa': tarifa, 'coste': mo_coste_m})

    # Calculate filtered totals (only months up to current month)
    horas_filtradas = sum(meses.values())
    coste_filtrado = horas_filtradas * tarifa if tarifa > 0 else 0
    
    # Handle entries with no hours but with a total cost (e.g. MURO VECINO, OBRA CAMPO)
    if horas_filtradas == 0 and coste_filtrado == 0 and coste_total > 0:
        coste_filtrado = coste_total
        if CURRENT_MONTH > 0:
            coste_por_mes = coste_total / CURRENT_MONTH
            for mi in range(1, CURRENT_MONTH + 1):
                meses[mi] = 0
                if mi not in mo_by_month:
                    mo_by_month[mi] = []
                mo_by_month[mi].append({'proyecto': proyecto, 'horas': 0, 'tarifa': 0, 'coste': round(coste_por_mes, 2)})
    
    if horas_filtradas > 0 or coste_filtrado > 0:
        if tarifa <= 0 and horas_filtradas > 0 and coste_filtrado > 0:
            tarifa = coste_filtrado / horas_filtradas if horas_filtradas > 0 else 0
        mano_obra_all.append({
            'proyecto': proyecto, 'horas': horas_filtradas, 'tarifa': tarifa,
            'coste': round(coste_filtrado, 2), 'year': 2026, 'meses': meses
        })

# ===== 3. CSV GASTOS =====
csv_path = DASH + r'\ECO_STRUCT_-_Workspace_Gastos.csv'
with open(csv_path, 'r', encoding='latin-1') as f:
    content = f.read()

reader = csv.DictReader(io.StringIO(content), delimiter=';')
gg_total = 0.0; gg_count = 0; veh_total = 0.0; veh_count = 0
directos_por_proyecto = collections.defaultdict(lambda: {'total': 0.0, 'count': 0, 'facturas': []})
# Per-month tracking for gastos
gg_by_month = collections.Counter()
veh_by_month = collections.Counter()
dir_by_month = collections.defaultdict(lambda: collections.defaultdict(lambda: {'total': 0.0, 'count': 0}))

for row in reader:
    proyecto = ''; importe_str = '0'; titulo = ''; proveedor = ''; fecha = ''; codigo = ''; estado = ''; proyecto_id = ''
    for key, val in row.items():
        if key is None: continue
        key_lower = key.lower(); val = val.strip() if val else ''
        if 'proyecto' == key_lower: proyecto = val.upper()
        elif 'proyecto id' == key_lower: proyecto_id = val.strip()
        elif 'importe' == key_lower: importe_str = val
        elif 't' in key_lower and 'tulo' in key_lower: titulo = val
        elif 'proveedor' in key_lower and 'id' not in key_lower: proveedor = val
        elif key_lower == 'fecha': fecha = val
        elif 'digo' in key_lower or 'odigo' in key_lower: codigo = val
        elif 'estado' == key_lower: estado = val

    importe = parse_euro_amount(importe_str)
    _f_parts = fecha.split('/') if fecha else []
    _f_yr = _f_parts[2] if len(_f_parts) == 3 else ''
    _f_month = int(_f_parts[1]) if len(_f_parts) >= 2 and _f_parts[1].isdigit() else 0
    
    # Skip invoices from future months
    if _f_month > CURRENT_MONTH:
        continue

    if 'GASTOS GENERALES' in proyecto:
        gg_total += importe; gg_count += 1
        if _f_month: gg_by_month[_f_month] += importe
    elif 'VEHICULOS' in proyecto or 'VEH\u00cdCULOS' in proyecto:
        veh_total += importe; veh_count += 1
        if _f_month: veh_by_month[_f_month] += importe
    elif proyecto:
        if proyecto_id and not proyecto[0].isdigit():
            proyecto = proyecto_id + ' - ' + proyecto
        directos_por_proyecto[proyecto]['total'] += importe
        directos_por_proyecto[proyecto]['count'] += 1
        directos_por_proyecto[proyecto]['facturas'].append({
            'codigo': codigo, 'fecha': fecha, 'titulo': titulo,
            'importe': importe, 'proveedor': proveedor, 'estado': estado
        })
        if _f_month:
            dir_by_month[_f_month][proyecto]['total'] += importe
            dir_by_month[_f_month][proyecto]['count'] += 1

total_gastos_comunes = gg_total + veh_total
total_directos_csv = sum(d['total'] for d in directos_por_proyecto.values())
total_facturas_dir = sum(d['count'] for d in directos_por_proyecto.values())

all_facturas_dir = []
for proj_csv, d in directos_por_proyecto.items():
    for f in d['facturas']:
        all_facturas_dir.append({
            'proyecto': proj_csv, 'codigo': f.get('codigo', ''), 'fecha': f.get('fecha', ''),
            'titulo': f.get('titulo', ''), 'proveedor': f.get('proveedor', ''),
            'estado': f.get('estado', ''), 'importe': f.get('importe', 0)
        })
all_facturas_dir.sort(key=lambda x: (x['proyecto'], -abs(x['importe'])))
for _fi in all_facturas_dir:
    _f_parts = _fi.get('fecha', '').split('/')
    _fi['year'] = _f_parts[2] if len(_f_parts) == 3 else ''
    _fi['month'] = int(_f_parts[1]) if len(_f_parts) >= 2 and _f_parts[1].isdigit() else 0

# ===== 4. MAPEO CSV -> CERTIFICACIONES =====
csv_to_cert = {}
for proj_csv in directos_por_proyecto:
    proj_upper = proj_csv.upper()
    for cert in certificaciones:
        cert_upper = cert['nombre'].upper()
        if cert_upper in proj_upper or proj_upper in cert_upper:
            csv_to_cert[proj_csv] = cert['nombre']; break
        kw = False
        if 'FORMENTERA' in proj_upper and 'FORMENTERA' in cert_upper:
            if ('12' in proj_upper and '12' in cert_upper) or ('14' in proj_upper and '14' in cert_upper):
                if ('JOAQUIN' in proj_upper and 'JOAQUIN' in cert_upper) or ('JUANMA' in proj_upper and 'JUANMA' in cert_upper):
                    kw = True
        if 'EDIFICIO ALICANTE' in proj_upper and 'ALICANTE' in cert_upper and 'PARTE DIFICIL' in cert_upper: kw = True
        if 'CUARTEL DE ARTILLERIA' in proj_upper and 'MURCIA' in cert_upper and 'PARTE DIFICIL' in cert_upper: kw = True
        if 'EDIFICIO' in proj_upper and 'EDIFICIO' in cert_upper: kw = True
        if 'CUARTEL' in proj_upper and 'CUARTEL' in cert_upper: kw = True
        if 'SANTA ROSA' in proj_upper and 'SANTA ROSA' in cert_upper: kw = True
        if 'CARTAGENA' in proj_upper and 'CARTAGENA' in cert_upper: kw = True
        if 'CASTILLO' in proj_upper and 'CASTILLO' in cert_upper: kw = True
        if 'GARAJE' in proj_upper and 'GARAJE' in cert_upper: kw = True
        if 'PEREAMAR' in proj_upper and 'PEREAMAR' in cert_upper: kw = True
        if 'CBS' in proj_upper and 'CBS' in cert_upper: kw = True
        if 'CEMENTERIO' in proj_upper and 'CEMENTERIO' in cert_upper: kw = True
        if 'BARINAS' in proj_upper and 'BARINAS' in cert_upper: kw = True
        if 'ALBERCA' in proj_upper and 'ALBERCA' in cert_upper: kw = True
        if 'PLAZA CIRCULAR' in proj_upper and 'PLAZA CIRCULAR' in cert_upper: kw = True
        if 'HELENA' in proj_upper and 'HELENA' in cert_upper: kw = True
        if 'A-13' in proj_upper and 'A-13' in cert_upper: kw = True
        if 'CARLA' in proj_upper and 'CARLA' in cert_upper: kw = True
        if 'PADRE TRINI' in proj_upper and 'PADRE TRINI' in cert_upper: kw = True
        if 'PISO IBI' in proj_upper and 'PISO IBI' in cert_upper: kw = True
        if 'LUC2' in proj_upper and 'LUC2' in cert_upper: kw = True
        if 'MEJORA DEL VALLADO' in proj_upper and 'CASTILLO' in cert_upper: kw = True
        if ('ANGEL' in proj_upper or 'NGEL' in proj_upper) and 'HELENA' in cert_upper and 'CARMEN' in proj_upper: kw = True
        if 'HUERTO CAPUCHINOS' in proj_upper and 'HUERTO CAPUCHINOS' in cert_upper: kw = True
        if kw:
            csv_to_cert[proj_csv] = cert['nombre']; break

cert_to_csvs = {}
for csv_proj, cert_mapped in csv_to_cert.items():
    if cert_mapped not in cert_to_csvs: cert_to_csvs[cert_mapped] = []
    cert_to_csvs[cert_mapped].append(csv_proj)

all_project_names = []
_all_pn_set = set()
for cert in certificaciones:
    if cert['nombre'] not in _all_pn_set:
        all_project_names.append(cert['nombre']); _all_pn_set.add(cert['nombre'])
for csv_proj in directos_por_proyecto:
    if csv_proj not in csv_to_cert and csv_proj not in _all_pn_set:
        all_project_names.append(csv_proj); _all_pn_set.add(csv_proj)

cert_lookup = {}
for c in certificaciones:
    name = c['nombre']
    if name in cert_lookup:
        cert_lookup[name]['importe'] += c['importe']
        for m, v in c.get('meses', {}).items():
            cert_lookup[name].setdefault('meses', {})[m] = cert_lookup[name].get('meses', {}).get(m, 0) + v
    else:
        cert_lookup[name] = {'nombre': name, 'importe': c['importe'], 'meses': dict(c.get('meses', {}))}

total_cert = sum(c['importe'] for c in cert_lookup.values())

all_display_names = []
_adn_set = set()
for p in certificaciones:
    if p['nombre'] not in _adn_set:
        all_display_names.append(p['nombre']); _adn_set.add(p['nombre'])
for csv_proj in directos_por_proyecto:
    if csv_proj not in csv_to_cert and csv_proj not in _adn_set:
        all_display_names.append(csv_proj); _adn_set.add(csv_proj)

def match_mo_to_project(mo_upper, display_names):
    for dname in display_names:
        dname_upper = dname.upper()
        if dname_upper in mo_upper or mo_upper in dname_upper: return dname
        if 'FORMENTERA' in mo_upper and 'FORMENTERA' in dname_upper:
            if ('12' in mo_upper and '12' in dname_upper) or ('14' in mo_upper and '14' in dname_upper): return dname
            if ('JOAQUIN' in mo_upper and 'JOAQUIN' in dname_upper) or ('JUANMA' in mo_upper and 'JUANMA' in dname_upper): return dname
        if 'CARTAGENA' in mo_upper and 'CARTAGENA' in dname_upper: return dname
        if 'PARTE DIFICIL' in mo_upper and 'PARTE DIFICIL' in dname_upper:
            if 'ALICANTE' in mo_upper and 'ALICANTE' in dname_upper: return dname
            if 'MURCIA' in mo_upper and 'MURCIA' in dname_upper: return dname
            if 'ALICANTE' not in dname_upper and 'MURCIA' not in dname_upper: return dname
            continue
        if 'CEMENTERIO' in mo_upper and 'CEMENTERIO' in dname_upper: return dname
        if 'PEREAMAR' in mo_upper and 'PEREAMAR' in dname_upper: return dname
        if ('ANGEL' in mo_upper or 'NGEL' in mo_upper) and 'HELENA' in dname_upper and 'CARMEN' in mo_upper: return dname
        if 'MURO VECINO' in mo_upper and 'MURO VECINO' in dname_upper: return dname
        if 'OBRA CAMPO' in mo_upper and 'CAMPO' in dname_upper and 'ARANTXA' in dname_upper: return dname
        if 'HELENA' in mo_upper and 'HELENA' in dname_upper: return dname
        if 'ALBERTO' in mo_upper and 'EVA' in mo_upper and 'ALBERTO' in dname_upper: return dname
        if 'CAPUCHINOS' in mo_upper and 'CAPUCHINOS' in dname_upper: return dname
        if 'HUERTO' in mo_upper and 'HUERTO' in dname_upper: return dname
    return None

mo_to_project = {}
for mo in mano_obra_all:
    matched_name = match_mo_to_project(mo['proyecto'].upper(), all_display_names)
    mo_to_project[id(mo)] = matched_name

for mo in mano_obra_all:
    if mo_to_project.get(id(mo), None) is None:
        mo_name = mo['proyecto']
        if mo_name not in _all_pn_set:
            all_project_names.append(mo_name)
            _all_pn_set.add(mo_name)
            all_display_names.append(mo_name)
            _adn_set.add(mo_name)
            mo_to_project[id(mo)] = mo_name

# ===== 5. CONSOLIDAR =====
def mo_cost(m):
    if m['tarifa'] > 0:
        return m['horas'] * m['tarifa']
    return m['coste']

def build_proyectos(certs_for_month, dir_for_month, mo_for_month, gg_yr, veh_yr, cert_names_for_month, month_num=None):
    """Build project data for a specific month or all months."""
    _proyectos = []
    for pname in all_project_names:
        cert_data = certs_for_month.get(pname, None)
        ci = cert_data['importe'] if cert_data else 0.0
        _pct = ci / sum(c['importe'] for c in certs_for_month.values()) if certs_for_month and ci > 0 and cert_data else 0
        
        dt = 0.0; dc = 0
        if cert_data:
            for csv_proj in cert_to_csvs.get(pname, []):
                dt += dir_for_month.get(csv_proj, {}).get('total', 0)
                dc += dir_for_month.get(csv_proj, {}).get('count', 0)
        elif pname in dir_for_month:
            dt = dir_for_month[pname]['total']
            dc = dir_for_month[pname]['count']
        
        _pr = _pct * (gg_yr + veh_yr)
        _mh = 0; _mc = 0.0
        for _mo in mo_for_month:
            if mo_to_project.get(id(_mo), None) == pname:
                # Use monthly hours if month specified, else total
                if month_num and month_num in _mo.get('meses', {}):
                    _h = _mo['meses'][month_num]
                    _mh += _h
                    _mc += _h * _mo['tarifa'] if _mo['tarifa'] > 0 else 0
                else:
                    _mh += _mo['horas']; _mc += mo_cost(_mo)
        _tc = dt + _pr + _mc; _mg = ci - _tc; _mp = (_mg / ci * 100) if ci > 0 else 0
        _proyectos.append({
            'nombre': pname, 'certificacion': round(ci, 2), 'pct': round(_pct, 6),
            'gastos_directos': round(dt, 2), 'direct_count': dc,
            'prorrateo': round(_pr, 2), 'mano_obra_horas': _mh,
            'mano_obra_coste': round(_mc, 2), 'total_coste': round(_tc, 2),
            'margen': round(_mg, 2), 'margen_pct': round(_mp, 1),
            'has_cert': cert_data is not None and ci > 0,
        })
    _proyectos.sort(key=lambda x: (0 if x['has_cert'] else 1, -x['certificacion'] if x['has_cert'] else -x['gastos_directos']))
    return _proyectos

# Build ALL months data
proyectos_all = build_proyectos(cert_lookup, directos_por_proyecto, mano_obra_all, gg_total, veh_total, cert_lookup)

sum_cert = sum(p['certificacion'] for p in proyectos_all)
sum_directos = sum(p['gastos_directos'] for p in proyectos_all)
sum_prorrateo = sum(p['prorrateo'] for p in proyectos_all)
sum_mo = sum(p['mano_obra_coste'] for p in proyectos_all)
sum_horas = sum(p['mano_obra_horas'] for p in proyectos_all)
sum_coste = sum(p['total_coste'] for p in proyectos_all)
sum_margen = sum(p['margen'] for p in proyectos_all)

# Build per-month summary
monthly_data = {}
for mi in range(1, 13):
    # Cert for this month
    certs_m = {}
    for pname in all_project_names:
        cl = cert_lookup.get(pname, None)
        if cl and mi in cl.get('meses', {}):
            certs_m[pname] = {'nombre': pname, 'importe': cl['meses'][mi], 'meses': {mi: cl['meses'][mi]}}
    
    # Directos for this month
    dir_m = {}
    for pname, d in dir_by_month[mi].items():
        dir_m[pname] = d
    
    # MO for this month - filter from mano_obra_all using meses field
    mo_m = [mo for mo in mano_obra_all if mi in mo.get('meses', {})]
    
    # GG/VEH for this month
    gg_m = gg_by_month.get(mi, 0)
    veh_m = veh_by_month.get(mi, 0)
    
    proyectos_m = build_proyectos(certs_m, dir_m, mo_m, gg_m, veh_m, certs_m, month_num=mi)
    
    sc = sum(p['certificacion'] for p in proyectos_m)
    sd = sum(p['gastos_directos'] for p in proyectos_m)
    sp = sum(p['prorrateo'] for p in proyectos_m)
    sm = sum(p['mano_obra_coste'] for p in proyectos_m)
    sh = sum(p['mano_obra_horas'] for p in proyectos_m)
    stc = sum(p['total_coste'] for p in proyectos_m)
    sml = sum(p['margen'] for p in proyectos_m)
    
    monthly_data[mi] = {
        'nombre': MONTH_ES[mi],
        'cert': round(sc, 2), 'directos': round(sd, 2),
        'prorrateo': round(sp, 2), 'mo': round(sm, 2),
        'horas': sh, 'coste': round(stc, 2), 'margen': round(sml, 2),
        'gg': round(gg_m, 2), 'veh': round(veh_m, 2),
        'nfacturas': sum(d['count'] for d in dir_m.values()),
        'proyectos': proyectos_m,
    }

# GG/VEH categories
from collections import Counter
gg_cat_map = {'Combustible': 0, 'Alquiler': 0, 'Parking': 0, 'Ropa Laboral': 0,
    'Asesoria': 0, 'Telecomunicaciones': 0, 'Preencion': 0, 'Material': 0,
    'Lavado': 0, 'Seguros': 0, 'Otros': 0}
with open(csv_path, 'r', encoding='latin-1') as f:
    content = f.read()
reader = csv.DictReader(io.StringIO(content), delimiter=';')
for row in reader:
    proyecto = ''; importe_str = '0'; titulo = ''
    for key, val in row.items():
        if key is None: continue
        kl = key.lower(); val = val.strip() if val else ''
        if 'proyecto' == kl: proyecto = val.upper()
        elif 'importe' == kl: importe_str = val
        elif 't' in kl and 'tulo' in kl: titulo = val.upper()
    if 'GASTOS GENERALES' not in proyecto: continue
    importe = parse_euro_amount(importe_str)
    if any(w in titulo for w in ['REPOSTAJE', 'PLENOIL', 'GASO', 'COMBUSTIBLE', 'DIESEL', 'GASOLINA']): gg_cat_map['Combustible'] += importe
    elif 'ALQUILER' in titulo: gg_cat_map['Alquiler'] += importe
    elif 'PARKING' in titulo: gg_cat_map['Parking'] += importe
    elif any(w in titulo for w in ['ROPA', 'CALZADO', 'BOTAS']): gg_cat_map['Ropa Laboral'] += importe
    elif any(w in titulo for w in ['ASESOR', 'CONTAB', 'FISCAL']): gg_cat_map['Asesoria'] += importe
    elif any(w in titulo for w in ['TEL', 'DIGI', 'ORANGE', 'MOVISTAR', 'TELEFON']): gg_cat_map['Telecomunicaciones'] += importe
    elif any(w in titulo for w in ['RECONOCIMIENTO', 'MEDICO', 'PREVENCION', 'MEDICINA']): gg_cat_map['Preencion'] += importe
    elif any(w in titulo for w in ['MATERIAL', 'HERRAM', 'COMPR', 'BROCA', 'CORTAD', 'DISCO', 'MALLA', 'PINTURA', 'TORNILL', 'LLAVE']): gg_cat_map['Material'] += importe
    elif 'LAVADO' in titulo: gg_cat_map['Lavado'] += importe
    elif any(w in titulo for w in ['SEGURO', 'SEGUROMERC']): gg_cat_map['Seguros'] += importe
    else: gg_cat_map['Otros'] += importe

veh_cat_map = Counter()
with open(csv_path, 'r', encoding='latin-1') as f:
    content = f.read()
reader = csv.DictReader(io.StringIO(content), delimiter=';')
for row in reader:
    proyecto = ''; importe_str = '0'; titulo = ''
    for key, val in row.items():
        if key is None: continue
        kl = key.lower(); val = val.strip() if val else ''
        if 'proyecto' == kl: proyecto = val.upper()
        elif 'importe' == kl: importe_str = val
        elif 't' in kl and 'tulo' in kl: titulo = val.upper()
    if 'VEHICULOS' not in proyecto and 'VEH\u00cdCULOS' not in proyecto: continue
    importe = parse_euro_amount(importe_str)
    if any(w in titulo for w in ['REPOSTAJE', 'GASO', 'COMBUSTIBLE', 'DIESEL']): veh_cat_map['Combustible'] += importe
    elif 'ITV' in titulo: veh_cat_map['ITV'] += importe
    elif 'ASEGUR' in titulo: veh_cat_map['Seguro'] += importe
    elif any(w in titulo for w in ['REPARA', 'MANTEN']): veh_cat_map['Reparacion'] += importe
    elif 'LAVADO' in titulo: veh_cat_map['Lavado'] += importe
    elif 'NEUMATICOS' in titulo or 'NEUM' in titulo: veh_cat_map['Neumaticos'] += importe
    else: veh_cat_map['Otros'] += importe

supplier_totals = collections.defaultdict(float)
for f in all_facturas_dir:
    prov = f['proveedor'].strip() if f['proveedor'] else '(Sin proveedor)'
    supplier_totals[prov] += f['importe']
top10_suppliers = sorted(supplier_totals.items(), key=lambda x: -abs(x[1]))[:10]

top10_proj = sorted(directos_por_proyecto.items(), key=lambda x: -abs(x[1]['total']))[:10]

# Logo base64
import base64 as _b64
import io as _io
from PIL import Image as _Img
_logo_orig = _Img.open(r'C:\NAS\03PUBLI\LOGO\LOGO 1\For Web\png\symbol.png')
_logo_rot = _logo_orig.rotate(180)
_logo_buf = _io.BytesIO()
_logo_rot.save(_logo_buf, format='PNG')
_logo_b64 = 'data:image/png;base64,' + _b64.b64encode(_logo_buf.getvalue()).decode()

output = {
    'proyectos_data': proyectos_all,
    'sum_cert': round(sum_cert, 2),
    'sum_directos': round(sum_directos, 2),
    'sum_prorrateo': round(sum_prorrateo, 2),
    'sum_mo': round(sum_mo, 2),
    'sum_horas': sum_horas,
    'sum_coste': round(sum_coste, 2),
    'sum_margen': round(sum_margen, 2),
    'total_gastos_comunes': round(total_gastos_comunes, 2),
    'gg_total': round(gg_total, 2),
    'veh_total': round(veh_total, 2),
    'gg_count': gg_count,
    'veh_count': veh_count,
    'total_facturas_dir': total_facturas_dir,
    'all_facturas_dir': all_facturas_dir,
    'gg_cat_map': {k: round(v, 2) for k, v in gg_cat_map.items() if v > 0},
    'veh_cat_map': {k: round(v, 2) for k, v in veh_cat_map.items()},
    'top10_suppliers': [{'name': s[0], 'total': round(abs(s[1]), 2)} for s in top10_suppliers],
    'top10_proj': [{'name': p[0], 'total': round(abs(p[1]['total']), 2)} for p in top10_proj],
    'mano_obra_all': mano_obra_all,
    'available_years': ['2026'],
    'monthly_data': monthly_data,
    'logo_b64': _logo_b64,
}

with open(BASE + r'\datos_ecostruct.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, default=str)

print("datos_ecostruct.json generado correctamente")
print("  Certificaciones: {:,.2f} EUR".format(sum_cert))
print("  Gastos Directos: {:,.2f} EUR".format(sum_directos))
print("  Gastos Comunes:  {:,.2f} EUR".format(total_gastos_comunes))
print("  Mano de Obra:    {:,.2f} EUR ({} horas)".format(sum_mo, sum_horas))
print("  MARGEN:          {:,.2f} EUR".format(sum_margen))
print("  Meses disponibles: {}".format(list(monthly_data.keys())))
