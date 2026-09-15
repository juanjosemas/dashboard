// Month + Multi-Project filter system for ECO STRUCT Dashboard
// Shared between V1 and V2

var currentMonth = 'todos';
var selectedProjects = []; // empty = all projects
var projectList = []; // populated on load

function fmtE(v) {
    if (typeof Intl !== 'undefined') {
        return new Intl.NumberFormat('es-ES', {minimumFractionDigits: 2, maximumFractionDigits: 2}).format(v) + ' EUR';
    }
    var neg = v < 0;
    var abs = Math.abs(v);
    var intPart = Math.floor(abs);
    var decPart = Math.round((abs - intPart) * 100);
    var decStr = decPart < 10 ? '0' + decPart : String(decPart);
    var s = String(intPart);
    var result = '';
    var count = 0;
    for (var i = s.length - 1; i >= 0; i--) {
        count++;
        result = s[i] + result;
        if (count % 3 === 0 && i !== 0) result = '.' + result;
    }
    return (neg ? '-' : '') + result + ',' + decStr;
}

function fmtN(v) {
    if (typeof Intl !== 'undefined') {
        return new Intl.NumberFormat('es-ES').format(v);
    }
    var s = String(v);
    var result = '';
    var count = 0;
    for (var i = s.length - 1; i >= 0; i--) {
        count++;
        result = s[i] + result;
        if (count % 3 === 0 && i !== 0) result = '.' + result;
    }
    return result;
}

function shortName(nombre) {
    // Remove the ID prefix: "24016 - PLAZA CIRCULAR" -> "PLAZA CIRCULAR"
    var parts = nombre.split(' - ');
    if (parts.length > 1) return parts.slice(1).join(' - ');
    return nombre;
}

function getFilteredData(data) {
    if (!data || !data.proyectos) return data;
    if (selectedProjects.length === 0) return data; // all selected
    
    var filtered = [];
    var totalCert = 0, totalDir = 0, totalPrr = 0, totalMo = 0, totalHoras = 0;
    var totalFact = 0;
    for (var i = 0; i < data.proyectos.length; i++) {
        var p = data.proyectos[i];
        if (selectedProjects.indexOf(p.nombre) >= 0) {
            filtered.push(p);
            totalCert += p.certificacion;
            totalDir += p.gastos_directos;
            totalPrr += p.prorrateo;
            totalMo += p.mano_obra_coste;
            totalHoras += p.mano_obra_horas;
            totalFact += (p.direct_count || 0);
        }
    }
    var totalCoste = totalDir + totalPrr + totalMo;
    var totalMargen = totalCert - totalCoste;
    
    return {
        cert: totalCert,
        directos: totalDir,
        prorrateo: totalPrr,
        mo: totalMo,
        horas: totalHoras,
        coste: totalCoste,
        margen: totalMargen,
        gg: data.gg || 0,
        veh: data.veh || 0,
        gg_count: data.gg_count || 0,
        veh_count: data.veh_count || 0,
        nfacturas: totalFact,
        proyectos: filtered,
        _isProject: true
    };
}

function getProjectData(data, projectName) {
    if (!projectName || !data.proyectos) return data;
    var p = null;
    for (var i = 0; i < data.proyectos.length; i++) {
        if (data.proyectos[i].nombre === projectName) {
            p = data.proyectos[i];
            break;
        }
    }
    if (!p) return null;
    return {
        cert: p.certificacion,
        directos: p.gastos_directos,
        prorrateo: p.prorrateo,
        mo: p.mano_obra_coste,
        horas: p.mano_obra_horas,
        coste: p.total_coste,
        margen: p.margen,
        gg: p.prorrateo || 0,
        veh: 0,
        gg_count: 0,
        veh_count: 0,
        nfacturas: p.direct_count || 0,
        proyectos: [p],
        _isProject: true
    };
}

function updateFilterIndicator() {
    var el = document.getElementById('filterIndicator');
    if (!el) return;
    var monthNames = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                      'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
    var parts = [];
    if (currentMonth !== 'todos') parts.push(monthNames[parseInt(currentMonth)]);
    if (selectedProjects.length > 0) {
        parts.push(selectedProjects.length + ' obra(s) seleccionada(s)');
    }
    
    if (parts.length === 0) {
        el.textContent = 'Todos los datos';
        el.style.background = 'rgba(52,152,219,0.1)';
        el.style.color = '#3498db';
    } else {
        el.textContent = 'Filtrando: ' + parts.join(' | ');
        el.style.background = 'rgba(231,76,60,0.1)';
        el.style.color = '#e74c3c';
    }
}

function doFilter() {
    var data;
    if (currentMonth === 'todos') {
        data = monthlyDataAll;
    } else {
        data = monthlyData[String(currentMonth)];
    }
    if (!data) return;
    
    // Filter by selected projects (multi-select)
    if (selectedProjects.length > 0) {
        data = getFilteredData(data);
    }
    
    updateFilterIndicator();
    
    // V1: .kpi-card with .value and .sub
    var kpis = document.querySelectorAll('.kpi-card');
    if (kpis.length >= 5) {
        kpis[0].querySelector('.value').textContent = fmtE(data.cert);
        var certCount = data.proyectos ? data.proyectos.filter(function(p) { return p.has_cert; }).length : 0;
        kpis[0].querySelector('.sub').textContent = certCount + ' proyectos';
        kpis[1].querySelector('.value').textContent = fmtE(data.directos);
        kpis[1].querySelector('.sub').textContent = (data.nfacturas || 0) + ' facturas por obra';
        var gcTotal = (data.gg || 0) + (data.veh || 0);
        kpis[2].querySelector('.value').textContent = fmtE(gcTotal);
        if (selectedProjects.length > 0) {
            kpis[2].querySelector('.sub').textContent = 'Prorrateo adjudicado';
        } else {
            kpis[2].querySelector('.sub').textContent = 'GG ' + fmtN(Math.round(data.gg || 0)) + ' + VEH ' + fmtN(Math.round(data.veh || 0));
        }
        kpis[3].querySelector('.value').textContent = fmtE(data.mo);
        kpis[3].querySelector('.sub').textContent = fmtN(data.horas) + ' horas';
        var margenPct = data.cert > 0 ? (data.margen / data.cert * 100).toFixed(1) : '0.0';
        kpis[4].querySelector('.value').textContent = fmtE(data.margen);
        kpis[4].querySelector('.value').style.color = data.margen >= 0 ? '#27ae60' : '#e74c3c';
        kpis[4].querySelector('.sub').textContent = margenPct + '% sobre certificacion';
    }
    
    // V2: .kpi with .kpi-value and .kpi-sub
    var kpis2 = document.querySelectorAll('.kpi');
    if (kpis2.length >= 5) {
        kpis2[0].querySelector('.kpi-value').textContent = fmtE(data.cert);
        var certCount2 = data.proyectos ? data.proyectos.filter(function(p) { return p.has_cert; }).length : 0;
        var sub0 = kpis2[0].querySelectorAll('.kpi-sub');
        if (sub0.length > 0) sub0[0].textContent = certCount2 + ' proyectos certificados';
        kpis2[1].querySelector('.kpi-value').textContent = fmtE(data.directos);
        var sub1 = kpis2[1].querySelectorAll('.kpi-sub');
        if (sub1.length > 0) sub1[0].textContent = (data.nfacturas || 0) + ' facturas por obra';
        var gcTotal2 = (data.gg || 0) + (data.veh || 0);
        kpis2[2].querySelector('.kpi-value').textContent = fmtE(gcTotal2);
        var sub2 = kpis2[2].querySelectorAll('.kpi-sub');
        if (sub2.length > 0) {
            if (selectedProjects.length > 0) {
                sub2[0].textContent = 'Prorrateo adjudicado';
            } else {
                sub2[0].textContent = 'GG ' + fmtN(Math.round(data.gg || 0)) + ' + VEH ' + fmtN(Math.round(data.veh || 0));
            }
        }
        kpis2[3].querySelector('.kpi-value').textContent = fmtE(data.mo);
        var sub3 = kpis2[3].querySelectorAll('.kpi-sub');
        if (sub3.length > 0) sub3[0].textContent = fmtN(data.horas) + ' horas';
        var margenPct2 = data.cert > 0 ? (data.margen / data.cert * 100).toFixed(1) : '0.0';
        kpis2[4].querySelector('.kpi-value').textContent = fmtE(data.margen);
        var mc = data.margen >= 0 ? 'var(--success)' : 'var(--red)';
        kpis2[4].querySelector('.kpi-value').style.color = mc;
        var subEls = kpis2[4].querySelectorAll('.kpi-sub');
        if (subEls.length > 0) subEls[0].textContent = margenPct2 + '% sobre certificacion';
    }
}

function switchMonth(month, btn) {
    currentMonth = month;
    document.querySelectorAll('.month-btn').forEach(function(b) { b.classList.remove('active'); });
    if (btn) btn.classList.add('active');
    doFilter();
}

function switchMonthV2(month, btn) {
    currentMonth = month;
    document.querySelectorAll('.month-btn').forEach(function(b) { b.classList.remove('active'); });
    if (btn) btn.classList.add('active');
    doFilter();
}

// ===== MULTI-SELECT PROJECT DROPDOWN =====

function initMultiSelect() {
    var container = document.getElementById('multiSelectContainer');
    if (!container || !monthlyDataAll || !monthlyDataAll.proyectos) return;
    
    // Build project list from data
    projectList = monthlyDataAll.proyectos.map(function(p) { return p.nombre; });
    projectList.sort();
    
    // Detect dark theme (V2) - check CSS variable or dark background
    var bodyBg = getComputedStyle(document.body).backgroundColor;
    var isDark = document.body.classList.contains('dark-theme') || document.body.getAttribute('data-theme') === 'dark' || bodyBg === 'rgb(15, 25, 35)' || bodyBg === 'rgb(15, 23, 42)' || (bodyBg.match(/rgb/) && parseInt(bodyBg.split(',')[1]) < 50);
    var bg = isDark ? '#1e293b' : 'white';
    var bg2 = isDark ? '#0f172a' : '#fafafa';
    var border = isDark ? '#334155' : '#ddd';
    var text = isDark ? '#e2e8f0' : '#333';
    var text2 = isDark ? '#94a3b8' : '#666';
    var hoverBg = isDark ? '#334155' : '#f5f5f5';
    var accent = '#D4742C';
    
    // Build the multi-select HTML
    var html = '';
    html += '<div class="ms-wrapper" style="position:relative;display:inline-block;">';
    html += '<div class="ms-trigger" id="msTrigger" onclick="toggleMultiSelect()" style="cursor:pointer;padding:6px 14px;border:1px solid ' + border + ';border-radius:6px;background:' + bg + ';font-size:0.8rem;color:' + text + ';display:flex;align-items:center;gap:8px;min-width:320px;justify-content:space-between;transition:all .2s;">';
    html += '<span id="msLabel">Todas las obras (' + projectList.length + ')</span>';
    html += '<svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M3 5L6 8L9 5" stroke="' + text2 + '" stroke-width="1.5" stroke-linecap="round"/></svg>';
    html += '</div>';
    html += '<div class="ms-panel" id="msPanel" style="display:none;position:absolute;top:100%;left:0;min-width:400px;background:' + bg + ';border:1px solid ' + border + ';border-radius:6px;box-shadow:0 4px 12px rgba(0,0,0,0.25);z-index:1000;max-height:320px;overflow:hidden;">';
    
    // Search box
    html += '<div style="padding:8px;border-bottom:1px solid ' + border + ';">';
    html += '<input type="text" id="msSearch" placeholder="Buscar obra..." oninput="filterMsList()" style="width:100%;padding:6px 10px;border:1px solid ' + border + ';border-radius:4px;font-size:0.82rem;background:' + bg2 + ';color:' + text + ';outline:none;">';
    html += '</div>';
    
    // Select all / deselect all
    html += '<div style="padding:6px 10px;border-bottom:1px solid ' + border + ';display:flex;gap:12px;">';
    html += '<a href="#" onclick="msSelectAll();return false;" style="font-size:0.78rem;color:#3498db;text-decoration:none;font-weight:600;">Todas</a>';
    html += '<a href="#" onclick="msDeselectAll();return false;" style="font-size:0.78rem;color:#e74c3c;text-decoration:none;font-weight:600;">Ninguna</a>';
    html += '</div>';
    
    // Checkboxes
    html += '<div id="msList" style="max-height:240px;overflow-y:auto;padding:4px 0;">';
    for (var i = 0; i < projectList.length; i++) {
        var pn = projectList[i];
        var sn = shortName(pn);
        html += '<label class="ms-item" data-name="' + pn.replace(/"/g, '&quot;') + '" style="display:flex;align-items:center;gap:8px;padding:7px 12px;cursor:pointer;font-size:0.82rem;color:' + text + ';transition:background .15s;" onmouseover="this.style.background=\'' + hoverBg + '\'" onmouseout="this.style.background=\'transparent\'">';
        html += '<input type="checkbox" class="ms-cb" value="' + pn.replace(/"/g, '&quot;') + '" onchange="msChanged()" style="accent-color:#D4742C;width:15px;height:15px;">';
        html += '<span>' + sn + '</span>';
        html += '</label>';
    }
    html += '</div>';
    html += '</div>';
    html += '</div>';
    
    container.innerHTML = html;
    
    // Close on outside click
    document.addEventListener('click', function(e) {
        var panel = document.getElementById('msPanel');
        var trigger = document.getElementById('msTrigger');
        if (!panel || !trigger) return;
        if (!trigger.contains(e.target) && !panel.contains(e.target)) {
            panel.style.display = 'none';
        }
    });
}

function toggleMultiSelect() {
    var panel = document.getElementById('msPanel');
    if (!panel) return;
    var isOpen = panel.style.display !== 'none';
    panel.style.display = isOpen ? 'none' : 'block';
    if (!isOpen) {
        var search = document.getElementById('msSearch');
        if (search) { search.value = ''; search.focus(); filterMsList(); }
    }
}

function filterMsList() {
    var search = document.getElementById('msSearch');
    var list = document.getElementById('msList');
    if (!search || !list) return;
    var q = search.value.toLowerCase();
    var items = list.querySelectorAll('.ms-item');
    items.forEach(function(item) {
        var name = item.getAttribute('data-name').toLowerCase();
        item.style.display = name.indexOf(q) >= 0 ? 'flex' : 'none';
    });
}

function msSelectAll() {
    selectedProjects = [];
    document.querySelectorAll('.ms-cb').forEach(function(cb) { cb.checked = false; });
    updateMsLabel();
    doFilter();
}

function msDeselectAll() {
    selectedProjects = [];
    document.querySelectorAll('.ms-cb').forEach(function(cb) { cb.checked = false; });
    updateMsLabel();
    doFilter();
}

function msChanged() {
    selectedProjects = [];
    document.querySelectorAll('.ms-cb:checked').forEach(function(cb) {
        selectedProjects.push(cb.value);
    });
    updateMsLabel();
    doFilter();
}

function updateMsLabel() {
    var label = document.getElementById('msLabel');
    if (!label) return;
    var bodyBg2 = getComputedStyle(document.body).backgroundColor;
    var isDark = document.body.classList.contains('dark-theme') || bodyBg2 === 'rgb(15, 25, 35)' || bodyBg2 === 'rgb(15, 23, 42)' || (bodyBg2.match(/rgb/) && parseInt(bodyBg2.split(',')[1]) < 50);
    var defaultColor = isDark ? '#e2e8f0' : '#333';
    if (selectedProjects.length === 0) {
        label.textContent = 'Todas las obras (' + projectList.length + ')';
        label.style.color = defaultColor;
    } else if (selectedProjects.length === 1) {
        label.textContent = shortName(selectedProjects[0]);
        label.style.color = '#D4742C';
    } else {
        label.textContent = selectedProjects.length + ' obras seleccionadas';
        label.style.color = '#D4742C';
    }
}

// Initialize on load
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(initMultiSelect, 100);
});
