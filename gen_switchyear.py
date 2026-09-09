#!/usr/bin/env python3
"""Genera switchYear.js para dashboard_v2.html"""
import json, os

BASE = r'C:\Users\jjmax\Downloads\1'
with open(BASE + r'\datos_ecostruct.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

available_years = data['available_years']
C_SUCCESS = '#22c55e'
C_RED = '#ef4444'
C_ACCENT2 = '#3b82f6'
C_ORANGE = '#f97316'
C_PURPLE = '#a855f7'
C_BG = '#0f1923'
CHART_COLORS = ['#3b82f6', '#f97316', '#00d4aa', '#a855f7', '#06b6d4', '#eab308', '#ef4444', '#64748b', '#818cf8', '#f472b6']

lines = []
lines.append("var currentYear='todos';var allCharts={};")
lines.append("function switchYear(year,btn){")
lines.append("  currentYear=year;")
lines.append("  document.querySelectorAll('.year-btn').forEach(function(b){b.classList.remove('active');});")
lines.append("  if(btn)btn.classList.add('active');")
lines.append("  var d=yearData;var y=year;")
lines.append("  var cert=d.sumCert[y]||0;var dir=d.sumDirectos[y]||0;var prr=d.sumProrrateo[y]||0;")
lines.append("  var mo=d.sumMO[y]||0;var hrs=d.sumHoras[y]||0;var cost=d.sumCoste[y]||0;")
lines.append("  var marg=d.sumMargen[y]||0;var gg=d.ggTotal[y]||0;var veh=d.vehTotal[y]||0;")
lines.append("  var gc=gg+veh;var nfact=d.totalFacturasDir[y]||0;")
lines.append("  var projects=d.proyectos[y]||[];")
lines.append("  function fmtE2(v){if(v<0)return '-'+fmtE2(-v);return Math.abs(v).toLocaleString('es-ES',{minimumFractionDigits:2,maximumFractionDigits:2});}")

# Update KPIs
lines.append("  var kpi=document.querySelectorAll('.kpi');")
lines.append("  if(kpi.length>=5){")
lines.append("    kpi[0].querySelector('.kpi-value').textContent=fmtE2(cert)+' EUR';")
lines.append("    kpi[0].querySelector('.kpi-sub').textContent=projects.filter(function(p){return p.has_cert;}).length+' proyectos';")
lines.append("    kpi[1].querySelector('.kpi-value').textContent=fmtE2(dir)+' EUR';")
lines.append("    kpi[1].querySelector('.kpi-sub').textContent=nfact+' facturas';")
lines.append("    kpi[2].querySelector('.kpi-value').textContent=fmtE2(gc)+' EUR';")
lines.append("    kpi[2].querySelector('.kpi-sub').textContent='GG '+fmtE2(gg)+' + VEH '+fmtE2(veh);")
lines.append("    kpi[3].querySelector('.kpi-value').textContent=fmtE2(mo)+' EUR';")
lines.append("    kpi[3].querySelector('.kpi-sub').textContent=hrs.toLocaleString()+' horas';")
lines.append("    kpi[4].querySelector('.kpi-value').textContent=fmtE2(marg)+' EUR';")
lines.append("    kpi[4].querySelector('.kpi-value').style.color=marg>=0?'"+C_SUCCESS+"':'"+C_RED+"';")
lines.append("  }")

# Destroy old charts
lines.append("  Object.keys(allCharts).forEach(function(k){if(allCharts[k]){allCharts[k].destroy();allCharts[k]=null;}});")
lines.append("  ['chartGlobalDonut','chartCostStack','chartMargenBar','chartComp','chartProrrBar','chartProrrPie'].forEach(function(id){var c=Chart.getChart(id);if(c)c.destroy();});")

# Rebuild charts
lines.append("  var certP=projects.filter(function(p){return p.has_cert;});")
lines.append("  var cl2=certP.map(function(p){return p.nombre.substring(0,25);});")

# Donut
lines.append("  allCharts.gd=new Chart(document.getElementById('chartGlobalDonut'),{type:'doughnut',data:{labels:['Gastos Directos','Prorrateo','Mano de Obra'],datasets:[{data:[dir,prr,mo],backgroundColor:['%s','%s','%s'],borderWidth:3,borderColor:'%s'}]},options:{responsive:false,cutout:'60%%',plugins:{legend:{position:'bottom',labels:{color:'#94a3b8',font:{size:12},padding:14}}}}});" % (C_ACCENT2, C_ORANGE, C_PURPLE, C_BG))

# Stacked bar
lines.append("  allCharts.cs=new Chart(document.getElementById('chartCostStack'),{type:'bar',data:{labels:cl2,datasets:[{label:'Facturas',data:certP.map(function(p){return p.gastos_directos;}),backgroundColor:'%s'},{label:'Prorrateo',data:certP.map(function(p){return p.prorrateo;}),backgroundColor:'%s'},{label:'Mano de Obra',data:certP.map(function(p){return p.mano_obra_coste;}),backgroundColor:'%s'}]},options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,scales:{x:{stacked:true,ticks:{color:'#94a3b8'}},y:{stacked:true,ticks:{color:'#94a3b8'}}},plugins:{legend:{position:'top',labels:{color:'#94a3b8'}}}}});" % (C_ACCENT2, C_ORANGE, C_PURPLE))

# Margen bar
lines.append("  var mv2=certP.map(function(p){return p.margen;});var mcc=certP.map(function(p){return p.margen>=0?'%s':'%s';});" % (C_SUCCESS, C_RED))
lines.append("  allCharts.mb=new Chart(document.getElementById('chartMargenBar'),{type:'bar',data:{labels:cl2,datasets:[{label:'Margen',data:mv2,backgroundColor:mcc}]},options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{ticks:{color:'#94a3b8'}},y:{ticks:{color:'#94a3b8'}}},onClick:function(e,els){if(els.length>0){showDetail(els[0].index);}}}});")

# Comparison bar
lines.append("  allCharts.cp=new Chart(document.getElementById('chartComp'),{type:'bar',data:{labels:cl2,datasets:[{label:'Certificacion',data:certP.map(function(p){return p.certificacion;}),backgroundColor:'%s'},{label:'Coste Total',data:certP.map(function(p){return p.total_coste;}),backgroundColor:'%s'}]},options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'top',labels:{color:'#94a3b8'}}},scales:{x:{ticks:{color:'#94a3b8'}},y:{ticks:{color:'#94a3b8'}}}}});" % (C_ACCENT2, C_ORANGE))

# Prorrateo bar + pie
lines.append("  allCharts.pb=new Chart(document.getElementById('chartProrrBar'),{type:'bar',data:{labels:cl2,datasets:[{label:'Prorrateo',data:certP.map(function(p){return p.prorrateo;}),backgroundColor:'%s'}]},options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{ticks:{color:'#94a3b8'}},y:{ticks:{color:'#94a3b8'}}}}});" % C_ORANGE)
lines.append("  allCharts.pp=new Chart(document.getElementById('chartProrrPie'),{type:'pie',data:{labels:cl2,datasets:[{data:certP.map(function(p){return p.prorrateo;}),backgroundColor:['%s','%s','%s','%s','%s','%s','%s','%s','%s','%s']}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'right',labels:{color:'#94a3b8',font:{size:10}}}}}});" % tuple(CHART_COLORS[:10]))

# Build table HTML using template literals (no escaping needed)
lines.append("  var mr='';")
lines.append("  projects.forEach(function(p,i){")
lines.append("    var cls=p.margen>=0?'pos':'neg';var bw=Math.min(Math.abs(p.margen_pct),100);")
lines.append("    var bc=p.margen>=0?'%s':'%s';" % (C_SUCCESS, C_RED))
lines.append("    var rs=p.has_cert?'':` style=\"background:rgba(249,115,22,0.05)\"`;")
lines.append("    var cl=p.has_cert?fmtE2(p.certificacion):'<span style=\"color:var(--text2)\">-</span>';")
lines.append("    var pl=p.has_cert?fmtE2(p.prorrateo):'<span style=\"color:var(--text2)\">-</span>';")
lines.append("    var pc=p.has_cert?p.margen_pct.toFixed(1)+'%':'-';")
lines.append("    var ne=p.has_cert?'':` <span style=\"font-size:0.6rem;color:var(--text2)\">(s/c)</span>`;")
lines.append("    var dn=p.nombre.length>28?p.nombre.substring(0,26)+'..':p.nombre;")
lines.append("    mr+=`<tr${rs}><td title=\"${p.nombre}\"><strong>${dn}</strong>${ne}</td>`;")
lines.append("    mr+=`<td class=\"num\">${cl}</td><td class=\"num\">${fmtE2(p.gastos_directos)}</td>`;")
lines.append("    mr+=`<td class=\"num\">${pl}</td><td class=\"num\">${fmtE2(p.mano_obra_coste)}</td>`;")
lines.append("    mr+=`<td class=\"num\"><strong>${fmtE2(p.total_coste)}</strong></td><td class=\"num\">${pc}</td>`;")
lines.append("    mr+=`<td><span class=\"${cls}\">${fmtE2(p.margen)} EUR</span>`;")
lines.append("    mr+=`<div class=\"progress-bar\" style=\"margin-top:3px\"><div class=\"progress-fill\" style=\"width:${bw}%;background:${bc}\"></div></div>`;")
lines.append("    mr+=`</td></tr>`;")
lines.append("  });")

# Total row
lines.append("  mr+=`<tr class=\"total-row\"><td>TOTAL (${projects.length})</td><td class=\"num\">${fmtE2(cert)}</td><td class=\"num\">${fmtE2(dir)}</td><td class=\"num\">${fmtE2(prr)}</td><td class=\"num\">${fmtE2(mo)}</td><td class=\"num\"><strong>${fmtE2(cost)}</strong></td><td class=\"num\"></td>`;")
lines.append("  if(cert>0){mr+=`<td><span class=\"pos\">${fmtE2(marg)} EUR (${(marg/cert*100).toFixed(1)}%)</span></td></tr>`;}else{mr+=`<td><span class=\"neg\">${fmtE2(marg)} EUR</span></td></tr>`;}")

# Update tables
lines.append("  var ptb=document.getElementById('projTable');if(ptb){var tb=ptb.querySelector('tbody');if(tb)tb.innerHTML=mr;}")
lines.append("  reattachRowClicks();")

# Prorrateo table
lines.append("  var prr2='';projects.forEach(function(p){prr2+=`<tr><td>${p.nombre}</td><td class=\"num\">${fmtE2(p.certificacion)}</td><td class=\"num\">${(p.pct*100).toFixed(2)}%</td><td class=\"num\">${fmtE2(p.prorrateo)}</td></tr>`;});")
lines.append("  prr2+=`<tr class=\"total-row\"><td>TOTAL</td><td class=\"num\">${fmtE2(cert)}</td><td class=\"num\">100.00%</td><td class=\"num\">${fmtE2(gc)}</td></tr>`;")
lines.append("  var prt=document.getElementById('prorrTable');if(prt){var ptb2=prt.querySelector('tbody');if(ptb2)ptb2.innerHTML=prr2;}")
lines.append("  projectData=projects.map(function(p){return{nombre:p.nombre,certificacion:p.certificacion,gastos_directos:p.gastos_directos,prorrateo:p.prorrateo,mano_obra:p.mano_obra_coste,total_coste:p.total_coste,margen:p.margen,margen_pct:p.margen_pct,has_cert:p.has_cert};});")
lines.append("}")

# reattachRowClicks
lines.append("function reattachRowClicks(){")
lines.append("  var rows=document.getElementById('projTable').querySelectorAll('tbody tr:not(.total-row)');")
lines.append("  rows.forEach(function(row,i){row.style.cursor='pointer';row.onclick=function(){showDetail(i);};row.onmouseenter=function(){row.style.background='rgba(0,212,170,0.08)';};row.onmouseleave=function(){row.style.background='';};});")
lines.append("}")

js_content = '\n'.join(lines) + '\n'
with open(BASE + r'\switchYear.js', 'w', encoding='utf-8') as f:
    f.write(js_content)
print("switchYear.js generado correctamente (%d lineas)" % len(lines))
