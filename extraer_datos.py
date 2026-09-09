#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrae todos los datos de CSV y DOCX a datos_ecostruct.json
para que ambos dashboards (v1 y v2) usen los mismos datos.
"""
import csv
import io
import re
import collections
import json
from docx import Document

def parse_euro_amount(s):
    s = s.strip().replace('\u20ac', '').strip()
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

def mo_cost(m):
    if m['tarifa'] > 0:
        return m['horas'] * m['tarifa']
    return m['coste']

BASE = r'C:\Users\jjmax\Downloads\1'
DASH = BASE + r'\dashboard'

# ===== 1. CERTIFICACIONES =====
doc_cert = Document(DASH + r'\CERTIFICACIONES.docx')
certificaciones = []
certificaciones_by_year = {}
current_cert_year = ''

for p in doc_cert.paragraphs:
    text = p.text.strip()
    if not text:
        continue
    year_match = re.search(r'A[ÑN]O\s+(20\d{2})', text, re.IGNORECASE)
    if year_match:
        current_cert_year = year_match.group(1)
        continue
    matches = list(re.finditer(r'([\d.,]+)\s*\u20ac', text))
    if not matches:
        continue
    last_match = matches[-1]
    importe = parse_euro_amount(last_match.group(1))
    proyecto = text[:last_match.start()].strip()
    proyecto = re.sub(r'[\s\-]+$', '', proyecto).strip()
    proyecto = re.sub(r'\([\d.,\s\+\-]+\)\s*=\s*$', '', proyecto).strip()
    proyecto = re.sub(r'[\s\-]+$', '', proyecto).strip()
    if importe > 0 and proyecto:
        cert_entry = {'nombre': proyecto, 'importe': importe, 'year': current_cert_year}
        certificaciones.append(cert_entry)
        if current_cert_year not in certificaciones_by_year:
            certificaciones_by_year[current_cert_year] = []
        certificaciones_by_year[current_cert_year].append(cert_entry)

# ===== 2. MANO DE OBRA =====
doc_mo = Document(DASH + r'\GASTOS MANO DE OBRA.docx')
mano_obra_all = []
current_year = 2026

for p in doc_mo.paragraphs:
    text = p.text.strip()
    if not text:
        continue
    if '2025' in text:
        current_year = 2025
        continue
    if '2026' in text:
        current_year = 2026
        continue
    if text.startswith('GASTOS'):
        continue
    clean = re.sub(r'[^\x00-\x7f]+', ' ', text)
    clean = re.sub(r'\s+', ' ', clean).strip()
    horas_match = re.search(r'(\d+)\s*HORAS?\s*A\s*(\d+).*?TOTAL\s*([\d.,]+)', clean, re.IGNORECASE)
    if horas_match:
        horas_val = int(horas_match.group(1))
        tarifa_val = int(horas_match.group(2))
        coste_val = parse_euro_amount(horas_match.group(3))
        name_end = horas_match.start()
        proyecto = clean[:name_end].strip()
        proyecto = re.sub(r'[\s\-]+$', '', proyecto).strip()
        if proyecto:
            mano_obra_all.append({'proyecto': proyecto, 'horas': horas_val, 'tarifa': tarifa_val, 'coste': coste_val, 'year': current_year})
            continue
    match2 = re.search(r'(.+?)[\s\-]+TOTAL\s*([\d.,]+)', clean, re.IGNORECASE)
    if match2:
        proyecto = match2.group(1).strip()
        coste = parse_euro_amount(match2.group(2))
        mano_obra_all.append({'proyecto': proyecto, 'horas': 0, 'tarifa': 0, 'coste': coste, 'year': current_year})

# ===== 3. CSV GASTOS =====
csv_path = DASH + r'\ECO_STRUCT_-_Workspace_Gastos.csv'
with open(csv_path, 'r', encoding='latin-1') as f:
    content = f.read()

reader = csv.DictReader(io.StringIO(content), delimiter=';')
gg_total = 0.0; gg_count = 0; veh_total = 0.0; veh_count = 0
gg_total_year = collections.Counter(); veh_total_year = collections.Counter()
gg_count_year = collections.Counter(); veh_count_year = collections.Counter()
directos_por_proyecto = collections.defaultdict(lambda: {'total': 0.0, 'count': 0, 'facturas': []})

for row in reader:
    proyecto = ''; importe_str = '0'; titulo = ''; proveedor = ''; fecha = ''; codigo = ''; estado = ''
    for key, val in row.items():
        if key is None: continue
        key_lower = key.lower(); val = val.strip() if val else ''
        if 'proyecto' == key_lower: proyecto = val.upper()
        elif 'importe' == key_lower: importe_str = val
        elif 't' in key_lower and 'tulo' in key_lower: titulo = val
        elif 'proveedor' in key_lower and 'id' not in key_lower: proveedor = val
        elif key_lower == 'fecha': fecha = val
        elif 'digo' in key_lower or 'odigo' in key_lower: codigo = val
        elif 'estado' == key_lower: estado = val

    importe = parse_euro_amount(importe_str)
    _f_parts = fecha.split('/') if fecha else []
    _f_yr = _f_parts[2] if len(_f_parts) == 3 else ''

    if 'GASTOS GENERALES' in proyecto:
        gg_total += importe; gg_count += 1
        if _f_yr: gg_total_year[_f_yr] += importe; gg_count_year[_f_yr] += 1
    elif 'VEHICULOS' in proyecto or 'VEH\u00cdCULOS' in proyecto:
        veh_total += importe; veh_count += 1
        if _f_yr: veh_total_year[_f_yr] += importe; veh_count_year[_f_yr] += 1
    elif proyecto:
        directos_por_proyecto[proyecto]['total'] += importe
        directos_por_proyecto[proyecto]['count'] += 1
        directos_por_proyecto[proyecto]['facturas'].append({
            'codigo': codigo, 'fecha': fecha, 'titulo': titulo,
            'importe': importe, 'proveedor': proveedor, 'estado': estado
        })

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

directos_por_proyecto_year = {}
for _fi in all_facturas_dir:
    _yr = _fi.get('year', '')
    if not _yr: continue
    _proj = _fi.get('proyecto', '')
    _imp = _fi.get('importe', 0)
    if 'GASTOS GENERALES' not in _proj.upper() and 'VEHICULOS' not in _proj.upper() and 'VEH\u00cdCULOS' not in _proj.upper():
        if _yr not in directos_por_proyecto_year:
            directos_por_proyecto_year[_yr] = collections.defaultdict(lambda: {'total': 0.0, 'count': 0})
        directos_por_proyecto_year[_yr][_proj]['total'] += _imp
        directos_por_proyecto_year[_yr][_proj]['count'] += 1

mo_by_year = {}
for mo in mano_obra_all:
    _yr = str(mo['year'])
    if _yr not in mo_by_year: mo_by_year[_yr] = []
    mo_by_year[_yr].append(mo)

available_years = sorted(set(list(directos_por_proyecto_year.keys()) + list(mo_by_year.keys())))

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
    if name in cert_lookup: cert_lookup[name]['importe'] += c['importe']
    else: cert_lookup[name] = {'nombre': name, 'importe': c['importe']}

total_cert = sum(c['importe'] for c in cert_lookup.values())

all_display_names = []
_adn_set = set()
for p in certificaciones:
    if p['nombre'] not in _adn_set:
        all_display_names.append(p['nombre']); _adn_set.add(p['nombre'])
for csv_proj in directos_por_proyecto:
    if csv_proj not in csv_to_cert and csv_proj not in _adn_set:
        all_display_names.append(csv_proj); _adn_set.add(csv_proj)
has_alberto = any('ALBERTO' in m['proyecto'].upper() and 'EVA' in m['proyecto'].upper() for m in mano_obra_all)
if has_alberto:
    all_display_names.append('ALBERTO Y EVA')
    all_project_names.append('ALBERTO Y EVA')

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
        if 'ALBERTO' in mo_upper and 'EVA' in mo_upper and 'ALBERTO' in dname_upper: return dname
    return None

mo_to_project = {}
for mo in mano_obra_all:
    matched_name = match_mo_to_project(mo['proyecto'].upper(), all_display_names)
    mo_to_project[id(mo)] = matched_name

# ===== 5. CONSOLIDAR =====
proyectos_data = []
for pname in all_project_names:
    cert_data = cert_lookup.get(pname, None)
    cert_importe = cert_data['importe'] if cert_data else 0.0
    pct = cert_importe / total_cert if total_cert > 0 and cert_data else 0.0
    direct_total = 0.0; direct_count = 0
    if cert_data:
        for csv_proj in cert_to_csvs.get(pname, []):
            direct_total += directos_por_proyecto[csv_proj]['total']
            direct_count += directos_por_proyecto[csv_proj]['count']
    elif pname in directos_por_proyecto:
        direct_total = directos_por_proyecto[pname]['total']
        direct_count = directos_por_proyecto[pname]['count']
    prorrateo = pct * total_gastos_comunes
    mo_horas = 0; mo_coste = 0.0
    for mo in mano_obra_all:
        if mo_to_project.get(id(mo), None) == pname:
            mo_horas += mo['horas']; mo_coste += mo_cost(mo)
    total_coste = direct_total + prorrateo + mo_coste
    margen = cert_importe - total_coste
    margen_pct = (margen / cert_importe * 100) if cert_importe > 0 else 0
    proyectos_data.append({
        'nombre': pname, 'certificacion': cert_importe, 'pct': pct,
        'gastos_directos': direct_total, 'direct_count': direct_count,
        'prorrateo': prorrateo, 'mano_obra_horas': mo_horas,
        'mano_obra_coste': mo_coste, 'total_coste': total_coste,
        'margen': margen, 'margen_pct': margen_pct, 'has_cert': cert_data is not None,
    })

proyectos_data.sort(key=lambda x: (0 if x['has_cert'] else 1, -x['certificacion'] if x['has_cert'] else -x['gastos_directos']))

sum_cert = sum(p['certificacion'] for p in proyectos_data)
sum_directos = sum(p['gastos_directos'] for p in proyectos_data)
sum_prorrateo = sum(p['prorrateo'] for p in proyectos_data)
sum_mo = sum(p['mano_obra_coste'] for p in proyectos_data)
sum_horas = sum(p['mano_obra_horas'] for p in proyectos_data)
sum_coste = sum(p['total_coste'] for p in proyectos_data)
sum_margen = sum(p['margen'] for p in proyectos_data)

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

# Top suppliers
supplier_totals = collections.defaultdict(float)
for f in all_facturas_dir:
    prov = f['proveedor'].strip() if f['proveedor'] else '(Sin proveedor)'
    supplier_totals[prov] += f['importe']
top10_suppliers = sorted(supplier_totals.items(), key=lambda x: -abs(x[1]))[:10]

top10_proj = sorted(directos_por_proyecto.items(), key=lambda x: -abs(x[1]['total']))[:10]

# Per-year data
yp_data = {}
yp_data['todos'] = {
    'cert': round(sum_cert, 2), 'directos': round(sum_directos, 2),
    'prorrateo': round(sum_prorrateo, 2), 'mo': round(sum_mo, 2),
    'horas': sum_horas, 'coste': round(sum_coste, 2), 'margen': round(sum_margen, 2),
    'gg': round(gg_total, 2), 'veh': round(veh_total, 2),
    'gg_count': gg_count, 'veh_count': veh_count,
    'nfacturas': total_facturas_dir, 'proyectos': proyectos_data,
}

for _yr_key in available_years:
    _dir_yr = directos_por_proyecto_year.get(_yr_key, {})
    _gg_yr = gg_total_year.get(_yr_key, 0)
    _veh_yr = veh_total_year.get(_yr_key, 0)
    _mo_yr = mo_by_year.get(_yr_key, [])
    _mo_h = sum(m['horas'] for m in _mo_yr)
    _mo_c = sum(mo_cost(m) for m in _mo_yr)
    _certs_yr = {c['nombre']: c for c in certificaciones_by_year.get(_yr_key, [])}
    _sum_cert_yr = sum(c['importe'] for c in _certs_yr.values())
    _py = []
    for _pname in all_project_names:
        _cd = cert_lookup.get(_pname, None)
        _ci = _certs_yr.get(_pname, {}).get('importe', 0.0) if _cd else 0.0
        _pct = _ci / _sum_cert_yr if _sum_cert_yr > 0 and _cd else 0
        _dt = 0.0; _dc = 0
        if _cd:
            for _cp in cert_to_csvs.get(_pname, []):
                if _cp in _dir_yr: _dt += _dir_yr[_cp]['total']; _dc += _dir_yr[_cp]['count']
        elif _pname in _dir_yr: _dt = _dir_yr[_pname]['total']; _dc = _dir_yr[_pname]['count']
        _pr = _pct * (_gg_yr + _veh_yr)
        _mh = 0; _mc = 0.0
        for _mo in _mo_yr:
            if mo_to_project.get(id(_mo), None) == _pname: _mh += _mo['horas']; _mc += mo_cost(_mo)
        _tc = _dt + _pr + _mc; _mg = _ci - _tc; _mp = (_mg / _ci * 100) if _ci > 0 else 0
        _py.append({
            'nombre': _pname, 'certificacion': round(_ci, 2), 'pct': round(_pct, 6),
            'gastos_directos': round(_dt, 2), 'direct_count': _dc,
            'prorrateo': round(_pr, 2), 'mano_obra_horas': _mh,
            'mano_obra_coste': round(_mc, 2), 'total_coste': round(_tc, 2),
            'margen': round(_mg, 2), 'margen_pct': round(_mp, 1),
            'has_cert': _cd is not None,
        })
    _py.sort(key=lambda x: (0 if x['has_cert'] else 1, -x['certificacion'] if x['has_cert'] else -x['gastos_directos']))
    _cp_yr = [p for p in _py if p['has_cert']]
    yp_data[_yr_key] = {
        'cert': round(sum(p['certificacion'] for p in _py), 2),
        'directos': round(sum(p['gastos_directos'] for p in _py), 2),
        'prorrateo': round(sum(p['prorrateo'] for p in _py), 2),
        'mo': round(sum(p['mano_obra_coste'] for p in _py), 2),
        'horas': sum(p['mano_obra_horas'] for p in _py),
        'coste': round(sum(p['total_coste'] for p in _py), 2),
        'margen': round(sum(p['margen'] for p in _py), 2),
        'gg': round(_gg_yr, 2), 'veh': round(_veh_yr, 2),
        'gg_count': gg_count_year.get(_yr_key, 0), 'veh_count': veh_count_year.get(_yr_key, 0),
        'nfacturas': sum(d['count'] for d in _dir_yr.values()),
        'proyectos': _py,
    }

# Logo base64
import base64 as _b64
import io as _io
from PIL import Image as _Img
_logo_orig = _Img.open(r'C:\NAS\03PUBLI\LOGO\LOGO 1\For Web\png\symbol.png')
_logo_rot = _logo_orig.rotate(180)
_logo_buf = _io.BytesIO()
_logo_rot.save(_logo_buf, format='PNG')
_logo_b64 = 'data:image/png;base64,' + _b64.b64encode(_logo_buf.getvalue()).decode()

# Save all data
output = {
    'proyectos_data': proyectos_data,
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
    'available_years': available_years,
    'yp_data': yp_data,
    'logo_b64': _logo_b64,
}

with open(BASE + r'\datos_ecostruct.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, default=str)

print("datos_ecostruct.json generado correctamente")
print("  Certificaciones: {:,.2f} EUR".format(sum_cert))
print("  Gastos Directos: {:,.2f} EUR".format(sum_directos))
print("  Gastos Comunes:  {:,.2f} EUR".format(total_gastos_comunes))
print("  Mano de Obra:    {:,.2f} EUR ({} horas)".format(sum_mo, sum_horas))
print("  MARGEN:          {:,.2f} EUR ({:.1f}%)".format(sum_margen, sum_margen/sum_cert*100 if sum_cert > 0 else 0))
