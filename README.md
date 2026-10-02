# ECO STRUCT — Dashboard Financiero de Obras

Control de costes y margen de las obras de ECO STRUCT Constructive.
Todo el proyecto es **autónomo**: vive en esta carpeta y no depende de ninguna
carpeta de red ni de ningún servidor.

- **Dashboard en línea:** <https://juanjosemas.github.io/dashboard/>
- **Versión clásica (V1):** [`dashboard.html`](dashboard.html)
- **Versión corporativa oscura (V2):** [`dashboard_v2.html`](dashboard_v2.html) — es la que abre `index.html`
- **Excel de trabajo:** [`ECO_STRUCT_Datos.xlsx`](ECO_STRUCT_Datos.xlsx)

---

## Cómo se usa (lo normal)

1. Actualizas tus datos en los **3 archivos de la carpeta [`dashboard/`](dashboard)**.
2. Haces doble clic en **[`actualizar.bat`](actualizar.bat)**.
3. Listo: se regenera el dashboard, el Excel, la copia de seguridad y te pregunta si quieres subirlo a GitHub.

---

## Los 3 archivos de entrada

Los único que tienes que mantener tú. Van en la carpeta [`dashboard/`](dashboard):

| Archivo | Qué contiene | Formato |
|---|---|---|
| `ECO_STRUCT_-_Workspace_Gastos.csv` | Todas las facturas de gastos (directos, generales y vehículos) | CSV separated por `;`, codificación **latin-1** |
| `CERTIFICACIONES POR MESES 2026.xlsx` | Certificaciones de cada obra, mes a mes. Fila 1 = título, fila 2 = meses, datos desde la fila 4. Columna N = total, columna O = importe | Excel |
| `GASTOS MANO DE OBRA POR MESES 2026.xlsx` | Horas de mano de obra por obra y mes. Columna 15 = precio/hora, 16 = suma de horas, 17 = gasto total | Excel |

> ⚠️ El CSV **no** es UTF-8. Si lo abres y lo guardas desde Excel, déjalo en
> "CSV (separado por punto y coma)" y no lo conviertas, o las tildes se
> romperán y las obras dejarán de emparejarse.

---

## Reglas de cálculo

- Solo se trabaja el año en curso. **No se incluyen facturas de otros años.**
- Se usa la columna **"Fecha"** para decidir el mes de cada factura.
- **Certificaciones:** se leen del xlsx y se agrupan por obra.
- **Mano de obra:** se lee del xlsx, con el precio/hora de la propia columna 15 (actualmente 17,00 €/h). Si en el xlsx hubiera precios distintos, se avisa y cada obra usa el suyo.
- **Prorrateo de gastos comunes:** se reparte desde el **primer mes con actividad** de cada obra, usando el **% anual de certificaciones**.
- **Gastos Comunes** en pantalla:
  - con obras seleccionadas en el filtro → muestra el **prorrateo adjudicado** a esas obras;
  - con "Todas" → muestra el total real (**Gastos Generales + Vehículos**).

### Cómo se emparejan las obras

El nombre de la obra en el CSV casi nunca coincide literalmente con el del xlsx
(espacios, tildes, guiones). El emparejamiento es, por orden:

1. **Código de obra** (los 4-5 dígitos al principio del nombre). Es lo más fiable.
2. **Nombre normalizado** (mayúsculas, sin acentos, sin espacios ni signos).
3. Coincidencia por palabras clave.

---

## Obras huérfanas

Si una obra tiene facturas pero no aparece en el xlsx de certificaciones, sus
gastos se quedan "sueltos" y el margen sale más bajo. Cada vez que se actualiza
se genera **[`INFORME_HUERFANAS.txt`](INFORME_HUERFANAS.txt)** con la lista, el
importe y el motivo de cada una. En el dashboard aparecen marcadas en rojo con
`⚠`.

Arreglar una huérfana significa **corregir el nombre de la obra en el CSV** para
que coincida con el del xlsx de certificaciones (mismo código de obra).

### Cómo se reflejan en el Excel

En la pestaña **Resumen** del Excel, la columna **"Gastos Directos (EUR)"** es
el `SUMIF` de la pestaña **"Gastos por Proyecto"**: solo las facturas imputadas a
esa obra. Los gastos generales y los vehículos van aparte (celdas B5 y B6), el
prorrateo va en la columna D y la mano de obra en la F.

Debajo de las 23 obras con certificación se añade un bloque **"OBRAS SIN
CERTIFICACION"** con las huérfanas (certificación 0, margen negativo = pérdida),
y esas filas **sí se suman** en el TOTAL GENERAL. Así el Excel cuadra con el
dashboard: certificaciones, gastos directos, mano de obra y margen coinciden al
céntimo (salvo el prorrateo, que puede diferir en céntimos por redondeo).

---

## Qué hace `actualizar.bat`

| Paso | Qué hace |
|---|---|
| 1 | `extraer_datos.py` → lee los 3 archivos y genera `datos_ecostruct.json` + `INFORME_HUERFANAS.txt` |
| 2 | `regenerar_dashboard.py` → genera `dashboard.html` (V1) |
| 2 | extrae `pdf_func.js` del V1 (para el botón de PDF por obra) |
| 2 | `regenerar_dashboard_v2.py` → genera `dashboard_v2.html` (V2) |
| 3 | `crear_excel_completo.py` → genera `ECO_STRUCT_Datos.xlsx` |
| 4 | `crear_copia_drive.py` → crea el ZIP y lo sube a Google Drive |
| 5 | Pregunta si quieres subir a GitHub (`subir_a_github.bat`) |

### Copia de seguridad

Se crea `COPIA_SEGURIDAD_DASHBOARD.zip` y se copia a la carpeta local de Google
Drive para escritorio. En esa carpeta hay un archivo `origen.txt` que recuerda
qué carpeta del proyecto gestiona la copia: si ejecutas `actualizar.bat` desde
una **copia** del proyecto, no pisará la copia de seguridad real.

---

## Los scripts

| Archivo | Para qué sirve |
|---|---|
| `extraer_datos.py` | Extrae y normaliza todo. Es el corazón del proyecto. |
| `regenerar_dashboard.py` | Genera `dashboard.html` (V1). |
| `regenerar_dashboard_v2.py` | Genera `dashboard_v2.html` (V2). |
| `crear_excel_completo.py` | Genera `ECO_STRUCT_Datos.xlsx`. |
| `crear_copia_drive.py` | ZIP de seguridad + sincronización con Drive. |
| `subir_a_github.bat` | `git add` + commit + push a GitHub Pages. |
| `gen_switchyear.py` | Genera el selector de año del dashboard. |
| `ver_proveedores.py` / `proveedores.html` | Análisis de proveedores. |
| `month_filter.js` | Filtro de mes y multi-select de obras (compartido por V1 y V2). |
| `pdf_func.js` | Generación de PDF por obra. Se regenera solo desde el V1. |
| `assets/symbol.png` | El logo que se incrusta en los dashboards. |

Todas las rutas son **relativas a la carpeta del proyecto**: puedes moverla,
copiarla o cambiarle el nombre y sigue funcionando.

---

## Requisitos

- **Python 3** instalado y accesible como `python` en el PATH.
- Las librerías `openpyxl` y `pillow`.