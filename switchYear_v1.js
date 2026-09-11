var currentYear='todos';
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
  function fmtE2(v){if(typeof v==='string')v=parseFloat(v);if(isNaN(v))return '0,00';if(v<0)return '-'+fmtE2(-v);return Math.abs(v).toLocaleString('es-ES',{minimumFractionDigits:2,maximumFractionDigits:2});}
  // Update KPI cards (.kpi-card with .value and .sub)
  var cards=document.querySelectorAll('.kpi-card');
  if(cards.length>=5){
    cards[0].querySelector('.value').textContent=fmtE2(cert)+' EUR';
    cards[0].querySelector('.sub').textContent=projects.filter(function(p){return p.has_cert;}).length+' proyectos';
    cards[1].querySelector('.value').textContent=fmtE2(dir)+' EUR';
    cards[1].querySelector('.sub').textContent=nfact+' facturas';
    cards[2].querySelector('.value').textContent=fmtE2(gc)+' EUR';
    cards[2].querySelector('.sub').textContent='GG '+fmtE2(gg)+' + VEH '+fmtE2(veh);
    cards[3].querySelector('.value').textContent=fmtE2(mo)+' EUR';
    cards[3].querySelector('.sub').textContent=hrs.toLocaleString('es-ES')+' horas';
    cards[4].querySelector('.value').textContent=fmtE2(marg)+' EUR';
    cards[4].querySelector('.value').style.color=marg>=0?'#2ecc71':'#e94560';
  }
  // Update mini stats - find the grid that has "Eficiencia" text
  var allBoxes=document.querySelectorAll('[style*="grid-template-columns"]');
  allBoxes.forEach(function(box){
    if(box.children.length>=5){
      var hasKpiCard=box.querySelector('.kpi-card');
      if(hasKpiCard) return; // skip KPI grid
      var certCount=projects.filter(function(p){return p.has_cert;}).length;
      var lossCount=projects.filter(function(p){return p.has_cert && p.margen<0;}).length;
      var values=[(cost>0&&cert>0?(cost/cert*100).toFixed(1)+'%':'0.0%'),certCount.toString(),lossCount.toString(),nfact.toLocaleString('es-ES'),hrs.toLocaleString('es-ES')+' h',projects.length.toString()];
      for(var i=0;i<Math.min(box.children.length,values.length);i++){
        var ch=box.children[i];
        var lastDiv=ch.querySelector('div:last-child');
        if(lastDiv && i<values.length) lastDiv.textContent=values[i];
      }
    }
  });
  // Update projects table
  var certP=projects.filter(function(p){return p.has_cert;});
  var mr='';
  projects.forEach(function(p,i){
    var cls=p.margen>=0?'pos':'neg';
    var bw=Math.min(Math.abs(p.margen_pct),100);
    var bc=p.margen>=0?'#2ecc71':'#e94560';
    var cl=p.has_cert?fmtE2(p.certificacion):'<span style="color:#999">-</span>';
    var pl=p.has_cert?fmtE2(p.prorrateo):'<span style="color:#999">-</span>';
    var pc=p.has_cert?p.margen_pct.toFixed(1)+'%':'-';
    var ne=p.has_cert?'':' <span style="font-size:0.65rem;color:#999">(s/c)</span>';
    var dn=p.nombre.length>30?p.nombre.substring(0,28)+'..':p.nombre;
    mr+='<tr><td title="'+p.nombre+'"><strong>'+dn+'</strong>'+ne+'</td>';
    mr+='<td class="num">'+cl+'</td><td class="num">'+fmtE2(p.gastos_directos)+'</td>';
    mr+='<td class="num">'+pl+'</td><td class="num">'+fmtE2(p.mano_obra_coste)+'</td>';
    mr+='<td class="num"><strong>'+fmtE2(p.total_coste)+'</strong></td><td class="num">'+pc+'</td>';
    mr+='<td><span class="'+cls+'">'+fmtE2(p.margen)+' EUR</span>';
    mr+='<div class="progress-bar" style="margin-top:3px"><div class="progress-fill" style="width:'+bw+'%;background:'+bc+'"></div></div>';
    mr+='</td></tr>';
  });
  var totalCert=certP.reduce(function(s,p){return s+p.certificacion;},0);
  var totalDir=certP.reduce(function(s,p){return s+p.gastos_directos;},0);
  var totalPrr=certP.reduce(function(s,p){return s+p.prorrateo;},0);
  var totalMO=certP.reduce(function(s,p){return s+p.mano_obra_coste;},0);
  var totalCost=certP.reduce(function(s,p){return s+p.total_coste;},0);
  var totalMarg=certP.reduce(function(s,p){return s+p.margen;},0);
  mr+='<tr class="total-row"><td>TOTAL ('+certP.length+')</td>';
  mr+='<td class="num">'+fmtE2(totalCert)+'</td><td class="num">'+fmtE2(totalDir)+'</td>';
  mr+='<td class="num">'+fmtE2(totalPrr)+'</td><td class="num">'+fmtE2(totalMO)+'</td>';
  mr+='<td class="num"><strong>'+fmtE2(totalCost)+'</strong></td><td class="num"></td>';
  if(totalCert>0){mr+='<td><span class="pos">'+fmtE2(totalMarg)+' EUR ('+(totalMarg/totalCert*100).toFixed(1)+'%)</span></td>';}
  else{mr+='<td><span class="neg">'+fmtE2(totalMarg)+' EUR</span></td>';}
  mr+='</tr>';
  var ptb=document.querySelector('#margenTable tbody');if(ptb)ptb.innerHTML=mr;
  // Update prorrateo table
  var prr2='';
  projects.forEach(function(p){
    prr2+='<tr><td>'+p.nombre+'</td><td class="num">'+fmtE2(p.certificacion)+'</td><td class="num">'+(p.pct*100).toFixed(2)+'%</td><td class="num">'+fmtE2(p.prorrateo)+'</td></tr>';
  });
  prr2+='<tr class="total-row"><td>TOTAL</td><td class="num">'+fmtE2(cert)+'</td><td class="num">100.00%</td><td class="num">'+fmtE2(gc)+'</td></tr>';
  var prt=document.querySelector('#prorrTable tbody');if(prt)prt.innerHTML=prr2;
}
