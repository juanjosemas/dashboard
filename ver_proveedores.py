#!/usr/bin/env python3
"""
Visor de Presupuestos por Proveedor
====================================
Escanea la carpeta PROVEEDORES, genera un HTML interactivo,
lanza un servidor local y abre el navegador.

Uso: python ver_proveedores.py
"""

import os
import json
import webbrowser
import http.server
import socketserver
import threading
import sys
import io
from pathlib import Path

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ─── Configuración ───────────────────────────────────────────────
PROVEEDORES_DIR = r"C:\Users\jjmax\Downloads\PROVEEDORES"
PORT = 8765

# ─── Escanear carpetas ───────────────────────────────────────────
def escanear_proveedores(base_dir):
    """Devuelve dict con {proveedor: [archivos_pdf]}"""
    proveedores = {}
    base = Path(base_dir)
    
    if not base.exists():
        print(f"❌ No se encuentra la carpeta: {base_dir}")
        sys.exit(1)
    
    for carpeta in sorted(base.iterdir()):
        if carpeta.is_dir() and not carpeta.name.startswith('.'):
            pdfs = sorted([
                f.name for f in carpeta.iterdir()
                if f.is_file() and f.suffix.lower() == '.pdf'
            ])
            if pdfs:
                proveedores[carpeta.name] = pdfs
    
    return proveedores


# ─── Generar HTML ─────────────────────────────────────────────────
def generar_html(proveedores):
    """Genera el HTML del visor"""
    
    # Calcular estadísticas
    total_proveedores = len(proveedores)
    total_pdfs = sum(len(p) for p in proveedores.values())
    
    # Generar las tarjetas de proveedores
    tarjetas_html = ""
    for i, (proveedor, pdfs) in enumerate(proveedores.items()):
        pdfs_html = ""
        for pdf in pdfs:
            # URL relativa al servidor
            url_pdf = f"{proveedor}/{pdf}".replace("\\", "/")
            # Limpiar nombre para mostrar
            nombre_limpio = pdf.replace(".pdf", "").strip()
            pdfs_html += f"""
                    <a href="{url_pdf}" target="_blank" class="pdf-item">
                        <div class="pdf-icon">📄</div>
                        <div class="pdf-info">
                            <div class="pdf-name">{nombre_limpio}</div>
                            <div class="pdf-size">PDF</div>
                        </div>
                        <div class="pdf-arrow">→</div>
                    </a>"""
        
        # Ícono según el tipo de proveedor
        icono = "🔧"
        if "ELECTRIC" in proveedor.upper() or "FERRIS" in proveedor.upper():
            icono = "⚡"
        elif "CLIMA" in proveedor.upper() or "AIRE" in proveedor.upper() or "GOCLIMA" in proveedor.upper():
            icono = "❄️"
        elif "ACAV" in proveedor.upper():
            icono = "🚪"
        
        tarjetas_html += f"""
        <div class="proveedor-card" data-index="{i}">
            <div class="proveedor-header" onclick="toggleProveedor({i})">
                <div class="proveedor-left">
                    <span class="proveedor-icon">{icono}</span>
                    <div class="proveedor-info">
                        <h3 class="proveedor-name">{proveedor}</h3>
                        <span class="proveedor-count">{len(pdfs)} presupuesto{'s' if len(pdfs) != 1 else ''}</span>
                    </div>
                </div>
                <div class="proveedor-toggle" id="toggle-{i}">▼</div>
            </div>
            <div class="proveedor-body" id="body-{i}">
                <div class="pdf-list">
                    {pdfs_html}
                </div>
            </div>
        </div>"""
    
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Presupuestos - Proveedores</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  
  body {{
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    min-height: 100vh;
    color: #333;
  }}
  
  /* ─── Header ─── */
  .header {{
    background: linear-gradient(135deg, #2B3A4E 0%, #1a2533 100%);
    color: white;
    padding: 30px 40px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  }}
  .header-content {{
    max-width: 1100px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
  }}
  .header h1 {{
    font-size: 1.8rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 12px;
  }}
  .header h1 .emoji {{ font-size: 2rem; }}
  .header-stats {{
    display: flex;
    gap: 24px;
  }}
  .stat {{
    text-align: center;
  }}
  .stat-value {{
    font-size: 1.6rem;
    font-weight: 700;
    color: #4ecdc4;
  }}
  .stat-label {{
    font-size: 0.75rem;
    color: #8899aa;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }}
  
  /* ─── Barra de búsqueda ─── */
  .search-bar {{
    max-width: 1100px;
    margin: 24px auto 0;
    padding: 0 40px;
  }}
  .search-wrapper {{
    position: relative;
  }}
  .search-wrapper input {{
    width: 100%;
    padding: 14px 20px 14px 48px;
    border: 2px solid #e0e0e0;
    border-radius: 12px;
    font-size: 1rem;
    background: white;
    transition: border-color 0.3s, box-shadow 0.3s;
    outline: none;
  }}
  .search-wrapper input:focus {{
    border-color: #D4742C;
    box-shadow: 0 0 0 3px rgba(212, 116, 44, 0.15);
  }}
  .search-wrapper .search-icon {{
    position: absolute;
    left: 16px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 1.2rem;
    color: #999;
  }}
  .search-wrapper .clear-btn {{
    position: absolute;
    right: 16px;
    top: 50%;
    transform: translateY(-50%);
    background: none;
    border: none;
    font-size: 1.2rem;
    color: #999;
    cursor: pointer;
    display: none;
  }}
  .search-wrapper .clear-btn.visible {{ display: block; }}
  
  /* ─── Contenido ─── */
  .container {{
    max-width: 1100px;
    margin: 24px auto;
    padding: 0 40px 40px;
  }}
  
  /* ─── Cards de proveedor ─── */
  .proveedor-card {{
    background: white;
    border-radius: 14px;
    margin-bottom: 16px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    overflow: hidden;
    transition: box-shadow 0.3s, transform 0.2s;
  }}
  .proveedor-card:hover {{
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  }}
  .proveedor-card.hidden {{ display: none; }}
  
  .proveedor-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 24px;
    cursor: pointer;
    user-select: none;
    transition: background 0.2s;
  }}
  .proveedor-header:hover {{
    background: #f8f9fa;
  }}
  
  .proveedor-left {{
    display: flex;
    align-items: center;
    gap: 16px;
  }}
  .proveedor-icon {{
    font-size: 2rem;
    width: 50px;
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #f0f4f8;
    border-radius: 12px;
  }}
  .proveedor-name {{
    font-size: 1.1rem;
    font-weight: 600;
    color: #2B3A4E;
    margin: 0;
  }}
  .proveedor-count {{
    font-size: 0.8rem;
    color: #888;
  }}
  
  .proveedor-toggle {{
    font-size: 0.9rem;
    color: #999;
    transition: transform 0.3s;
  }}
  .proveedor-toggle.open {{
    transform: rotate(180deg);
  }}
  
  /* ─── Lista de PDFs ─── */
  .proveedor-body {{
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.4s ease, padding 0.3s ease;
    padding: 0 24px;
  }}
  .proveedor-body.open {{
    max-height: 1000px;
    padding: 0 24px 20px;
  }}
  
  .pdf-list {{
    border-top: 1px solid #eee;
    padding-top: 12px;
  }}
  
  .pdf-item {{
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 14px 16px;
    border-radius: 10px;
    text-decoration: none;
    color: inherit;
    transition: background 0.2s, transform 0.15s;
    margin-bottom: 4px;
  }}
  .pdf-item:hover {{
    background: #fff8f0;
    transform: translateX(4px);
  }}
  
  .pdf-icon {{
    font-size: 1.6rem;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #fee2e2;
    border-radius: 10px;
    flex-shrink: 0;
  }}
  
  .pdf-info {{
    flex: 1;
    min-width: 0;
  }}
  .pdf-name {{
    font-weight: 600;
    font-size: 0.92rem;
    color: #2B3A4E;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }}
  .pdf-size {{
    font-size: 0.75rem;
    color: #999;
    margin-top: 2px;
  }}
  
  .pdf-arrow {{
    font-size: 1.2rem;
    color: #D4742C;
    opacity: 0;
    transition: opacity 0.2s;
    flex-shrink: 0;
  }}
  .pdf-item:hover .pdf-arrow {{
    opacity: 1;
  }}
  
  /* ─── Botón expandir todo ─── */
  .toolbar {{
    display: flex;
    gap: 12px;
    margin-bottom: 20px;
    flex-wrap: wrap;
  }}
  .toolbar-btn {{
    padding: 10px 20px;
    border: 2px solid #e0e0e0;
    border-radius: 10px;
    background: white;
    font-size: 0.85rem;
    font-weight: 600;
    color: #555;
    cursor: pointer;
    transition: all 0.2s;
  }}
  .toolbar-btn:hover {{
    border-color: #D4742C;
    color: #D4742C;
  }}
  .toolbar-btn.active {{
    background: #D4742C;
    border-color: #D4742C;
    color: white;
  }}
  
  /* ─── Empty state ─── */
  .empty-state {{
    text-align: center;
    padding: 60px 20px;
    color: #999;
  }}
  .empty-state .emoji {{ font-size: 3rem; margin-bottom: 12px; }}
  .empty-state p {{ font-size: 1rem; }}
  
  /* ─── Footer ─── */
  .footer {{
    text-align: center;
    padding: 20px;
    color: #aaa;
    font-size: 0.75rem;
  }}
  
  /* ─── Responsive ─── */
  @media (max-width: 600px) {{
    .header {{ padding: 20px; }}
    .header h1 {{ font-size: 1.3rem; }}
    .container, .search-bar {{ padding: 0 16px; }}
    .proveedor-header {{ padding: 16px; }}
    .proveedor-icon {{ width: 40px; height: 40px; font-size: 1.4rem; }}
  }}
</style>
</head>
<body>

<div class="header">
  <div class="header-content">
    <h1>
      <span class="emoji">📋</span>
      Presupuestos por Proveedor
    </h1>
    <div class="header-stats">
      <div class="stat">
        <div class="stat-value">{total_proveedores}</div>
        <div class="stat-label">Proveedores</div>
      </div>
      <div class="stat">
        <div class="stat-value">{total_pdfs}</div>
        <div class="stat-label">Presupuestos</div>
      </div>
    </div>
  </div>
</div>

<div class="search-bar">
  <div class="search-wrapper">
    <span class="search-icon">🔍</span>
    <input type="text" id="searchInput" placeholder="Buscar proveedor o presupuesto..." oninput="filtrar()">
    <button class="clear-btn" id="clearBtn" onclick="limpiarBusqueda()">✕</button>
  </div>
</div>

<div class="container">
  <div class="toolbar">
    <button class="toolbar-btn" onclick="expandirTodo()">📂 Expandir todo</button>
    <button class="toolbar-btn" onclick="colapsarTodo()">📁 Colapsar todo</button>
  </div>
  
  <div id="proveedoresList">
    {tarjetas_html}
  </div>
  
  <div class="empty-state" id="emptyState" style="display:none">
    <div class="emoji">🔍</div>
    <p>No se encontraron resultados</p>
  </div>
</div>

<div class="footer">
  Presupuestos Proveedores · ECO STRUCT · Generado automáticamente
</div>

<script>
function toggleProveedor(index) {{
  const body = document.getElementById('body-' + index);
  const toggle = document.getElementById('toggle-' + index);
  body.classList.toggle('open');
  toggle.classList.toggle('open');
}}

function expandirTodo() {{
  document.querySelectorAll('.proveedor-body').forEach(el => el.classList.add('open'));
  document.querySelectorAll('.proveedor-toggle').forEach(el => el.classList.add('open'));
}}

function colapsarTodo() {{
  document.querySelectorAll('.proveedor-body').forEach(el => el.classList.remove('open'));
  document.querySelectorAll('.proveedor-toggle').forEach(el => el.classList.remove('open'));
}}

function filtrar() {{
  const query = document.getElementById('searchInput').value.toLowerCase().trim();
  const clearBtn = document.getElementById('clearBtn');
  clearBtn.classList.toggle('visible', query.length > 0);
  
  const cards = document.querySelectorAll('.proveedor-card');
  let visibles = 0;
  
  cards.forEach(card => {{
    const nombre = card.querySelector('.proveedor-name').textContent.toLowerCase();
    const pdfs = card.querySelectorAll('.pdf-name');
    let algunPdfVisible = false;
    
    pdfs.forEach(pdfEl => {{
      const pdfCard = pdfEl.closest('.pdf-item');
      if (pdfEl.textContent.toLowerCase().includes(query) || query === '') {{
        pdfCard.style.display = 'flex';
        algunPdfVisible = true;
      }} else {{
        pdfCard.style.display = 'none';
      }}
    }});
    
    if (nombre.includes(query) || algunPdfVisible || query === '') {{
      card.classList.remove('hidden');
      visibles++;
      // Auto-expandir si hay búsqueda
      if (query.length > 0) {{
        card.querySelector('.proveedor-body').classList.add('open');
        card.querySelector('.proveedor-toggle').classList.add('open');
      }}
    }} else {{
      card.classList.add('hidden');
    }}
  }});
  
  document.getElementById('emptyState').style.display = visibles === 0 ? 'block' : 'none';
}}

function limpiarBusqueda() {{
  document.getElementById('searchInput').value = '';
  filtrar();
}}

// Atajo de teclado: Ctrl+K para buscar
document.addEventListener('keydown', function(e) {{
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {{
    e.preventDefault();
    document.getElementById('searchInput').focus();
  }}
}});
</script>

</body>
</html>"""
    
    return html


# ─── Servidor HTTP ────────────────────────────────────────────────
class QuietHandler(http.server.SimpleHTTPRequestHandler):
    """Handler silencioso que no imprime cada request"""
    def log_message(self, format, *args):
        pass  # Silenciar logs


def iniciar_servidor(directory, port):
    """Inicia el servidor HTTP en el directorio dado"""
    os.chdir(directory)
    
    # Buscar puerto disponible
    for p in range(port, port + 100):
        try:
            with socketserver.TCPServer(("", p), QuietHandler) as httpd:
                httpd.server_close()
                port = p
                break
        except OSError:
            continue
    
    handler = QuietHandler
    httpd = socketserver.TCPServer(("", port), handler)
    
    print(f"🌐 Servidor iniciado en http://localhost:{port}")
    print(f"📂 Sirviendo desde: {directory}")
    print(f"🔗 Abre: http://localhost:{port}/index.html")
    print(f"\n⏹  Pulse Ctrl+C para detener el servidor\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido.")
        httpd.server_close()


# ─── Main ─────────────────────────────────────────────────────────
def main():
    print("=" * 55)
    print("  VISOR DE PRESUPUESTOS POR PROVEEDOR")
    print("  ECO STRUCT")
    print("=" * 55)
    print()
    
    # 1. Escanear
    print("🔍 Escaneando carpetas de proveedores...")
    proveedores = escanear_proveedores(PROVEEDORES_DIR)
    
    if not proveedores:
        print("❌ No se encontraron proveedores con PDFs.")
        sys.exit(1)
    
    total = sum(len(p) for p in proveedores.values())
    print(f"   ✅ {len(proveedores)} proveedores, {total} presupuestos encontrados")
    
    for prov, pdfs in proveedores.items():
        print(f"   📁 {prov}: {len(pdfs)} PDFs")
    
    # 2. Generar HTML
    print("\n📝 Generando visor HTML...")
    html = generar_html(proveedores)
    
    html_path = os.path.join(PROVEEDORES_DIR, "index.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"   ✅ Creado: {html_path}")
    
    # 3. Abrir navegador
    url = f"http://localhost:{PORT}/index.html"
    print(f"\n🌍 Abriendo navegador...")
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    
    # 4. Iniciar servidor
    print()
    iniciar_servidor(PROVEEDORES_DIR, PORT)


if __name__ == "__main__":
    main()
