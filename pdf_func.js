function generatePDF(){
var btn=document.getElementById('btnPDF');
btn.innerHTML='&#9203; Generando PDF...';
btn.disabled=true;btn.style.opacity='0.7';
setTimeout(function(){
try{
var jsPDF=window.jspdf.jsPDF;
var doc=new jsPDF({unit:'mm',format:'a4',orientation:'portrait'});
var W=210,H=297,mL=15,mR=15,mT=15,mB=15;
var cW=W-mL-mR;
var y=mT;
var allProjects=typeof projectData!=='undefined'?projectData:[];
var sel=document.getElementById('pdfProjectSelect');
var filterName=sel?sel.value:'';
var projects=filterName?allProjects.filter(function(p){return p.nombre===filterName;}):allProjects;
if(filterName&&projects.length===0){projects=allProjects;}
var d=new Date();
var ds=d.getDate()+'/'+(d.getMonth()+1)+'/'+d.getFullYear();
var titleSuffix=filterName?' - '+filterName:'';
function fmtE(v){
var neg=v<0;
var abs=Math.abs(v);
var intPart=Math.floor(abs);
var decPart=Math.round((abs-intPart)*100);
var decStr=decPart<10?'0'+decPart:String(decPart);
var s=String(intPart);
var result='';
var count=0;
for(var i=s.length-1;i>=0;i--){
count++;
result=s[i]+result;
if(count%3===0&&i!==0) result='.'+result;
}
return (neg?'- ':'')+result+','+decStr;
}
function checkPage(needed){
if(y+needed>H-mB){doc.addPage();y=mT;return true;}
return false;
}
function addLine(color){
doc.setDrawColor(color||212);doc.setLineWidth(0.5);
doc.line(mL,y,W-mR,y);y+=4;
}
var tC=0,tD=0,tP=0,tM=0,tO=0,tG=0,cc=0,nc=0;
projects.forEach(function(p){
tC+=p.certificacion;tD+=p.gastos_directos;tP+=p.prorrateo;
tM+=p.mano_obra;tO+=p.total_coste;tG+=p.margen;
if(p.has_cert)cc++;else nc++;
});
var mp=tC>0?(tG/tC*100).toFixed(1):'0';
doc.setFillColor(43,76,111);doc.rect(0,0,W,45,'F');
doc.setTextColor(255,255,255);doc.setFontSize(28);doc.setFont('helvetica','bold');
doc.text('ECO STRUCT',W/2,20,{align:'center'});
doc.setFontSize(13);doc.setFont('helvetica','normal');
doc.text('Constructive Ecosen Spain 2.3',W/2,28,{align:'center'});
doc.setFontSize(10);
doc.text('Dashboard Financiero',W/2,35,{align:'center'});
y=60;
doc.setTextColor(43,58,78);doc.setFontSize(22);doc.setFont('helvetica','bold');
doc.text('INFORME FINANCIERO',W/2,y,{align:'center'});y+=10;
doc.setFontSize(12);doc.setFont('helvetica','normal');
doc.setTextColor(90,106,122);
doc.text('Auditoria de Costes y Certificaciones'+titleSuffix,W/2,y,{align:'center'});y+=8;
doc.setFontSize(11);
doc.text('Fecha: '+ds,W/2,y,{align:'center'});y+=20;
addLine(212);y+=10;
doc.addPage();y=mT;
doc.setFontSize(14);doc.setFont('helvetica','bold');doc.setTextColor(212,116,44);
doc.text('1. RESUMEN EJECUTIVO'+titleSuffix,mL,y);y+=3;addLine(212);y+=4;
var kpis=[
{l:'Certificaciones',v:fmtE(tC)+' EUR',bc:[43,76,111]},
{l:'Gastos Directos',v:fmtE(tD)+' EUR',bc:[233,69,96]},
{l:'Gastos Comunes',v:fmtE(tP)+' EUR',bc:[243,156,18]},
{l:'Mano de Obra',v:fmtE(tM)+' EUR',bc:[142,68,173]},
{l:'MARGEN TOTAL',v:fmtE(tG)+' EUR',bc:tG>=0?[46,204,113]:[231,76,60]}
];
var bx=mL,bw=(cW-8)/5;
kpis.forEach(function(k,i){
doc.setFillColor(245,240,232);doc.roundedRect(bx,y,bw,18,2,2,'F');
doc.setFillColor(k.bc[0],k.bc[1],k.bc[2]);doc.rect(bx,y,2,18,'F');
doc.setFontSize(6);doc.setFont('helvetica','bold');doc.setTextColor(90,106,122);
doc.text(k.l.toUpperCase(),bx+5,y+5);
doc.setFontSize(10);doc.setFont('helvetica','bold');doc.setTextColor(43,58,78);
doc.text(k.v,bx+5,y+12);
bx+=bw+2;
});
y+=24;
doc.setFontSize(11);doc.setFont('helvetica','bold');doc.setTextColor(43,76,111);
doc.text('Composicion de Costes Totales',mL,y);y+=6;
doc.setFillColor(43,76,111);doc.rect(mL,y,cW,7,'F');
doc.setFontSize(8);doc.setFont('helvetica','bold');doc.setTextColor(255,255,255);
doc.text('Concepto',mL+3,y+5);
doc.text('Importe',mL+cW-50,y+5,{align:'right'});
doc.text('% del Total',mL+cW-3,y+5,{align:'right'});
y+=7;
var items=[{n:'Gastos Directos',v:tD},{n:'Prorrateo GG+VEH',v:tP},{n:'Mano de Obra',v:tM}];
items.forEach(function(it,i){
if(i%2===0){doc.setFillColor(250,247,242);doc.rect(mL,y,cW,6,'F');}
doc.setFontSize(8);doc.setFont('helvetica','normal');doc.setTextColor(43,58,78);
doc.text(it.n,mL+3,y+4.5);
doc.text(fmtE(it.v)+' EUR',mL+cW-50,y+4.5,{align:'right'});
var pct=tO>0?(it.v/tO*100).toFixed(1):'0';
doc.text(pct+'%',mL+cW-3,y+4.5,{align:'right'});
y+=6;
});
doc.setFillColor(245,240,232);doc.rect(mL,y,cW,7,'F');
doc.setDrawColor(43,76,111);doc.setLineWidth(0.3);doc.line(mL,y,W-mR,y);
doc.setFontSize(8);doc.setFont('helvetica','bold');doc.setTextColor(43,58,78);
doc.text('TOTAL COSTES',mL+3,y+5);
doc.text(fmtE(tO)+' EUR',mL+cW-50,y+5,{align:'right'});
doc.text('100%',mL+cW-3,y+5,{align:'right'});
y+=12;
doc.setFontSize(9);doc.setTextColor(90,106,122);
doc.text('Eficiencia Coste/Certif: '+(tC>0?(tO/tC*100).toFixed(1):'0')+'% | Obras con beneficio: '+cc+' | Obras con perdida: '+nc,mL,y);
if(!filterName){
doc.addPage();y=mT;
doc.setFontSize(14);doc.setFont('helvetica','bold');doc.setTextColor(212,116,44);
doc.text('2. DETALLE POR PROYECTO',mL,y);y+=3;addLine(212);y+=4;
doc.setFillColor(43,76,111);doc.rect(mL,y,cW,7,'F');
doc.setFontSize(7);doc.setFont('helvetica','bold');doc.setTextColor(255,255,255);
var th=['#','Proyecto','Certif.','G.Directos','Prorrateo','Mano Obra','TOTAL','MARGEN'];
var tw=[8,52,28,28,28,28,28,28];
var tx=mL;
th.forEach(function(h,i){doc.text(h,tx+2,y+5);tx+=tw[i];});
y+=7;
projects.forEach(function(p,i){
checkPage(6);
if(i%2===0){doc.setFillColor(250,247,242);doc.rect(mL,y,cW,5.5,'F');}
var mc=p.margen>=0?[46,204,113]:[231,76,60];
doc.setFontSize(7);doc.setFont('helvetica','normal');doc.setTextColor(43,58,78);
var cv=p.has_cert?fmtE(p.certificacion):'-';
var vals=[String(i+1),p.nombre.length>28?p.nombre.substring(0,26)+'..':p.nombre,cv,fmtE(p.gastos_directos),fmtE(p.prorrateo),fmtE(p.mano_obra),fmtE(p.total_coste),fmtE(p.margen)];
tx=mL;
vals.forEach(function(v,j){
if(j===7){doc.setTextColor(mc[0],mc[1],mc[2]);doc.setFont('helvetica','bold');}
doc.text(v,tx+2,y+4);
if(j===7){doc.setTextColor(43,58,78);doc.setFont('helvetica','normal');}
tx+=tw[j];
});
y+=5.5;
});
checkPage(7);
doc.setFillColor(245,240,232);doc.rect(mL,y,cW,7,'F');
doc.setDrawColor(43,76,111);doc.setLineWidth(0.3);doc.line(mL,y,W-mR,y);
doc.setFontSize(7);doc.setFont('helvetica','bold');doc.setTextColor(43,58,78);
var tv=['','TOTAL',fmtE(tC),fmtE(tD),fmtE(tP),fmtE(tM),fmtE(tO),fmtE(tG)];
tx=mL;
tv.forEach(function(v,j){doc.text(v,tx+2,y+5);tx+=tw[j];});
var sectionNum=3;
}else{
var sectionNum=2;
}
doc.addPage();y=mT;
doc.setFontSize(14);doc.setFont('helvetica','bold');doc.setTextColor(212,116,44);
doc.text(sectionNum+'. ANALISIS POR PROYECTO'+titleSuffix,mL,y);y+=3;addLine(212);y+=4;
projects.forEach(function(p,i){
checkPage(35);
var mc=p.margen>=0?[46,204,113]:[231,76,60];
doc.setFontSize(11);doc.setFont('helvetica','bold');doc.setTextColor(43,76,111);
doc.text((i+1)+'. '+p.nombre,mL,y);y+=6;
var ky=y;var kbx=mL;var kbw=(cW-4)/3;
var kItems=[
{l:'Certificacion',v:p.has_cert?fmtE(p.certificacion)+' EUR':'Sin certif.',bc:[43,76,111]},
{l:'Coste Total',v:fmtE(p.total_coste)+' EUR',bc:[233,69,96]},
{l:'Margen',v:fmtE(p.margen)+' EUR ('+p.margen_pct+'%)',bc:mc}
];
kItems.forEach(function(k){
doc.setFillColor(245,240,232);doc.roundedRect(kbx,ky,kbw,14,1,1,'F');
doc.setFillColor(k.bc[0],k.bc[1],k.bc[2]);doc.rect(kbx,ky,1.5,14,'F');
doc.setFontSize(5.5);doc.setFont('helvetica','bold');doc.setTextColor(90,106,122);
doc.text(k.l.toUpperCase(),kbx+4,ky+5);
doc.setFontSize(9);doc.setFont('helvetica','bold');doc.setTextColor(43,58,78);
doc.text(k.v,kbx+4,ky+11);
kbx+=kbw+2;
});
y+=18;
doc.setFontSize(7);doc.setFont('helvetica','bold');
doc.setFillColor(43,76,111);doc.rect(mL,y,cW,5,'F');
doc.setTextColor(255,255,255);
doc.text('Componente',mL+3,y+3.5);
doc.text('Importe',mL+cW-45,y+3.5,{align:'right'});
doc.text('% Coste',mL+cW-3,y+3.5,{align:'right'});
y+=5;
var comps=[{n:'Gastos Directos',v:p.gastos_directos},{n:'Prorrateo GG+VEH',v:p.prorrateo},{n:'Mano de Obra',v:p.mano_obra}];
comps.forEach(function(c2,j){
if(j%2===0){doc.setFillColor(250,247,242);doc.rect(mL,y,cW,4.5,'F');}
doc.setFontSize(7);doc.setFont('helvetica','normal');doc.setTextColor(43,58,78);
doc.text(c2.n,mL+3,y+3.2);
doc.text(fmtE(c2.v)+' EUR',mL+cW-45,y+3.2,{align:'right'});
var pct=p.total_coste>0?(c2.v/p.total_coste*100).toFixed(1):'0';
doc.text(pct+'%',mL+cW-3,y+3.2,{align:'right'});
y+=4.5;
});
doc.setFillColor(245,240,232);doc.rect(mL,y,cW,5,'F');
doc.setDrawColor(43,76,111);doc.setLineWidth(0.2);doc.line(mL,y,W-mR,y);
doc.setFontSize(7);doc.setFont('helvetica','bold');
doc.text('TOTAL',mL+3,y+3.5);
doc.text(fmtE(p.total_coste)+' EUR',mL+cW-45,y+3.5,{align:'right'});
doc.text('100%',mL+cW-3,y+3.5,{align:'right'});
y+=10;
});
var totalPages=doc.internal.getNumberOfPages();
for(var pg=1;pg<=totalPages;pg++){
doc.setPage(pg);
doc.setFontSize(6);doc.setFont('helvetica','normal');doc.setTextColor(170,170,170);
var footerText='ECO STRUCT - Constructive Ecosen Spain 2.3 | Informe generado el '+ds;
if(filterName) footerText+=' | Obra: '+filterName;
footerText+=' | Pagina '+pg+' de '+totalPages;
doc.text(footerText,mL,H-8);
}
var fileName='ECO_STRUCT';
if(filterName) fileName+='_obra-'+filterName.substring(0,20);
fileName+='_Informe_'+ds.split('/').join('-')+'.pdf';
doc.save(fileName);
btn.innerHTML='<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg> Exportar PDF';
btn.disabled=false;btn.style.opacity='1';
}catch(err){
console.error('PDF Error:',err);
alert('Error generando PDF: '+err.message);
btn.innerHTML='Exportar PDF';
btn.disabled=false;btn.style.opacity='1';
}
},100);
}
function generateObraPDF(nombre){
var sel=document.getElementById('pdfProjectSelect');
if(sel){sel.value=nombre;}
generatePDF();
}
function pdfFromDetail(){
  var el=document.getElementById('detail-title');
  var nombre=el.getAttribute('data-nombre');
  if(nombre) generateObraPDF(nombre);
}