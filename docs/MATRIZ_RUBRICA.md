# Matriz de trazabilidad de la rúbrica

**Datos: Sports Reference LLC / Basketball-Reference.com.**

**Fuente de los criterios y pesos:** guía del proyecto registrada en `AGENTE.md`, sección 4.
**Fecha de esta auditoría:** 2026-11-18.
**Regla:** un criterio solo se marca `CUMPLE` si existe evidencia verificable en el repositorio.
`PARCIAL` = hay trabajo real pero falta un componente. `PENDIENTE` = no existe evidencia.

> **Advertencia de honestidad.** Esta matriz no estima una calificación ni promete un puntaje.
> Solo verifica que exista evidencia para cada requisito. La evaluación final depende del docente.

---

## Resumen

| # | Criterio | Peso | Estado | Evidencia principal |
|---|---|---:|---|---|
| 1 | Web scraping dinámico | 20 % | **CUMPLE** | `scraping.py`, `data/raw/fragments/` (54), `outputs/logs/scrape_log.csv`; el HTML crudo (`data/raw/html/`, 27) existe en local pero está excluido del repo público por `.gitignore` |
| 2 | Limpieza y manipulación | 20 % | **CUMPLE** | `limpieza.py`, `data/processed/nba_teams_clean.csv`, `outputs/metrics/limpieza_resumen.csv` |
| 3 | Modelado y optimización | 25 % | **CUMPLE con salvedad** | `modelado.py`, `outputs_corrida2_16vars_fase4/`, `docs/FASE_IV_MODELADO_16VARS.md` |
| 4 | Código y entregables | 15 % | **PARCIAL** | Código modular, repo público verificado, PDF borrador y presentación 16:9; falta el PDF final con el video |
| 5 | Sustentación en video | 20 % | **PENDIENTE** | Guion y presentación 16:9 listos en `docs/`; video sin grabar |

---

## 1. Web scraping dinámico — 20 %

**Nivel excelente esperado:** pandas y bucles eficientes sobre URLs dinámicas e iterativas;
consolidación limpia.

| Requisito | Evidencia | Estado |
|---|---|---|
| Fuente web real | Basketball-Reference, `https://www.basketball-reference.com/leagues/NBA_{año}.html` | CUMPLE |
| Scraping automatizado | `scraping.py` con `requests` + `pandas.read_html` | CUMPLE |
| Bucle que recorre páginas/iteraciones | `for year in range(2000, 2027)` sobre 27 temporadas | CUMPLE |
| Variables dinámicas | Una página por temporada; tablas *Advanced* y *Per Game* | CUMPLE |
| Consolidación en lista/diccionario | Fragmentos por temporada y tabla unida | CUMPLE |
| Evidencia de ejecución | `outputs/logs/scrape_log.csv` (17/11/2026); 54 fragmentos CSV; HTML en local, no publicado | CUMPLE |
| Respeto de límites del sitio | Pausa de 4 s, caché local, `User-Agent` identificable | CUMPLE |
| No es un CSV estático | Los datos se extraen y se cachean localmente; el CSV final se construye en Fase II | CUMPLE |

**Riesgo:** el `User-Agent` ya no contiene un correo personal; se identifica con el
usuario de GitHub `ctlucifer1504-bit`. No se publican correos ni códigos institucionales.

---

## 2. Limpieza y manipulación — 20 %

**Nivel excelente esperado:** concatenación masiva; nulos tratados con justificación; tipos
formateados; filtros múltiples bien agrupados.

| Requisito | Evidencia | Estado |
|---|---|---|
| `pd.concat()` | `limpieza.py` concatena los 54 fragmentos | CUMPLE |
| Duplicados tratados | 0 duplicados exactos y 0 por `(season, Team)`; verificado | CUMPLE |
| Nulos tratados con justificación | Solo `Attend.` y `Attend./G` (4 cada una), excluidas del modelo; documentado en `docs/DICCIONARIO_DATOS.md` | CUMPLE |
| Conversión explícita de tipos | `ADV_NUM` y `PG_NUM`; auditoría de conversión sin NaN nuevos | CUMPLE |
| Filtros con condiciones múltiples agrupadas | Dos filtros con `&` y `\|` en `limpieza.py`; resultados 53 y 40 equipos | CUMPLE |
| Evidencia de ejecución | `outputs/metrics/limpieza_resumen.csv`; dataset final 805 × 52 con hash estable | CUMPLE |

**Verificación reproducible:** el SHA256 del CSV procesado es
`c04704d9ecdd511b24bd81b1aef73250082e02bd1f63a501eed900f1f9ea3ea9` en todas las corridas
documentadas.

---

## 3. Modelado y optimización — 25 %

**Nivel excelente esperado:** train/test correcto; `GridSearchCV` exhaustivo; validación
cruzada; mejora del score documentada.

| Requisito | Evidencia | Estado |
|---|---|---|
| scikit-learn | `modelado.py` usa `Pipeline`, `GridSearchCV`, `cross_validate`, métricas de sklearn | CUMPLE |
| Clasificación o regresión | Clasificación binaria (`playoffs`) | CUMPLE |
| Train/test | Protocolo temporal (2000–2019 / 2020–2026) y estratificado 80/20 | CUMPLE |
| Modelo base | `DummyClassifier` + logística y Random Forest con hiperparámetros por defecto | CUMPLE |
| `GridSearchCV` | Logística: 8 combinaciones; Random Forest: 48 combinaciones | CUMPLE |
| Validación cruzada ≥ 5 folds | `StratifiedGroupKFold(5)` y `StratifiedKFold(5)` | CUMPLE |
| Comparación antes/después | `modelado_cv_base_vs_optimizado_{protocolo}_16vars.csv` | CUMPLE |
| Mejora del score documentada | **Ver salvedad abajo** | **PARCIAL** |
| Evaluación en test | Una sola evaluación por protocolo; `modelado_test_{protocolo}_16vars.csv` | CUMPLE |
| Métricas suficientes | Accuracy, precision, recall, F1, ROC-AUC, PR-AUC, Brier, matriz de confusión | CUMPLE |
| Control de fuga de datos | Pipeline ajustado dentro de cada fold; umbral elegido fuera de test; ningún modelo, hiperparámetro ni umbral elegido con test | CUMPLE |
| Interpretación | Importancia por permutación, coeficientes, VIF, sensibilidad | CUMPLE |

**Salvedad honesta sobre «mejora del score documentada»:**
- En validación cruzada, `GridSearchCV` mejora el F1 de 0,9076 a 0,9117 (**+0,004**).
- En test, la mejora **no se replica**: F1 0,866 vs. 0,879 con umbral 0,50.
- Con el umbral ajustado (0,46), el modelo optimizado alcanza F1 0,880 vs. 0,879 del base
  (**+0,001**) y mejora el Brier de 0,099 a 0,097 (**−0,002**).

El requisito de *comparar* antes y después se cumple con evidencia. El requisito literal de
*mejora* se cumple solo de forma marginal y no significativa. **No se infla el resultado.**
Para la defensa: explicar que la mejora pequeña es un hallazgo válido, que el modelo base ya
era fuerte y que forzar una conclusión contraria sería incorrecto.

---

## 4. Código y entregables — 15 %

**Nivel excelente esperado:** enlace público y funcional; código modular, limpio, sin errores
y comentado; PDF impecable.

| Requisito | Evidencia | Estado |
|---|---|---|
| Código modular | Cuatro scripts separados por fase; funciones con responsabilidad única | CUMPLE |
| Código comentado | Docstrings y comentarios en los cuatro scripts | CUMPLE |
| Sin errores de sintaxis | `python -m py_compile` sobre los cuatro scripts; pruebas en `tests/` | CUMPLE |
| Reproducibilidad | `requirements.txt` fijado; `docs/REPRODUCIBILIDAD.md` | CUMPLE |
| Repositorio público de GitHub | Publicado y verificado: `PUBLIC`, rama `main`, 144 archivos, sin datos | CUMPLE |
| Enlace funcional en el PDF | GitHub verificado; el de YouTube se añade al terminar el video | **PARCIAL** |
| PDF institucional | `docs/INFORME_FINAL_BORRADOR.pdf` generado (22 páginas, carta, índice y enlaces); falta el enlace del video y la exportación final | **PARCIAL** |
| Presentación del video | `docs/PRESENTACION_VIDEO.pdf` (18 páginas 16:9: 15 + 3 anexos) y guion por diapositiva en `docs/GUION_PRESENTACION_VIDEO.md` | **CUMPLE (borrador)** |

**Qué falta y quién debe hacerlo:** grabar y publicar el video, pegar su enlace en el
informe y regenerar el PDF final. El repositorio ya está publicado y verificado.

---

## 5. Sustentación en video — 20 %

**Nivel excelente esperado:** todos participan; explicaciones técnicas profundas, claras,
fluidas y demostrativas.

| Requisito | Evidencia | Estado |
|---|---|---|
| Guion estructurado | `docs/GUION_VIDEO.md` y `docs/GUION_PRESENTACION_VIDEO.md` con tiempos y reparto | CUMPLE (documento) |
| Duración ≤ 15 min | Guion planificado en ~13 min | CUMPLE (plan) |
| Todos los integrantes participan | Reparto definido en el guion | PENDIENTE de ejecución |
| Cámara encendida al inicio | Indicado en el guion | PENDIENTE de ejecución |
| Video público en YouTube | Sin grabar ni publicar | **PENDIENTE** |
| Enlace en el PDF | Depende del video | **PENDIENTE** |

---

## 6. Restricción expresa del curso

| Requisito | Estado | Evidencia |
|---|---|---|
| No usar el dataset de fútbol de Inglaterra | CUMPLE | El proyecto usa NBA. |
| No usar el dataset de laptops | CUMPLE | El proyecto usa NBA. |
| Confirmar el tema con el docente | **PENDIENTE** | No hay constancia de aprobación explícita del tema. |

---

## 7. Acciones pendientes antes de entregar

| # | Acción | Responsable | Bloquea |
|---|---|---|---|
| 1 | Revisar nombres, institución, asignatura y docente en la portada | **Hecho** | PDF y video |
| 2 | Crear repositorio público y subir el código | **Hecho** | Criterio 4 |
| 3 | Verificar enlaces públicos sin sesión | **Hecho** | Criterio 4 |
| 4 | Grabar y publicar el video (≤ 15 min) | Ambos integrantes | Criterio 5 |
| 5 | Añadir el enlace de YouTube y regenerar el PDF | Equipo | Criterio 4 |
| 6 | Reemplazar el correo de ejemplo del `User-Agent` | **Hecho** | Publicación |
| 7 | Confirmar el tema con el docente | Equipo | Riesgo académico |
| 8 | Elegir licencia del repositorio | **Hecho** (MIT + CC BY 4.0) | Publicación |

---

## 8. Conclusión de la auditoría

- **Criterios técnicos (1, 2 y 3):** evidencia suficiente y ejecutada. El criterio 3 tiene una
  salvedad honesta sobre la magnitud de la mejora.
- **Criterio 4:** el código está listo, el repositorio está publicado y la presentación
  existe; faltan el enlace del video y la exportación final del PDF.
- **Criterio 5:** depende enteramente de grabar el video.

**No se declara el proyecto terminado.** El estado global es **técnicamente completo,
administrativamente pendiente**.
