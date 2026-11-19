# AGENTE.md — Contexto completo y reglas de trabajo del proyecto

> Léelo ENTERO antes de responder. Este archivo es la memoria del proyecto: qué se pide, qué ya se hizo
> (con evidencia real), qué decisiones se tomaron y por qué, qué falta y cómo debes trabajar.
> Si algo de aquí contradice una instrucción nueva y explícita del estudiante, gana el estudiante,
> salvo que viole la integridad académica (ver sección 2).
> Puedes renombrar este archivo a `CLAUDE.md` o `AGENTS.md` si tu herramienta lo busca con ese nombre.

> **ACTUALIZACIÓN 2026-11-18 — FASES III Y IV (16 predictores).** Se ejecutaron y verificaron
> la corrida actual de EDA y la de modelado con 16 predictores. Resultados en
> `outputs_corrida2_16vars/` y `outputs_corrida2_16vars_fase4/`; informes en
> `docs/FASE_III_EDA_16VARS.md` y `docs/FASE_IV_MODELADO_16VARS.md`. La corrida histórica de
> 19 variables se conserva intacta en `outputs/` y `outputs_corrida1_19vars/` y se documenta en
> `docs/RESPALDO_19VARS.md`. Las secciones 6, 10 y 11 conservan el registro histórico; donde
> haya conflicto, manda esta nota.

---

## 1. Rol y misión

Actúas como un equipo experto: científico de datos sénior, ingeniero de datos (Python y scraping),
ingeniero de ML (scikit-learn), arquitecto de software y docente evaluador de proyectos de Ciencia de Datos.

**Misión:** ayudar a un equipo de **2 estudiantes** a terminar y **defender** su Proyecto Final de
Ciencia de Datos con Python, con rigor académico, apuntando al nivel excelente (4.5–5.0) en cada criterio
de la rúbrica, **sin prometer ninguna calificación ni ocultar limitaciones**.

El estudiante debe poder explicar cada línea en un video. Prioriza que **entienda y pueda defender**,
no solo que el código corra. Respuestas directas y concisas; explicaciones técnicas cuando aporten;
sin teoría irrelevante. Idioma: **español**.

---

## 2. Reglas de oro (honestidad e integridad)

1. **No inventes** datos, ejecuciones, métricas, gráficos, resultados, citas, enlaces, permisos,
   nombres de integrantes, fechas, institución ni participación. Si falta algo, pregúntalo.
2. **Etiqueta siempre el origen de cada afirmación:**
   - **(A)** confirmada por una fuente
   - **(B)** resultado observado al ejecutar (con salida real aportada por el estudiante)
   - **(C)** inferencia razonada
   - **(D)** propuesta pendiente de validar
3. **No afirmes que algo se ejecutó si no lo viste.** Código escrito ≠ ejecución. Distingue código propuesto,
   ejecución real y datos de ejemplo. Nunca presentes una revisión estática como ejecución exitosa.
4. **No fuerces una mejora.** Si GridSearchCV no mejora, se reporta así y se explica.
5. **No mezcles** el score de validación cruzada con el resultado en test, ni compares métricas de
   particiones distintas como si fueran equivalentes.
6. **Correlación ≠ causalidad.** La importancia de variables describe asociación, no causa.
7. **Respeta los términos de uso** de la fuente. No evadas autenticación, CAPTCHA ni bloqueos.
   Si el sitio responde 403/429: **detente**, no insistas (ver sección 17).
8. **No declares el proyecto terminado** hasta completar la auditoría de la rúbrica y verificar entregables.
9. **Integridad académica:** ayuda a construir, explicar y defender el trabajo; no sustituyas la
   comprensión del estudiante. No atribuyas a una persona trabajo que no hizo.
10. No guardes ni pegues contraseñas, tokens o datos personales sensibles en ningún archivo.

---

## 3. Protocolo de APROBACIÓN entre fases (obligatorio)

Trabajas **una fase a la vez**. Para pasar a la siguiente, el estudiante debe escribir una aprobación
explícita (por ejemplo: `APROBADO FASE X`). Un "ok" ambiguo o el silencio **no** cuentan.

**Ciclo por fase:**
1. Presenta propósito, requisito que cumple, código/acciones y cómo comprobarlas.
2. **Pide los resultados reales** (salida de consola, archivos, figuras). No continúes sin ellos
   cuando sean necesarios.
3. Analiza esa evidencia; detecta errores, riesgos y límites; propón correcciones y vuelve a verificar.
4. Entrega un **mini-informe de cierre de fase** con estado por requisito:
   `CUMPLE` / `PARCIAL` / `NO CUMPLE` / `PENDIENTE DE EVIDENCIA`
   (no marques CUMPLE solo porque el código existe: debe haber evidencia de ejecución).
5. **Detente y pregunta:** "¿Apruebas la Fase X para continuar con la Fase Y?" y espera.

Si el estudiante pide "adelantar todo", puedes **preparar borradores** de fases posteriores (código,
esqueletos de documentos), pero márcalos como `PROPUESTA (no aprobada)` y **no los des por buenos**
hasta que existan resultados reales y aprobación.

**Formato de cada avance:**

| Apartado | Contenido |
|---|---|
| Estado | Fase actual y estado: propuesta / en desarrollo / ejecutada / verificada |
| Objetivo | Qué resuelve esta fase |
| Requisito académico | Punto exacto de la guía/rúbrica |
| Decisión técnica | Herramienta o método elegido y por qué |
| Implementación | Código completo, ordenado, listo para probar |
| Explicación | Qué hace y cómo defenderlo en el video |
| Validación | Pruebas, salidas reales, criterios de aceptación |
| Riesgos | Errores conocidos, limitaciones, acciones correctivas |
| Evidencia | Archivos, gráficos, métricas, capturas a conservar |
| Pendientes | Qué falta y qué debe aportar el estudiante |

---

## 4. Contexto institucional (fuente: guía del proyecto y rúbrica)

**Asignatura:** Ciencia de Datos con Python. **Proyecto:** solución integral de Ciencia de Datos sobre una
problemática real de **tema libre**; equipo de 1 a 3 (aquí: **2**). Debe demostrar el ciclo de vida de los
datos y programación estructurada en Python.

### Requisitos obligatorios por fase

| Fase | Requisito |
|---|---|
| I. Extracción | Web scraping **automatizado** de un portal web **real**; pandas; variables dinámicas; ciclo `for`/`while` que recorra páginas, categorías, fechas o regiones; consolidación en lista o diccionario. **No** sustituir por un CSV estático (p. ej. Kaggle). |
| II. Limpieza | `pd.concat()`; tratamiento explícito de **duplicados y NaN**; filtros con condiciones múltiples con `&` y `\|` agrupadas con paréntesis; **conversión explícita** de texto a tipos numéricos. |
| III. Exploración | Visualizaciones estructuradas e **interpretación** de patrones, distribuciones y relaciones entre variables independientes y la variable objetivo. |
| IV. ML | scikit-learn; clasificación o regresión; train/test; **modelo base**; **GridSearchCV**; validación cruzada de **mínimo 5 folds**; comparación del score **antes y después**. |

### Entregables
- **PDF institucional** con los **enlaces** al código fuente y al video, claramente visibles.
- **Código:** repositorio **público de GitHub** (o Colab público con lectura); ordenado, modular, comentado.
- **Video:** enlace directo de **YouTube** (público u oculto). **No** se acepta Drive ni descarga local.
  **Máximo 15 min.** Todos los integrantes participan: cámara encendida al inicio, se presentan y explican
  activamente una sección técnica.

### Rúbrica

| Criterio | Peso | Excelente (4.5–5.0) |
|---|---|---|
| Web scraping dinámico | 20 % | Pandas y bucles eficientes sobre URLs dinámicas e iterativas; consolidación limpia |
| Limpieza y manipulación | 20 % | Concatenación masiva; nulos tratados con justificación; tipos formateados; filtros múltiples bien agrupados |
| Modelado y optimización | 25 % | Train/test correcto; GridSearchCV exhaustivo; validación cruzada; mejora del score documentada |
| Código y entregables | 15 % | Enlace público y funcional; código modular, limpio, sin errores y comentado; PDF impecable |
| Sustentación en video | 20 % | Todos participan; explicaciones técnicas profundas, claras, fluidas y demostrativas |

### Restricción expresa
**Prohibido** usar exactamente los datasets del video del curso: **partidos de fútbol de Inglaterra/ligas** y
**características de laptops**. Su uso implica **cero** en los criterios técnicos.
(El proyecto actual usa baloncesto NBA, que no es ninguno de los dos; falta confirmar con el docente, ver sección 11.)

---

## 5. El proyecto

- **Título provisional:** ¿Qué estadísticas de juego explican que un equipo de la NBA llegue a playoffs?
- **Tipo de problema:** clasificación binaria. **Variable objetivo:** `playoffs` (1 = clasificó, 0 = no).
- **Fuente:** Basketball-Reference, una página por temporada: `https://www.basketball-reference.com/leagues/NBA_{año}.html`
  (año = año de cierre de la temporada; 2026 = temporada 2025-26).
- **Alcance:** temporadas 2000 a 2026 (27 temporadas), un registro por equipo-temporada.
- **Equipo:** 2 integrantes: Mauricio Villafañe y Santiago de la Hoz. Universidad Americana de Barranquilla, Facultad de Ingeniería de Sistemas; docente Edgar Morillo Vergel; 7.º semestre.
- **Entorno:** Windows, **VS Code**, Python local (ver sección 17). Entrega de código en **GitHub público**.
- **Fecha límite:** **jueves 19 de noviembre de 2026**. El docente no puso condiciones extra.
- **Reparto propuesto:** Persona 1 = Fases I y II (scraping y limpieza); Persona 2 = Fases III y IV
  (exploración y ML). Ambos participan en video, PDF y README.

---

## 6. Estado actual por fase (a la fecha de este archivo)

| Fase | Estado | Evidencia real (B) |
|---|---|---|
| Etapa 1–2 (viabilidad y diseño) | **Aprobada** por el estudiante (eligió la opción A: NBA) | — |
| I. Scraping | **Ejecutada y verificada** | 27/27 temporadas OK; 29 equipos en 2000–2004 y 30 desde 2005; 805 filas por tabla; log en `outputs/logs/scrape_log.csv` |
| II. Limpieza | **Ejecutada y verificada** | Ver sección 8 |
| III. Exploración | **Ejecutada y verificada** (16 variables); figuras revisadas e interpretadas | `outputs_corrida2_16vars/` (11 figuras, 14 CSV, log); informe `docs/FASE_III_EDA_16VARS.md` |
| IV. ML | **Ejecutada y verificada** (16 variables); histórica de 19 variables conservada | `outputs_corrida2_16vars_fase4/` (10 figuras, tablas, logs, manifiesto); informe `docs/FASE_IV_MODELADO_16VARS.md` |
| QA / auditoría de rúbrica | Parcial | `docs/MATRIZ_RUBRICA.md` (criterios técnicos con evidencia; repo, PDF y video pendientes) |
| PDF | Pendiente (esqueleto en sección 13) | — |
| Repo GitHub | Pendiente | — |
| Video | Pendiente (guion en sección 14) | — |

**Siguiente paso inmediato:** Fase IV ejecutada y verificada; el proyecto avanza a la revisión
de entrega (repositorio, PDF y video).

---

## 7. Inventario de archivos (carpeta raíz del proyecto, estructura plana)

Todos los scripts se ejecutan **desde la carpeta raíz** (usan rutas relativas) y se encadenan en orden.

| Archivo | Fase | Qué hace | Salidas |
|---|---|---|---|
| `scraping.py` | I | Bucle `for year in range(2000, 2027)`; descarga con `requests` (pausa 4 s, reintentos, **caché local**); lee tablas con `pd.read_html` (incluye tablas dentro de comentarios HTML); extrae **Advanced Stats** y **Per Game Stats** por equipo; valida título de la página y nº de equipos; guarda fragmentos como **texto** | `data/raw/html/NBA_AAAA.html`, `data/raw/fragments/{advanced,per_game}_AAAA.csv`, `outputs/logs/scrape_log.csv` |
| `limpieza.py` | II | `pd.concat`, duplicados, consistencia entre tablas, conversión numérica auditada, unión, nulos, filtros compuestos, verificaciones | `data/raw/*_raw_concat.csv`, `data/processed/nba_teams_clean.csv`, `outputs/metrics/limpieza_resumen.csv` |
| `exploracion.py` | III | Variables relativas por temporada (`_rel`), 11 figuras, correlaciones, pares redundantes, atípicos, quintiles, calidad | `outputs_corrida2_16vars/figures/*_16vars.png`, `outputs_corrida2_16vars/metrics/eda_*_16vars.csv` |
| `modelado.py` | IV | Protocolo temporal (≤2019 / >2019) con `StratifiedGroupKFold`, línea base, base vs `GridSearchCV` (5 folds), test único, importancia por permutación, VIF y sensibilidad | `outputs_corrida2_16vars_fase4/figures/*_16vars.png`, `outputs_corrida2_16vars_fase4/metrics/*_16vars.*` |
| `README.md`, `requirements.txt` | - | Documentación y dependencias | - |

**Constantes y decisiones clave en el código**
- `scraping.py`: `FIRST_SEASON=2000`, `LAST_SEASON=2026`, `SLEEP_SECONDS=4`. `HEADERS` lleva un User-Agent
  identificable con el usuario de GitHub `ctlucifer1504-bit`.
- `limpieza.py`: clave única `["season","Team"]`; `ADV_NUM` y `PG_NUM` listan columnas a convertir.
- `exploracion.py`: `FOUR_FACTORS` (8 variables de cuatro factores) y `OTHER_FEATURES`; `FEATURES = FOUR_FACTORS + OTHER_FEATURES`.
  `add_relative_features()` crea `col_rel = valor − promedio de la liga en esa temporada`.
- `modelado.py`: `RANDOM_STATE=42`, `TEST_SIZE=0.20`, `N_FOLDS=5`, `REFIT="f1"`, `TEMPORAL_CUTOFF=2019`.
  `MODELS` = LogisticRegression (grilla en `C`) y RandomForest (grilla de 48 combinaciones).
  Pipeline = `SimpleImputer(median)` → `StandardScaler` → modelo. Importa `FEATURES, TARGET, add_relative_features` de `exploracion.py`.

---

## 8. Datos: hechos verificados y particularidades

**Hechos observados (B):**
- Tras `pd.concat`: **805 filas** (advanced: 32 columnas; per_game: 29). Sin duplicados (ni exactos ni por clave).
- Nulos solo en `Attend.` y `Attend./G`: **4 filas** cada una. *Hipótesis (C), NO verificada:* temporadas de pandemia.
  Esas columnas **no entran al modelo**.
- Tablas consistentes entre sí: 0 equipos en una sola tabla; 0 desacuerdos en `playoffs`.
- Conversión numérica sin valores inválidos (0 NaN nuevos).
- **Variable objetivo:** 432 clasificados (53,7 %) y 373 no (46,3 %). 432 = 16 × 27 exactamente → el asterisco
  del sitio marca bien a los 16 clasificados por temporada (incluida la "burbuja" 2020 y el play-in desde 2021).
- **Filtros compuestos (B):**
  1. `(playoffs==1) & ((win_pct<0.5) | (NRtg<0))` → **53** equipos clasificaron con récord perdedor o diferencial negativo.
  2. `(playoffs==0) & ((ORtg>=q75 de su temporada) | (DRtg<=q25 de su temporada))` → **40** equipos no clasificaron pese a
     buen ataque o buena defensa **dentro de su temporada**. (Primera versión usaba cuantiles globales y medía la época, no la calidad; ya corregido.)

**Particularidades del sitio (A/B):**
- Una sola página por temporada contiene Advanced y Per Game; el asterisco en el nombre indica playoffs.
- Algunas tablas están dentro de **comentarios HTML** (se descomentan antes de `read_html`).
- Encabezado de dos niveles en Advanced: los cuatro factores aparecen repetidos para ataque y defensa;
  se renombran con prefijos `off_` y `def_`. `NRtg` viene como texto con signo (`+12.8`).
- Límite del sitio (A): ~**20 peticiones/minuto**; superarlo puede bloquear la sesión hasta un día.
  El script usa 4 s de pausa (~15/min) y caché.

**Particularidades de la liga a tener presentes (C):**
- Temporadas acortadas: 2012 (cierre patronal) y 2020 (pandemia) → usar tasas por partido, no totales.
- Cambios de nombre/ciudad de franquicias (Seattle, New Jersey, Charlotte/New Orleans…): `Team` es identificador, no predictor.
- Fuerte **deriva de época**: 3PAr 0,167→0,415; Pace 93,1→99,4; ORtg 104,1→115,8 (2000→2026).

---

## 9. Decisiones metodológicas y justificación (defiéndelas en el video)

1. **Variables relativas a la temporada** (`_rel`): comparar 2000 con 2026 en valores absolutos mide la época.
   *Limitación honesta:* el promedio de la temporada incluye equipos del test (no usa la variable objetivo, por lo que
   el riesgo es bajo, pero es una transformación transductiva; declararlo).
2. **Exclusión por fuga de datos** (revelan el resultado): `W, L, PW, PL, MOV, SOS, SRS, NRtg, win_pct, Rk`.
   `ORtg` y `DRtg` también se excluyen del análisis principal (casi equivalen al margen de puntos); se evalúan solo
   como **sensibilidad**. `Attend.`/`Attend./G` se excluyen por **causalidad inversa** (el éxito atrae público).
   `G` y `MP` no son predictores relevantes.
3. **Nulos:** no se imputan en Fase II; si hubiera nulos en predictores se imputan con la **mediana aprendida solo con
   el entrenamiento** dentro del Pipeline. (Hoy los predictores no tienen nulos.)
4. **Split:** 80/20 **estratificado**, `random_state=42`, **antes** de ajustar nada.
5. **CV:** `StratifiedKFold(5, shuffle=True, random_state=42)`; **el mismo objeto** para modelo base y GridSearchCV
   → comparación sobre folds idénticos.
6. **Métricas:** accuracy (clases equilibradas) + precision, recall, F1, ROC-AUC y matriz de confusión.
   Línea base trivial (clase mayoritaria) = referencia mínima.
7. **Selección del modelo final solo por CV**; test se evalúa **después**, sin tomar decisiones con él.
   `best_score_` es algo optimista (máximo entre muchas combinaciones).
8. **Robustez temporal** (entrenar ≤2019, probar >2019) y **sensibilidad** con ORtg/DRtg: análisis complementarios,
   **no comparables** directamente con el test principal.

---

## 10. Resultados observados (B) — Corrida 1 histórica (19 variables)

> **HISTÓRICO.** Los resultados de esta sección corresponden a la corrida de 19 variables.
> La corrida actual de 16 variables está en `docs/FASE_III_EDA_16VARS.md` y en
> `outputs_corrida2_16vars/`. No mezclar ambas.

**Exploración (correlación de predictores relativos con `playoffs`)**
`def_eFG% −0,582` · `off_eFG% +0,511` · `Age +0,452` · `3P% +0,349` · `def_DRB% +0,317` · `off_TOV% −0,275` ·
`AST +0,250` · `TRB +0,211` · `PF −0,190` · `def_FT/FGA −0,191` · `off_FT/FGA +0,186` · `3PAr +0,185` · `STL +0,175` ·
`BLK +0,163` · `def_TOV% +0,146` · `FTr +0,142` · `FT% +0,139` · `Pace −0,124` · `off_ORB% −0,006`.

**Pares redundantes (|r| ≥ 0,7):** `FTr`–`off_FT/FGA` 0,929 · `def_FT/FGA`–`PF` 0,893 · `def_TOV%`–`STL` 0,821 · `off_eFG%`–`3P%` 0,709.
**Atípicos (1,5×IQR):** pocos (≤1,9 % por variable; máximo en `3P%`, 15 casos).

**Modelado (accuracy en CV de 5 folds sobre train; media ± desv.)**

| Modelo | Base | Optimizado (GridSearchCV) | Mejores parámetros |
|---|---|---|---|
| Línea base trivial | 0,537 | — | — |
| LogisticRegression | 0,896 ± 0,026 | 0,899 ± 0,025 | `C=1000` (**extremo de la grilla**) |
| RandomForest | 0,871 ± 0,017 | 0,871 ± 0,017 | `max_depth=8, max_features='sqrt', min_samples_leaf=5, n_estimators=400` |

Mejora por optimización: logística **+0,003**, random forest **+0,000** → ambas **dentro de 1 desviación entre folds**
(no significativa). Modelo final elegido por CV: **LogisticRegression**.

**Test (161 equipos-temporada)**

| Modelo | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---|---|---|---|---|
| Línea base trivial | 0,534 | 0,534 | 1,000 | 0,696 | — |
| LogisticRegression (base) | 0,870 | 0,892 | 0,860 | 0,876 | 0,949 |
| LogisticRegression (optimizado) | 0,863 | 0,890 | 0,849 | 0,869 | 0,944 |

Con 161 muestras, 1 acierto ≈ 0,6 puntos: la diferencia base vs optimizado es **un solo equipo**.

**Importancia por permutación (test):** `FTr 0,215`, `def_eFG% 0,152`, `off_eFG% 0,077`, `off_FT/FGA 0,075`, `def_TOV% 0,071`, `FT% 0,047`…
**Sensibilidad (CV):** sin ratings 0,899; con ORtg/DRtg 0,901 (casi sin cambio).
**Robustez temporal** (train 595 / test 210): accuracy 0,857; precision 0,825; recall 0,929; F1 0,874; AUC 0,943.
Precision < recall: el modelo tiende a predecir "clasifica" de más (no conoce el cupo fijo de 16 por temporada).

**Lectura honesta (C):** el problema es casi lineal y los predictores ya son informativos; GridSearchCV no aporta mejora
significativa. Se reporta así. **No** presentar una mejora que no existe.

---

## 11. Problemas abiertos y cambios pendientes (por prioridad)

**ALTO — Importancia de `FTr` engañosa.** Sale como la más importante por permutación (0,215) pese a correlación de solo
0,14 con el objetivo. Probable efecto de colinealidad con `off_FT/FGA` (r = 0,93). **No afirmar** que `FTr` es la variable
más importante. Acción (decidida con la tabla de la Fase III, no con el test): quitar una variable de cada par con |r| ≥ 0,8.

> **Estado 2026-11-18:** los cambios de `exploracion.py` (16 variables) y de `modelado.py`
> (protocolo temporal, métricas ampliadas, anti-fuga) ya se aplicaron y ejecutaron. La Fase IV
> está verificada en `outputs_corrida2_16vars_fase4/`. Los puntos de esta sección se conservan
> como registro histórico.
>
> **Resultado de la corrida 2 (B):** logística optimizada (`C=0.1`), CV F1 0,912 ± 0,009;
> test temporal F1 0,880, accuracy 0,862, ROC-AUC 0,942. La mejora de `GridSearchCV` en CV
> (+0,004) **no se replicó en test**. `def_eFG%` y `def_TOV%` dominan la importancia por
> permutación. VIF > 10 en `TRB` (20,9), `Pace` (10,7) y `off_ORB%` (10,4).
>
> **Cambios aplicados en `modelado.py`:** salida aislada en `outputs_corrida2_16vars_fase4/`;
> protocolo temporal principal con `StratifiedGroupKFold`; umbral elegido en validación
> interna; ningún modelo, hiperparámetro ni umbral elegido con test; importancia por permutación fuera del test; VIF y sensibilidad;
> logging, manifiesto y métricas ampliadas.

**Cambios aplicados (registro):**
- En `exploracion.py`: `OTHER_FEATURES = ["Age", "Pace", "3PAr", "3P%", "FT%", "AST", "BLK", "TRB"]`
  (se retiran `FTr`, `PF`, `STL`).
- En `modelado.py`: grilla de la logística `"clf__C": [0.001, 0.01, 0.1, 1, 10, 100, 1000, 10000]` (el óptimo estaba en el borde).
- Antes de re-ejecutar, **conservar la corrida 1**: copiar `outputs` a `outputs_corrida1_19vars`.
- Reportar **ambas corridas** en el PDF (19 variables y la final con 16) y explicar el motivo.
- El par `off_eFG%`–`3P%` (0,709) se deja a la vista: se mantiene `3P%` y se discute la redundancia.

**MEDIO**
- Interpretar las figuras reales (02, 04, 05, 06, 09); el agente aún no las ha visto. No describir gráficos que no se hayan visto.
- Verificar la hipótesis de los 4 nulos de asistencia:
  `d = pd.read_csv("data/processed/nba_teams_clean.csv"); print(d.loc[d["Attend."].isna(), ["season","Team"]])`.
- Leer completa la **cláusula 5 de los términos de uso** de Basketball-Reference y documentar la conclusión (no se pudo leer completa).
- Confirmar con el docente, por escrito, que un deporte distinto al fútbol es válido (la guía habla de "ligas").
- El correo de contacto del `User-Agent` está configurado en `HEADERS` de `scraping.py`.

**BAJO**
- (Opcional) cuaderno `notebooks/proyecto_final.ipynb` que importe los módulos y muestre el flujo y las salidas.
- (Opcional) reorganizar en `src/`; **no hacerlo ahora** (rutas relativas e imports entre scripts pueden romperse a un día de la entrega).

---

## 12. Plan de trabajo hasta la entrega

| Cuándo | Qué | Responsable sugerido |
|---|---|---|
| **Miércoles 18 nov** (mañana) | Aprobar y ejecutar corrida 2 (Fase III/IV); pasar salidas y figuras 02, 04, 05, 06, 09 al agente | P2 |
| Miércoles 18 (mediodía) | Interpretar gráficos y resultados; QA contra rúbrica; completar datos de portada | P2 + agente |
| Miércoles 18 (tarde) | Redactar PDF; subir repo a GitHub (público); completar README | P1 + P2 |
| Miércoles 18 (noche) | Ensayar el video (cronometrar) | Ambos |
| **Jueves 19 nov** (mañana) | Grabar video (≤ 15 min), subir a YouTube (público u oculto), insertar enlaces en el PDF, verificar enlaces | Ambos |
| Jueves 19 | **Entregar** | Ambos |

Si hay riesgo de no llegar, prioriza en este orden: (1) código ejecutado con evidencia, (2) PDF con enlaces, (3) video con ambos participando.

---

## 13. PDF final: estructura (usar solo datos reales)

Portada (título, asignatura, **integrantes**, **docente**, **institución**, fecha) · Resumen · Introducción, problema,
justificación y objetivos · Fuente y scraping (portal, condiciones de uso, recorrido iterativo, volumen: 27 temporadas, 805 filas) ·
Limpieza (calidad inicial, decisiones, resultado) · Exploración (figuras + interpretación) · Modelado (objetivo, predictores,
partición, modelo base, GridSearchCV, CV de 5 folds) · Resultados y discusión (métricas reales, antes/después, **mejora no
significativa**, robustez, limitaciones) · Conclusiones y recomendaciones · Referencias · **Enlaces visibles al GitHub y al video de YouTube**.

**Limitaciones que deben aparecer:** una sola fuente y sesgo del portal; cobertura 2000–2026; cambios de formato (play-in desde 2021);
temporadas acortadas 2012 y 2020; asociación ≠ causalidad; variables relativas usan promedio de temporada que incluye test;
`best_score_` optimista; tamaño de test pequeño (161); colinealidad entre predictores; posible cambio de estructura de la web.

**Referencias:** distingue *fuente de datos* (Basketball-Reference) de *referencias metodológicas* (documentación de pandas y
scikit-learn). No inventes bibliografía; cita solo lo que se haya consultado de verdad.

---

## 14. Video de sustentación (≤ 15 min; apuntar a 14)

| Tiempo | Quién | Contenido | En pantalla |
|---|---|---|---|
| 0:00–1:00 | Ambos | Cámara encendida; se presentan; título y problema | Ambos visibles |
| 1:00–3:00 | P1 | Pregunta, objetivos, fuente y por qué NBA | Portal + pregunta |
| 3:00–5:30 | P1 | Scraping: bucle por temporada, pausas, caché, log, comentarios HTML | Código de `scraping.py`, `scrape_log.csv` |
| 5:30–7:30 | P1 | `pd.concat`, nulos, duplicados, tipos, filtro compuesto con `&`/`\|` | Salida de `limpieza.py` |
| 7:30–9:30 | P2 | Gráficos: deriva de época, boxplots, correlaciones, redundancia | Figuras 02, 04, 05, 06 |
| 9:30–12:30 | P2 | Split, línea base, modelo base, GridSearchCV (5 folds), antes/después, fuga de datos | Salida de `modelado.py` |
| 12:30–13:30 | P2 | Resultados en test, matriz de confusión, importancia | Figuras 08, 09 |
| 13:30–14:00 | P1 | Limitaciones y conclusiones | — |
| 14:00 | Ambos | Cierre y acceso al repositorio | GitHub |

Consejos: demostrar **ejecución real**, no solo diapositivas; cada uno explica con sus palabras lo que presenta; mencionar
explícitamente que la optimización no mejoró de forma significativa y por qué; cronometrar un ensayo.
Preguntas probables del docente: ¿por qué variables relativas? ¿qué es fuga de datos y cómo se evitó? ¿por qué se excluyeron
W/L/NRtg? ¿por qué no mejoró GridSearchCV? ¿por qué elegir logística? ¿qué significa la importancia por permutación?
¿es legal/ético el scraping? ¿qué pasaría si cambia la web?

---

## 15. Repositorio y entregables

**Subir a GitHub público:** scripts (`scraping.py`, `limpieza.py`, `exploracion.py`, `modelado.py`), `README.md`, `requirements.txt`,
`docs/`, `outputs_corrida2_16vars/` (Fase III actual), `outputs/` y `outputs_corrida1_19vars/` (corrida histórica, claramente
etiquetada), y `data/processed`. Sobre `data/raw/html` (páginas completas del sitio):
**decidir tras leer los términos de uso**; alternativa segura: no subirlas y dejar la instrucción de re-ejecutar el scraping.
`requirements.txt`: idealmente con versiones exactas (`pip freeze`). Versiones observadas en la máquina del estudiante:
scikit-learn 1.9.1, pandas 3.1.1, numpy 2.5.5, matplotlib 3.11.2, Python 3.15.2.
Antes de entregar: abrir el enlace del repo en una ventana de incógnito y comprobar que es público y funciona.
El enlace de YouTube también debe abrirse sin iniciar sesión.

---

## 16. Checklist maestro y estado actual

| Requisito | Estado | Nota |
|---|---|---|
| Tema libre, pertinente, no prohibido | CUMPLE (por confirmar con docente) | NBA ≠ fútbol inglés / laptops |
| Problema, pregunta y objetivos definidos | PARCIAL | Falta redactar formalmente en el PDF |
| Fuente real y condiciones de uso revisadas | PARCIAL | Cláusula 5 sin leer completa |
| Scraping con pandas / tablas HTML | CUMPLE | Log real 27/27 |
| Variable dinámica + bucle `for` | CUMPLE | `year` recorre 2000–2026 |
| Consolidación en lista/dict y DataFrames | CUMPLE | `fragments` + CSV |
| `pd.concat()` | CUMPLE | Salida de `limpieza.py` |
| Duplicados y NaN tratados con justificación | CUMPLE | 0 duplicados; 4 nulos en asistencia (excluida) |
| Filtro con `&`, `\|` y paréntesis | CUMPLE | Dos filtros ejecutados |
| Conversión explícita de tipos | CUMPLE | Auditada, 0 NaN nuevos |
| Gráficos con título, ejes e interpretación | CUMPLE | 11 figuras y 14 tablas; interpretación en `docs/FASE_III_EDA_16VARS.md` |
| Objetivo y predictores justificados | CUMPLE | 16 predictores justificados en `docs/FASE_IV_MODELADO_16VARS.md` |
| Train/test sin fuga | CUMPLE | Corrida 2 de 16 variables; ver `docs/FASE_IV_MODELADO_16VARS.md` §2.2 |
| Modelo base documentado | CUMPLE | Corrida 2 de 16 variables |
| GridSearchCV explícito, = 5 folds | CUMPLE | 5 folds; grilla documentada en `modelado.py` |
| Comparación antes/después | CUMPLE | Mejora no significativa, reportada |
| Evaluación final en test | CUMPLE | Corrida 2 de 16 variables; umbral titular 0,50 |
| Código modular, comentado, reproducible | PARCIAL | Falta README completo y repo público |
| Repo público y funcional | PENDIENTE DE EVIDENCIA | |
| PDF con enlaces a código y video | PENDIENTE DE EVIDENCIA | |
| Video ≤ 15 min, ambos participan | PENDIENTE DE EVIDENCIA | |
| Conclusiones con limitaciones | PENDIENTE | |

---

## 17. Entorno y comandos (Windows)

- Python del proyecto: `.\.venv\Scripts\python.exe` (3.15.2). Ejemplo de Python global en Windows: `C:\Python315\python.exe`.
- **Las librerías deben estar instaladas en el intérprete que ejecuta el script.** Un `.venv` nuevo está vacío;
  instalar dentro de él:
  `& '.\.venv\Scripts\python.exe' -m pip install pandas requests lxml matplotlib scikit-learn`
- Ejecutar siempre **desde la carpeta raíz del proyecto**, en este orden:
  ```powershell
  python scraping.py      # solo si faltan datos; usa caché si ya existen las páginas
  python limpieza.py
  python exploracion.py
  python modelado.py      # tarda varios minutos (búsqueda en rejilla)
  ```
  (usar la ruta completa del `python.exe` del `.venv` o el global según corresponda; no mezclar).
- Si PowerShell bloquea `Activate.ps1`: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned`.
- El aviso de pip "scripts not on PATH" es inofensivo.

**Si el sitio responde 403/429:** el script se detiene a propósito. No insistir. Alternativa legítima: abrir cada página en el
navegador, guardarla como `data/raw/html/NBA_AAAA.html` y re-ejecutar (usa los archivos sin hacer peticiones).

**Errores conocidos y solución**
| Síntoma | Causa | Solución |
|---|---|---|
| `ModuleNotFoundError` | Librería no instalada en ese intérprete | Instalar en el mismo intérprete |
| `FileNotFoundError` en `data/...` | Ejecutado fuera de la raíz | `cd` a la carpeta del proyecto |
| `[AVISO] columnas esperadas que no existen` (limpieza) | Cambió el formato del sitio | Revisar nombres de columnas del fragmento |
| `KeyError: Faltan columnas` (exploración) | CSV limpio sin alguna variable | Re-ejecutar `limpieza.py` |
| 403/429 en scraping | Límite del sitio / Cloudflare | Ver arriba; no insistir |

---

## 18. Qué NO debes hacer

- No reescribir el proyecto ni cambiar de tema/fuente sin aprobación explícita y sin explicar el motivo.
- No ejecutar ni proponer scraping agresivo, rotación de IP, suplantación de navegador ni evasión de bloqueos.
- No usar `W, L, PW, PL, MOV, SOS, SRS, NRtg, win_pct, Rk` como predictores. No usar `Attend.` como predictor.
- No usar el conjunto de test para elegir hiperparámetros, modelos o variables.
- No imputar ni escalar fuera del Pipeline.
- No interpretar figuras que no hayas visto; no inventar salidas de consola.
- No redactar el PDF con nombres, docente, institución, enlaces o resultados que el estudiante no haya aportado.
- No mover a `src/` ni refactorizar masivamente a un día de la entrega.
- No avanzar de fase sin la aprobación explícita descrita en la sección 3.

---

## 19. Primer mensaje que debes dar al cargar este archivo

1. Resume en 5 líneas lo que entendiste (problema, fuente, estado, siguiente paso).
2. Lista lo que **no** puedes confirmar (p. ej., figuras no vistas, corrida 2 no ejecutada).
3. Propón **solo** el siguiente paso inmediato (sección 11, prioridad ALTO) y pide **aprobación explícita** antes de modificar archivos.
4. Pregunta únicamente por los datos que faltan: nombres de los integrantes, asignatura, docente, institución, correo para `HEADERS`.
