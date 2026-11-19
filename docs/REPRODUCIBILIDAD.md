# Reproducibilidad y entorno

**Datos: Sports Reference LLC / Basketball-Reference.com.** No se incluyen en el repo.

## Versiones exactas

| Componente | Versión |
|---|---|
| Sistema operativo | Windows (entorno local del equipo) |
| Python | 3.15.2 |
| pandas | 3.1.1 |
| numpy | 2.5.5 |
| requests | 2.34.2 |
| lxml | 6.1.3 |
| matplotlib | 3.11.2 |
| scikit-learn | 1.9.1 |

Las versiones están fijadas en `requirements.txt`. Las pruebas usan `unittest` de la
biblioteca estándar, así que no requieren dependencias adicionales.

## Instalación

```powershell
python -m venv .venv
& .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Ejecución en orden

Todos los scripts se ejecutan **desde la raíz del proyecto** porque usan rutas relativas.

En un **clon limpio no existe `data/`**. El flujo empieza obligatoriamente por la
extracción:

```powershell
& .\.venv\Scripts\python.exe scraping.py     # Fase I  (~2 min con pausas de 4 s)
& .\.venv\Scripts\python.exe limpieza.py     # Fase II (~segundos)
& .\.venv\Scripts\python.exe exploracion.py  # Fase III (~10 s)
& .\.venv\Scripts\python.exe modelado.py     # Fase IV (~1 min)
& .\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Las pruebas que necesitan el dataset se **omiten** con un mensaje claro si
`data/processed/nba_teams_clean.csv` no existe. Las de predictores y artefactos de Fase IV
sí corren. Para la suite completa, ejecuta primero `scraping.py` y `limpieza.py`.

## Salidas por fase

| Fase | Carpeta | Contenido | ¿Se publica? |
|---|---|---|---|
| I | `data/raw/html/`, `data/raw/fragments/`, `outputs/logs/` | 27 HTML, 54 CSV, log de scraping | Solo el log; datos no |
| II | `data/processed/`, `outputs/metrics/` | Dataset limpio y resumen de limpieza | Solo el resumen agregado |
| III | `outputs_corrida2_16vars/` | 11 figuras, 14 tablas, log y metadatos | Sí, tablas agregadas |
| IV | `outputs_corrida2_16vars_fase4/` | 10 figuras, 23 tablas/JSON en local (21 publicadas; se excluyen 2 de predicciones), 3 logs de consola y 3 logs del script | Sí, salvo predicciones fila a fila |

## Verificaciones de integridad

```powershell
# Hash del dataset (debe ser siempre el mismo)
Get-FileHash data\processed\nba_teams_clean.csv -Algorithm SHA256

# Suite de pruebas
& .\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Hash esperado del dataset:

```text
c04704d9ecdd511b24bd81b1aef73250082e02bd1f63a501eed900f1f9ea3ea9
```

## Notas de reproducibilidad

- `random_state=42` en todos los splits y modelos.
- `GridSearchCV` con `n_jobs=-1`; el orden de los resultados no depende de los núcleos.
- Las figuras se generan con backend `Agg`, sin ventana interactiva.
- `scraping.py` usa caché local: si ya existen los HTML, no vuelve a descargar.
- Las rutas son relativas; cambiar de carpeta rompe la ejecución.
- Los resultados pueden variar ligeramente entre versiones de scikit-learn; por eso se fijan.

## Generación del PDF

El PDF del informe se construye desde `docs/INFORME_FINAL.md` con
`tools/build_pdf.py`. Ese script no forma parte del pipeline de datos y no altera
ninguna cifra: solo convierte el Markdown, añade portada, índice con números de página,
pie de página y metadatos.

```powershell
python -m pip install markdown reportlab pypdf
& .\.venv\Scripts\python.exe tools\build_pdf.py
```

Requiere Google Chrome o Microsoft Edge instalado, que se usan en modo headless para
imprimir el HTML a PDF. Salida: `docs/INFORME_FINAL_BORRADOR.pdf`, 22 páginas en
tamaño carta. Los enlaces externos (GitHub, Basketball-Reference, pandas, scikit-learn)
quedan clicables y el índice enlaza a cada sección.

## Generación de la presentación

Las diapositivas del video se construyen con `tools/build_slides.py` a partir de las
figuras y métricas ya registradas. No recalcula nada.

```powershell
& .\.venv\Scripts\python.exe tools\build_slides.py
```

Salida: `docs/PRESENTACION_VIDEO.pdf`, 13 páginas horizontales de 16:9 (960 × 540 pt):
11 para narrar y 2 de anexo con evidencias.

El guion que se dice en cada diapositiva es un PDF aparte:

```powershell
& .\.venv\Scripts\python.exe tools\build_guion.py
```

Salida: `docs/GUION_PRESENTACION_VIDEO.pdf`, 7 páginas en A4 a una columna, con el mapa
de tiempos, la asignación Mauricio/Santiago y el texto literal por diapositiva.

## Advertencia sobre el scraping

El sitio limita a ~20 peticiones por minuto. El script usa pausas de 4 s y caché. Si el
sitio responde 403/429, **detenerse** y usar los HTML ya guardados en `data/raw/html/`.
No se debe evadir autenticación ni CAPTCHA.

## Datos y licencias

Los datos no se publican y no están cubiertos por MIT ni CC BY 4.0. Antes de reutilizarlos,
lee `docs/CONSIDERACIONES_LEGALES.md` y los términos de Sports Reference. Atribución:
*Datos: Sports Reference LLC / Basketball-Reference.com*.
