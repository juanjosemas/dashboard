// Month + Project filter system for ECO STRUCT Dashboard
// Shared between V1 and V2

var currentMonth = 'todos';
var currentProject = '';

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
        gg: 0,
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
    if (currentProject) parts.push(currentProject.split(' - ').slice(1).join(' - '));
    
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
    
    // If project selected, filter to that project
    if (currentProject) {
        var pData = getProjectData(data, currentProject);
        if (pData) data = pData;
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
        kpis[2].querySelector('.value').textContent = fmtE((data.gg || 0) + (data.veh || 0));
        kpis[2].querySelector('.sub').textContent = 'GG ' + fmtN(Math.round(data.gg || 0)) + ' + VEH ' + fmtN(Math.round(data.veh || 0));
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
        kpis2[2].querySelector('.kpi-value').textContent = fmtE((data.gg || 0) + (data.veh || 0));
        var sub2 = kpis2[2].querySelectorAll('.kpi-sub');
        if (sub2.length > 0) sub2[0].textContent = 'GG ' + fmtN(Math.round(data.gg || 0)) + ' + VEH ' + fmtN(Math.round(data.veh || 0));
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

function switchProject(projName) {
    currentProject = projName;
    doFilter();
}
