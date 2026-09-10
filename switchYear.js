var currentYear='todos';var allCharts={};
function switchYear(year,btn){
  currentYear=year;
  document.querySelectorAll('.year-btn').forEach(function(b){b.classList.remove('active');});
  if(btn)btn.classList.add('active');
  var d=yearData;var y=year;
  var cert=d.sumCert[y]||0;var dir=d.sumDirectos[y]||0;var prr=d.sumProrrateo[y]||0;
  var mo=d.sumMO[y]||0;var hrs=d.sumHoras[y]||0;var cost=d.sumCoste[y]||0;
  var marg=d.sumMargen[y]||0;var gg=d.ggTotal[y]||0;var veh=d.vehTotal[y]||0;
  var gc=gg+veh;var nfact=d.totalFacturasDir[y]||0;
  var projects=d.proyectos[y]||[];
  function fmtE2(v){if(v<0)return '-'+fmtE2(-v);return Math.abs(v).toLocaleString('es-ES',{minimumFractionDigits:2,maximumFractionDigits:2});}
  var kpi=document.querySelectorAll('.kpi');
  if(kpi.length>=5){
    kpi[0].querySelector('.kpi-value').textContent=fmtE2(cert)+' EUR';
    kpi[0].querySelector('.kpi-sub').textContent=projects.filter(function(p){return p.has_cert;}).length+' proyectos';
    kpi[1].querySelector('.kpi-value').textContent=fmtE2(dir)+' EUR';
    kpi[1].querySelector('.kpi-sub').textContent=nfact+' facturas';
    kpi[2].querySelector('.kpi-value').textContent=fmtE2(gc)+' EUR';
    kpi[2].querySelector('.kpi-sub').textContent='GG '+fmtE2(gg)+' + VEH '+fmtE2(veh);
    kpi[3].querySelector('.kpi-value').textContent=fmtE2(mo)+' EUR';
    kpi[3].querySelector('.kpi-sub').textContent=hrs.toLocaleString()+' horas';
    kpi[4].querySelector('.kpi-value').textContent=fmtE2(marg)+' EUR';
    kpi[4].querySelector('.kpi-value').style.color=marg>=0?'#22c55e':'#ef4444';
  }
  Object.keys(allCharts).forEach(function(k){if(allCharts[k]){allCharts[k].destroy();allCharts[k]=null;}});
  ['chartGlobalDonut','chartCostStack','chartMargenBar','chartComp','chartProrrBar','chartProrrPie'].forEach(function(id){var c=Chart.getChart(id);if(c)c.destroy();});
  var certP=projects.filter(function(p){return p.has_cert;});
  var cl2=certP.map(function(p){return p.nombre.substring(0,25);});
  allCharts.gd=new Chart(document.getElementById('chartGlobalDonut'),{type:'doughnut',data:{labels:['Gastos Directos','Prorrateo','Mano de Obra'],datasets:[{data:[dir,prr,mo],backgroundColor:['#3b82f6','#f97316','#a855f7'],borderWidth:3,borderColor:'#0f1923'}]},options:{responsive:false,cutout:'60%',plugins:{legend:{position:'bottom',labels:{color:'#94a3b8',font:{size:12},padding:14}}}}});
  allCharts.cs=new Chart(document.getElementById('chartCostStack'),{type:'bar',data:{labels:cl2,datasets:[{label:'Facturas',data:certP.map(function(p){return p.gastos_directos;}),backgroundColor:'#3b82f6'},{label:'Prorrateo',data:certP.map(function(p){return p.prorrateo;}),backgroundColor:'#f97316'},{label:'Mano de Obra',data:certP.map(function(p){return p.mano_obra_coste;}),backgroundColor:'#a855f7'}]},options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,scales:{x:{stacked:true,ticks:{color:'#94a3b8'}},y:{stacked:true,ticks:{color:'#94a3b8'}}},plugins:{legend:{position:'top',labels:{color:'#94a3b8'}}}}});
  var mv2=certP.map(function(p){return p.margen;});var mcc=certP.map(function(p){return p.margen>=0?'#22c55e':'#ef4444';});
  allCharts.mb=new Chart(document.getElementById('chartMargenBar'),{type:'bar',data:{labels:cl2,datasets:[{label:'Margen',data:mv2,backgroundColor:mcc}]},options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{ticks:{color:'#94a3b8'}},y:{ticks:{color:'#94a3b8'}}},onClick:function(e,els){if(els.length>0){showResumenDetail(els[0].index);}}}});
  allCharts.cp=new Chart(document.getElementById('chartComp'),{type:'bar',data:{labels:cl2,datasets:[{label:'Certificacion',data:certP.map(function(p){return p.certificacion;}),backgroundColor:'#3b82f6'},{label:'Coste Total',data:certP.map(function(p){return p.total_coste;}),backgroundColor:'#f97316'}]},options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'top',labels:{color:'#94a3b8'}}},scales:{x:{ticks:{color:'#94a3b8'}},y:{ticks:{color:'#94a3b8'}}}}});
  allCharts.pb=new Chart(document.getElementById('chartProrrBar'),{type:'bar',data:{labels:cl2,datasets:[{label:'Prorrateo',data:certP.map(function(p){return p.prorrateo;}),backgroundColor:'#f97316'}]},options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{x:{ticks:{color:'#94a3b8'}},y:{ticks:{color:'#94a3b8'}}}}});
  allCharts.pp=new Chart(document.getElementById('chartProrrPie'),{type:'pie',data:{labels:cl2,datasets:[{data:certP.map(function(p){return p.prorrateo;}),backgroundColor:['#3b82f6','#f97316','#00d4aa','#a855f7','#06b6d4','#eab308','#ef4444','#64748b','#818cf8','#f472b6']}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'right',labels:{color:'#94a3b8',font:{size:10}}}}}});
  var mr='';
  projects.forEach(function(p,i){
    var cls=p.margen>=0?'pos':'neg';var bw=Math.min(Math.abs(p.margen_pct),100);
    var bc=p.margen>=0?'#22c55e':'#ef4444';
    var rs=p.has_cert?'':` style="background:rgba(249,115,22,0.05)"`;
    var cl=p.has_cert?fmtE2(p.certificacion):'<span style="color:var(--text2)">-</span>';
    var pl=p.has_cert?fmtE2(p.prorrateo):'<span style="color:var(--text2)">-</span>';
    var pc=p.has_cert?p.margen_pct.toFixed(1)+'%':'-';
    var ne=p.has_cert?'':` <span style="font-size:0.6rem;color:var(--text2)">(s/c)</span>`;
    var dn=p.nombre.length>28?p.nombre.substring(0,26)+'..':p.nombre;
    mr+=`<tr${rs}><td title="${p.nombre}"><strong>${dn}</strong>${ne}</td>`;
    mr+=`<td class="num">${cl}</td><td class="num">${fmtE2(p.gastos_directos)}</td>`;
    mr+=`<td class="num">${pl}</td><td class="num">${fmtE2(p.mano_obra_coste)}</td>`;
    mr+=`<td class="num"><strong>${fmtE2(p.total_coste)}</strong></td><td class="num">${pc}</td>`;
    mr+=`<td><span class="${cls}">${fmtE2(p.margen)} EUR</span>`;
    mr+=`<div class="progress-bar" style="margin-top:3px"><div class="progress-fill" style="width:${bw}%;background:${bc}"></div></div>`;
    mr+=`</td></tr>`;
  });
  mr+=`<tr class="total-row"><td>TOTAL (${projects.length})</td><td class="num">${fmtE2(cert)}</td><td class="num">${fmtE2(dir)}</td><td class="num">${fmtE2(prr)}</td><td class="num">${fmtE2(mo)}</td><td class="num"><strong>${fmtE2(cost)}</strong></td><td class="num"></td>`;
  if(cert>0){mr+=`<td><span class="pos">${fmtE2(marg)} EUR (${(marg/cert*100).toFixed(1)}%)</span></td></tr>`;}else{mr+=`<td><span class="neg">${fmtE2(marg)} EUR</span></td></tr>`;}
  var ptb=document.getElementById('projTable');if(ptb){var tb=ptb.querySelector('tbody');if(tb)tb.innerHTML=mr;}
  reattachRowClicks();
  var prr2='';projects.forEach(function(p){prr2+=`<tr><td>${p.nombre}</td><td class="num">${fmtE2(p.certificacion)}</td><td class="num">${(p.pct*100).toFixed(2)}%</td><td class="num">${fmtE2(p.prorrateo)}</td></tr>`;});
  prr2+=`<tr class="total-row"><td>TOTAL</td><td class="num">${fmtE2(cert)}</td><td class="num">100.00%</td><td class="num">${fmtE2(gc)}</td></tr>`;
  var prt=document.getElementById('prorrTable');if(prt){var ptb2=prt.querySelector('tbody');if(ptb2)ptb2.innerHTML=prr2;}
  projectData=projects.map(function(p){return{nombre:p.nombre,certificacion:p.certificacion,gastos_directos:p.gastos_directos,prorrateo:p.prorrateo,mano_obra:p.mano_obra_coste,total_coste:p.total_coste,margen:p.margen,margen_pct:p.margen_pct,has_cert:p.has_cert};});
}
function reattachRowClicks(){
  var rows=document.getElementById('projTable').querySelectorAll('tbody tr:not(.total-row)');
  rows.forEach(function(row,i){row.style.cursor='pointer';row.onclick=function(){showDetail(i);};row.onmouseenter=function(){row.style.background='rgba(0,212,170,0.08)';};row.onmouseleave=function(){row.style.background='';};});
}
