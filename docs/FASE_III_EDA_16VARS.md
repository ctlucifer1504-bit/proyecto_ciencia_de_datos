# Fase III — Análisis Exploratorio de Datos (EDA)

**Datos: Sports Reference LLC / Basketball-Reference.com.** El CSV de entrada no se
publica; se regenera con `data/README.md`.

**Proyecto:** ¿Qué estadísticas de la NBA explican que un equipo llegue a playoffs?  
**Corrida documentada:** `corrida2_16vars` — **16 predictores**  
**Fecha de ejecución:** 2026-11-18, 13:02:35–13:02:44 (hora local)  
**Entrada:** `data/processed/nba_teams_clean.csv`  
**SHA256 de la entrada:** `c04704d9ecdd511b24bd81b1aef73250082e02bd1f63a501eed900f1f9ea3ea9`  
**Salida:** `outputs_corrida2_16vars/`  
**Estado:** ejecutada y verificada. La Fase IV se ejecutó después (ver `docs/FASE_IV_MODELADO_16VARS.md`).

> **Actualización (2026-11-18, posterior a este informe).** Este documento se cerró antes de la Fase IV; por eso las frases «no se ejecutó la Fase IV» y «la Fase IV queda bloqueada» describen el estado de ese momento y se conservan como registro histórico. La Fase IV de 16 variables **sí se ejecutó** y sus resultados están en `outputs_corrida2_16vars_fase4/`.

> **Nota de trazabilidad.** La carpeta `outputs/` contiene resultados históricos de una corrida anterior de **19 predictores** (incluía `FTr`, `PF` y `STL`). Esos resultados están respaldados, sin cambios, en `outputs_corrida1_19vars/`. **No deben presentarse como resultados actuales.** La corrida actual de 16 predictores está únicamente en `outputs_corrida2_16vars/` y todos sus archivos llevan el sufijo `_16vars`.

---

## 1. Alcance, unidad de análisis y variable objetivo

- **Unidad de análisis:** equipo-temporada. Cada fila representa un equipo de la NBA en una temporada regular.
- **Cobertura:** 805 filas, 27 temporadas (2000–2026), 52 columnas originales. La temporada se identifica por el año de cierre: 2026 = temporada 2025-26.
- **Equipos por temporada:** 29 en 2000–2004 y 30 desde 2005. El salto es consistente con la incorporación de Charlotte Bobcats en 2004-05 (contexto externo, no verificado en esta fase); no se modificó nada en Fase II.
- **Variable objetivo:** `playoffs` (entero 0/1).
  - `1` = el equipo aparece marcado como clasificado a playoffs en Basketball-Reference para esa temporada.
  - `0` = no clasificó.
- **Balance:** 432 clasificados (53,66 %) y 373 no clasificados (46,34 %). No hay nulos en el objetivo y solo contiene los valores 0 y 1.

**Observación (B):** 16 equipos clasifican en cada una de las 27 temporadas. Por eso la tasa global es 55,17 % en 2000–2004 (16/29) y 53,33 % desde 2005 (16/30). No hay una tendencia temporal real en la proporción: cambia el denominador, no el número de clasificados. El play-in existe desde 2021 y cambia el camino de clasificación, pero el conteo de 16 se mantiene.

**Limitación:** el objetivo se toma del marcador de la fuente. La definición exacta de “clasificado” en temporadas con play-in no se verificó contra el reglamento de la NBA; se documenta como supuesto de la fuente.

---

## 2. Los 16 predictores actuales

La lista se mantiene exactamente como estaba en `exploracion.py` antes de esta fase. No se agregaron ni quitaron variables.

### 2.1 Cuatro factores (8)

| Variable | Unidad | Lectura |
|---|---|---|
| `off_eFG%` | proporción 0–1 | Eficiencia de tiro del equipo; mayor es mejor. |
| `off_TOV%` | % de posesiones | Pérdidas de balón; menor es mejor. |
| `off_ORB%` | % de rebotes ofensivos | Rebotes ofensivos capturados; mayor es mejor. |
| `off_FT/FGA` | razón | Tiros libres intentados por tiro de campo; mide agresividad y estilo. |
| `def_eFG%` | proporción 0–1 | Eficiencia de tiro permitida al rival; menor es mejor. |
| `def_TOV%` | % de posesiones | Pérdidas forzadas al rival; mayor es mejor. |
| `def_DRB%` | % de rebotes defensivos | Rebotes defensivos capturados; mayor es mejor. |
| `def_FT/FGA` | razón | Tiros libres permitidos por tiro de campo del rival; menor es mejor. |

### 2.2 Otras ocho variables (8)

| Variable | Unidad | Lectura |
|---|---|---|
| `Age` | años | Edad promedio ponderada por minutos. **No es una estadística de juego**; es una característica de la plantilla. |
| `Pace` | posesiones/48 min | Ritmo de juego. |
| `3PAr` | proporción | Proporción de tiros de tres sobre tiros de campo intentados. |
| `3P%` | proporción 0–1 | Porcentaje de acierto en triples. |
| `FT%` | proporción 0–1 | Porcentaje de acierto en tiros libres. |
| `AST` | por partido | Asistencias. |
| `BLK` | por partido | Tapones. |
| `TRB` | por partido | Rebotes totales. |

**Variables excluidas explícitamente:** `W`, `L`, `PW`, `PL`, `MOV`, `SOS`, `SRS`, `NRtg`, `win_pct`, `Rk`, `ORtg`, `DRtg`, `Attend.` y `Attend./G`. Las primeras revelan el resultado (fuga de datos); `ORtg`/`DRtg` se reservan para el análisis de sensibilidad de Fase IV; la asistencia se excluye por riesgo de causalidad inversa (el éxito atrae público) y porque tiene nulos.

### 2.3 Variables relativas

Para cada predictor se creó:

```text
x_rel = x - promedio de la liga en esa temporada
```

Esto evita comparar valores absolutos de épocas distintas. Por ejemplo, el promedio de liga de `3PAr` pasó de 0,167 en 2000 a 0,415 en 2026; comparar 0,30 absoluto en 2000 con 0,30 en 2026 mediría la época, no la calidad relativa del equipo.

**Limitación:** el promedio de temporada incluye a todos los equipos, también los del futuro conjunto de test. No usa la variable objetivo, por lo que el riesgo de fuga es bajo, pero es una transformación transductiva y debe declararse en el informe y en el video.

---

## 3. Calidad y validación de datos

| Comprobación | Resultado |
|---|---|
| Filas × columnas originales | 805 × 52 |
| Temporadas | 27 (2000–2026) |
| Duplicados por `(season, Team)` | 0 |
| Nulos en los 16 predictores | 0 |
| Infinitos en los 16 predictores | 0 |
| Predictores constantes | 0 |
| Nulos en `playoffs` | 0 |
| Valores de `playoffs` | solo 0 y 1 |
| Nulos en `Attend.` / `Attend./G` | 4 / 4 (contexto, excluidas) |

**Nulos de asistencia (B):** las 4 filas son de la temporada 2021: Miami Heat, Indiana Pacers, Sacramento Kings y Oklahoma City Thunder. **No se verificó la causa en la fuente**; por eso no se atribuye a la pandemia ni a otra razón. Esas columnas no son predictoras y no se imputan.

**Partidos por temporada (B; `G`, no es predictor):**

| Temporada | Partidos por equipo | Equipos con menos de 82 |
|---|---:|---:|
| 2012 | 66 | 30 |
| 2013 | 81–82 | 2 |
| 2020 | 64–75 | 30 |
| 2021 | 72 | 30 |
| Resto | 82 | 0 |

Esto corrige una formulación incompleta de la memoria previa del proyecto: no solo 2012 y 2020 fueron temporadas acortadas; **2021 también tuvo 72 partidos**, y en 2013 dos equipos jugaron 81. Por eso el EDA usa tasas y promedios por partido, no totales. La causa de cada caso no se investigó en esta fase.

**Decisión:** no se eliminó ni imputó ninguna observación. El EDA describe los datos recibidos de Fase II. Si se necesitara una corrección de limpieza, habría que documentarla y pedir autorización antes de tocar `limpieza.py`.

---

## 4. Estadísticas descriptivas

### 4.1 Predictores en unidades absolutas

Archivo completo: `outputs_corrida2_16vars/metrics/eda_descriptivas_absolutas_16vars.csv`.

| Variable | n | Media | Desv. est. | Mín. | Q1 | Mediana | Q3 | Máx. |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `off_eFG%` | 805 | 0,5061 | 0,0298 | 0,428 | 0,484 | 0,502 | 0,528 | 0,578 |
| `off_TOV%` | 805 | 13,2605 | 1,1200 | 9,9 | 12,5 | 13,3 | 14,0 | 18,0 |
| `off_ORB%` | 805 | 25,7513 | 3,1755 | 17,9 | 23,5 | 25,7 | 28,0 | 35,3 |
| `off_FT/FGA` | 805 | 0,2159 | 0,0278 | 0,143 | 0,196 | 0,214 | 0,233 | 0,303 |
| `def_eFG%` | 805 | 0,5061 | 0,0284 | 0,433 | 0,485 | 0,504 | 0,527 | 0,578 |
| `def_TOV%` | 805 | 13,2615 | 1,1853 | 10,3 | 12,4 | 13,2 | 14,1 | 16,5 |
| `def_DRB%` | 805 | 74,2338 | 2,6873 | 66,1 | 72,3 | 74,3 | 76,2 | 81,6 |
| `def_FT/FGA` | 805 | 0,2160 | 0,0285 | 0,145 | 0,195 | 0,214 | 0,233 | 0,340 |
| `Age` | 805 | 26,6323 | 1,7612 | 22,1 | 25,4 | 26,5 | 27,8 | 32,0 |
| `Pace` | 805 | 94,5621 | 4,0971 | 86,2 | 91,2 | 94,2 | 98,1 | 105,1 |
| `3PAr` | 805 | 0,2774 | 0,0958 | 0,095 | 0,201 | 0,257 | 0,359 | 0,536 |
| `3P%` | 805 | 0,3561 | 0,0188 | 0,278 | 0,344 | 0,356 | 0,369 | 0,416 |
| `FT%` | 805 | 0,7631 | 0,0300 | 0,660 | 0,745 | 0,765 | 0,783 | 0,839 |
| `AST` | 805 | 22,8396 | 2,5858 | 17,4 | 20,9 | 22,5 | 24,5 | 31,0 |
| `BLK` | 805 | 4,9017 | 0,7899 | 2,4 | 4,3 | 4,9 | 5,4 | 8,2 |
| `TRB` | 805 | 42,8639 | 2,0651 | 36,9 | 41,5 | 42,8 | 44,2 | 51,7 |

**Lectura:** los rangos son plausibles para la NBA. `3PAr` es la variable con mayor dispersión relativa (0,095–0,536), consistente con el cambio de estilo entre épocas. `Age` va de 22,1 a 32,0 años. No hay valores imposibles ni columnas constantes.

### 4.2 Predictores relativos

Archivo completo: `outputs_corrida2_16vars/metrics/eda_descriptivas_relativas_16vars.csv`.

Las medias son 0 por construcción (se resta el promedio de la temporada). Las desviaciones estándar relativas más grandes son `off_ORB%` (2,34), `Pace` (2,17), `AST` (1,79), `TRB` (1,72), `Age` (1,70) y `def_DRB%` (1,63). Las más pequeñas son `def_eFG%` (0,0151), `off_eFG%` (0,0176) y `3P%` (0,0180): una diferencia de 0,01 en eFG% ya es relevante.

### 4.3 Comparación entre clases

Archivo completo: `outputs_corrida2_16vars/metrics/eda_resumen_por_clase_16vars.csv`.  
La diferencia de medias es **clasificó menos no clasificó**, en unidades relativas. La `d` de Cohen estandariza esa diferencia por la desviación pooled. La tabla está ordenada por |d| descendente; el CSV completo conserva el orden por `d` con signo.

| Variable | Media no clasificó | Media clasificó | Diferencia | d de Cohen |
|---|---:|---:|---:|---:|
| `def_eFG%` | +0,0094 | −0,0081 | −0,0176 | **−1,435** |
| `off_eFG%` | −0,0097 | +0,0084 | +0,0181 | **+1,191** |
| `Age` | −0,8269 | +0,7140 | +1,5409 | **+1,014** |
| `3P%` | −0,0068 | +0,0058 | +0,0126 | **+0,747** |
| `def_DRB%` | −0,5561 | +0,4801 | +1,0362 | **+0,670** |
| `off_TOV%` | +0,2751 | −0,2375 | −0,5126 | −0,573 |
| `AST` | −0,4824 | +0,4165 | +0,8989 | +0,518 |
| `TRB` | −0,3893 | +0,3361 | +0,7254 | +0,432 |
| `def_FT/FGA` | +0,0045 | −0,0039 | −0,0084 | −0,390 |
| `off_FT/FGA` | −0,0043 | +0,0037 | +0,0079 | +0,380 |
| `3PAr` | −0,0083 | +0,0072 | +0,0156 | +0,376 |
| `BLK` | −0,1354 | +0,1169 | +0,2523 | +0,332 |
| `def_TOV%` | −0,1586 | +0,1370 | +0,2956 | +0,296 |
| `FT%` | −0,0041 | +0,0036 | +0,0077 | +0,281 |
| `Pace` | +0,2880 | −0,2487 | −0,5367 | −0,250 |
| `off_ORB%` | +0,0145 | −0,0125 | −0,0270 | −0,012 |

**Observación (B):** las mayores diferencias estandarizadas están en `def_eFG%`, `off_eFG%`, `Age`, `3P%` y `def_DRB%`. `off_ORB%` prácticamente no diferencia.  
**Interpretación (C):** la defensa eficiente (permitir malos tiros) y la eficiencia ofensiva son los ejes más asociados a clasificar. `Age` también separa, pero al no ser una estadística de juego podría estar actuando como proxy de madurez, continuidad o calidad de plantilla; no se debe leer como relación causal.  
**Limitación:** estas diferencias son descriptivas y no ajustan por otras variables ni por la temporada.

### 4.4 Correlación de cada predictor con el objetivo

Archivo completo: `outputs_corrida2_16vars/metrics/eda_correlacion_objetivo_16vars.csv`.  
Con un objetivo binario 0/1, el **r de Pearson es la correlación punto-biserial**. Se reporta también **Spearman** para captar asociación monótona.

| Variable | r Pearson | ρ Spearman |
|---|---:|---:|
| `off_eFG%` | **+0,511** | +0,522 |
| `Age` | **+0,452** | +0,455 |
| `3P%` | +0,349 | +0,358 |
| `def_DRB%` | +0,317 | +0,312 |
| `AST` | +0,250 | +0,241 |
| `TRB` | +0,211 | +0,212 |
| `off_FT/FGA` | +0,186 | +0,183 |
| `3PAr` | +0,185 | +0,180 |
| `BLK` | +0,164 | +0,157 |
| `def_TOV%` | +0,146 | +0,142 |
| `FT%` | +0,139 | +0,146 |
| `off_ORB%` | −0,006 | −0,009 |
| `Pace` | −0,124 | −0,129 |
| `def_FT/FGA` | −0,191 | −0,183 |
| `off_TOV%` | −0,275 | −0,277 |
| `def_eFG%` | **−0,582** | −0,594 |

**Observación (B):** `def_eFG%` es la asociación negativa más fuerte y `off_eFG%` la positiva más fuerte. `Age` ocupa el segundo lugar positivo. `off_ORB%` es prácticamente cero. Pearson y Spearman coinciden en signo y orden, así que la relación no parece depender de unos pocos valores extremos.  
**Limitación:** la correlación no ajusta por otras variables, no prueba causalidad y no detecta relaciones no lineales. Además, la variable objetivo está determinada por la clasificación final; cualquier estadística correlacionada con el margen de puntos tenderá a correlacionar con playoffs. El gráfico de quintiles (sección 5.8) ayuda a ver no linealidades.

---

## 5. Figuras y su interpretación

Todas las figuras están en `outputs_corrida2_16vars/figures/`. Se revisaron visualmente una por una.

### 5.1 `01_balance_clases_16vars.png` — balance del objetivo

**Observación (B):** 373 no clasificados (46,3 %) y 432 clasificados (53,7 %).  
**Interpretación:** el problema está razonablemente balanceado; la exactitud de una regla trivial que siempre prediga “clasificó” sería 53,7 %. Esa es la referencia mínima para la Fase IV. No se necesita remuestreo para el EDA.  
**Limitación:** el balance global oculta que el cupo es fijo por temporada (16); un modelo que ignore ese cupo puede predecir de más o de menos en una temporada concreta.

### 5.2 `02_evolucion_playoffs_por_temporada_16vars.png` — evolución temporal

**Observación (B):** 29 equipos y 16 clasificados en 2000–2004; 30 equipos y 16 clasificados desde 2005. La tasa pasa de 55,17 % a 53,33 % y se mantiene plana.  
**Interpretación:** no hay una tendencia temporal apreciable en la proporción de clasificados; el cambio es mecánico por el tamaño de la liga. La evolución temporal relevante está en las estadísticas de juego (figura 03), no en la tasa de playoffs.  
**Limitación:** el play-in (desde 2021) cambia cómo se clasifica, aunque no el número final de 16. La figura no distingue campeones de play-in ni ajusta por formato.

### 5.3 `03_deriva_por_epoca_16vars.png` — deriva de época

**Observación (B), promedios de liga 2000 → 2026:**
- `3PAr`: 0,167 → 0,415.
- `Pace`: 93,09 → 99,35.
- `ORtg`: 104,05 → 115,78 (solo contexto; no es predictor).
- `off_eFG%`: 0,478 → 0,546.
- `def_eFG%`: 0,478 → 0,546.
- `Age`: 27,79 → 26,10.

**Interpretación:** la liga tira más triples, juega algo más rápido y es más eficiente. Comparar valores absolutos entre 2000 y 2026 confundiría época con calidad; por eso el análisis principal usa `_rel`.  
**Limitación:** la transformación relativa elimina el nivel medio de la temporada, pero no otras diferencias de era (reglas, estilo, carga de partidos, play-in).

### 5.4 `04_histogramas_16vars.png` — distribución de los 16 predictores

**Observación (B):** la mayoría de las distribuciones relativas son aproximadamente simétricas alrededor de 0. Hay asimetría positiva moderada en `3PAr` (sesgo +0,47), `AST` (+0,45), `def_FT/FGA` (+0,34), `Pace` (+0,32) y `off_FT/FGA` (+0,32); `FT%` tiene sesgo negativo (−0,32). No se observan bimodalidades fuertes.  
**Interpretación:** no hay una variable con una distribución patológica que exija una transformación obligatoria. Las colas derechas de `3PAr`, `AST` y `off_FT/FGA` podrían reflejar equipos de estilo extremo, no errores.  
**Limitación:** los histogramas no ajustan por temporada; la versión `_rel` reduce la deriva, pero no elimina diferencias de dispersión entre eras.

### 5.5 `05_correlacion_con_objetivo_16vars.png` — correlación con el objetivo

**Observación (B):** reproduce la tabla 4.4. Las barras naranjas son asociaciones negativas y las azules positivas. Pearson y Spearman dan el mismo orden práctico.  
**Interpretación:** `def_eFG%` y `off_eFG%` son los candidatos más informativos; `Age`, `3P%` y `def_DRB%` siguen. `off_ORB%` no aporta señal lineal.  
**Limitación:** un coeficiente de correlación con un objetivo binario está acotado y depende del balance de clases; no mide importancia predictiva multivariada. La Fase IV deberá usar modelos y validación cruzada, no solo esta tabla.

### 5.6 `06_correlacion_entre_predictores_16vars.png` — redundancia

**Observación (B):** el único par con |r| ≥ 0,70 es `off_eFG%`–`3P%` (r = 0,709). También destaca `off_ORB%`–`TRB` (r = 0,53), por debajo del umbral. No hay pares con |r| ≥ 0,80.  
**Interpretación:** la multicolinealidad severa de la corrida de 19 variables (que incluía `FTr`, `PF`, `STL`) se redujo al quitar esas tres variables. `off_eFG%` y `3P%` miden conceptos relacionados pero no idénticos: eficiencia global de tiro vs acierto desde el triple. Se mantienen, pero conviene vigilar su efecto conjunto en la regresión logística de Fase IV.  
**Limitación:** Pearson solo detecta asociación lineal; no se calcularon VIF ni se evaluó multicolinealidad condicional. Los modelos de árboles son menos sensibles a esta redundancia que la regresión logística.

### 5.7 `07_dispersion_efg_ataque_defensa_16vars.png` — ataque vs defensa

Archivo de apoyo: `outputs_corrida2_16vars/metrics/eda_cuadrantes_efg_16vars.csv`.

| Cuadrante (relativo a la temporada) | n | Clasificados | Tasa |
|---|---:|---:|---:|
| Ataque > media; defensa mejor (`def_eFG%` < 0) | 239 | 216 | **90,38 %** |
| Ataque > media; defensa peor | 156 | 87 | 55,77 % |
| Ataque ≤ media; defensa mejor | 153 | 97 | 63,40 % |
| Ataque ≤ media; defensa peor | 257 | 32 | **12,45 %** |

**Observación (B):** el cuadrante con ataque y defensa mejores que la media concentra 239 equipos-temporada y el 90,4 % clasificó; el cuadrante opuesto concentra 257 y solo el 12,5 % clasificó.  
**Interpretación:** la combinación de ambas dimensiones separa mucho mejor que cualquiera por separado. La defensa parece marcar una diferencia especialmente grande en los extremos (63,4 % vs 12,5 %), pero el diseño es observacional y no permite atribuir causalidad.  
**Limitación:** los cuadrantes se definen con medianas de la temporada (0 relativo); un equipo puede estar apenas por encima o muy por encima y ambos caen en el mismo cuadrante. Los conteos son descriptivos, sin intervalos de confianza.

### 5.8 `08_tasa_playoffs_por_quintil_16vars.png` — forma de la relación

Archivo completo: `outputs_corrida2_16vars/metrics/eda_tasa_playoffs_por_quintil_16vars.csv`.  
Cada quintil se calcula **dentro de su temporada** (Q1 = 20 % más bajo de esa temporada; Q5 = 20 % más alto).

| Variable | Q1 | Q2 | Q3 | Q4 | Q5 | Patrón |
|---|---:|---:|---:|---:|---:|---|
| `off_eFG%` | 14,8 % | 40,4 % | 50,3 % | 70,5 % | 90,1 % | Monótono creciente |
| `def_eFG%` | 91,8 % | 76,4 % | 57,7 % | 34,4 % | 11,8 % | Monótono decreciente (menor es mejor) |
| `Age` | 21,7 % | 40,0 % | 49,4 % | 67,1 % | 88,0 % | Monótono creciente |
| `3P%` | 28,6 % | 43,5 % | 49,4 % | 64,6 % | 80,1 % | Monótono creciente |
| `def_DRB%` | 35,9 % | 41,7 % | 47,5 % | 65,8 % | 76,0 % | Creciente |
| `off_TOV%` | 69,3 % | 66,7 % | 52,0 % | 51,2 % | 31,0 % | Decreciente (más pérdidas, peor) |
| `def_TOV%` | 50,3 % | 45,1 % | 49,4 % | 55,7 % | 67,3 % | Creciente, con meseta |
| `def_FT/FGA` | 67,7 % | 55,2 % | 59,5 % | 48,2 % | 38,8 % | Decreciente (más tiros libres permitidos, peor) |
| `AST` | 39,7 % | 42,4 % | 56,0 % | 55,5 % | 73,5 % | Creciente, con meseta |
| `TRB` | 36,8 % | 43,8 % | 59,5 % | 63,6 % | 63,6 % | Creciente y meseta |
| `3PAr` | 44,9 % | 43,3 % | 51,5 % | 61,7 % | 66,3 % | Creciente |
| `FT%` | 46,8 % | 47,5 % | 52,5 % | 53,4 % | 67,7 % | Creciente suave |
| `BLK` | 45,4 % | 48,0 % | 47,5 % | 58,9 % | 66,7 % | Creciente con meseta |
| `Pace` | 63,9 % | 61,0 % | 46,5 % | 49,1 % | 48,2 % | No monótono; Q1–Q2 más alto |
| `off_FT/FGA` | 40,9 % | 45,7 % | 61,3 % | 51,6 % | 67,9 % | No monótono; altibajo en Q4 |
| `off_ORB%` | 57,9 % | 55,3 % | 48,4 % | 48,5 % | 58,5 % | Plano / forma de U suave |

**Observación (B):** las relaciones de `off_eFG%`, `def_eFG%`, `Age`, `3P%`, `def_DRB%`, `off_TOV%` y `def_FT/FGA` son claramente monótonas. `Pace`, `off_FT/FGA` y `off_ORB%` no lo son.  
**Interpretación:** hay señal fuerte y direccional en eficiencia y cuidado del balón, pero no en todas las variables. Las no linealidades de `Pace` y `off_FT/FGA` justifican probar términos no lineales o modelos de árboles en Fase IV; no justifican afirmar causalidad.  
**Limitación:** los quintiles agrupan equipos con valores distintos; las tasas son descriptivas y no están ajustadas por otras variables. Los tamaños por quintil están en el CSV (aproximadamente 141–174 equipos-temporada por barra).

### 5.9 `09_atipicos_y_sesgo_16vars.png` — atípicos y sesgo

Archivo completo: `outputs_corrida2_16vars/metrics/eda_atipicos_16vars.csv`.  
Regla: 1,5 × IQR sobre los valores relativos.

| Variable | Atípicos | % | Comentario |
|---|---:|---:|---|
| `3P%` | 15 | 1,86 | Más atípicos; colas de equipos muy buenos/malos desde el triple. |
| `off_FT/FGA` | 14 | 1,74 | Estilos extremos de agresividad. |
| `3PAr` | 13 | 1,61 | Cambio de época y estilos extremos. |
| `def_FT/FGA` | 12 | 1,49 | Defensas que permiten muchas o pocas faltas. |
| `TRB` | 11 | 1,37 | Equipos con dominancia o debilidad clara en rebotes. |
| `off_TOV%` | 10 | 1,24 | Equipos con cuidado o descuido extremo del balón. |
| `AST` | 9 | 1,12 | — |
| `off_ORB%` | 9 | 1,12 | — |
| `FT%` | 8 | 0,99 | — |
| `Pace` | 6 | 0,75 | — |
| `BLK` | 6 | 0,75 | — |
| `off_eFG%` | 6 | 0,75 | — |
| `def_TOV%` | 5 | 0,62 | — |
| `def_DRB%` | 5 | 0,62 | — |
| `def_eFG%` | 1 | 0,12 | — |
| `Age` | 1 | 0,12 | — |

**Observación (B):** el máximo es 1,86 % (`3P%`, 15 casos). No hay una cola extrema generalizada.  
**Interpretación:** los atípicos son pocos y plausibles; no se eliminan porque pueden ser equipos legítimamente extremos (por ejemplo, una temporada histórica de tiro o de rebotes). La Fase IV debería usar modelos robustos o revisar la influencia de esos casos, no borrarlos automáticamente.  
**Limitación:** la regla IQR es sensible a la forma de la distribución y al tamaño de la temporada; marcar un punto como atípico no significa que sea un error.

### 5.10 `10_boxplots_cuatro_factores_16vars.png` — cuatro factores

**Observación (B), medianas relativas (no clasificó → clasificó):**
- `off_eFG%`: −0,0099 → +0,0080.
- `off_TOV%`: +0,2833 → −0,2367.
- `off_ORB%`: +0,0966 → −0,0900 (prácticamente sin separación).
- `off_FT/FGA`: −0,0055 → +0,0012 (muy pequeña).
- `def_eFG%`: +0,0100 → −0,0077.
- `def_TOV%`: −0,1867 → +0,1117.
- `def_DRB%`: −0,4267 → +0,4933.
- `def_FT/FGA`: +0,0033 → −0,0042 (pequeña).

**Interpretación:** los clasificados tiran mejor, pierden menos balón, defienden mejor el tiro, fuerzan más pérdidas y aseguran más rebotes defensivos. El rebote ofensivo no muestra separación; el componente de tiros libres es pequeño.  
**Limitación:** las cajas muestran distribuciones marginales; no controlan por las demás variables. La separación visual no es una prueba de importancia multivariada.

### 5.11 `11_boxplots_otras_variables_16vars.png` — otras ocho variables

**Observación (B), medianas relativas (no clasificó → clasificó):**
- `Age`: −0,9241 → +0,6882 (separación clara).
- `Pace`: +0,1733 → −0,5233 (los clasificados algo más lentos, pero con mucha superposición).
- `3PAr`: −0,0091 → +0,0059 (pequeña).
- `3P%`: −0,0062 → +0,0059 (moderada).
- `FT%`: −0,0024 → +0,0047 (pequeña).
- `AST`: −0,6069 → +0,2586 (moderada).
- `BLK`: −0,1633 → +0,1167 (pequeña).
- `TRB`: −0,4500 → +0,2500 (moderada).

**Interpretación:** además de la eficiencia, los clasificados tienden a ser mayores, algo más lentos, mejores pasadores y mejores reboteadores. `Age` es la más llamativa, pero no es una estadística de juego: puede reflejar plantillas veteranas o equipos contendientes. `Pace` tiene una relación débil y no monótona.  
**Limitación:** la edad y el ritmo pueden estar correlacionados con la calidad del equipo y con la época; el EDA no separa esos efectos.

---

## 6. Hallazgos principales

### 6.1 Observaciones respaldadas por los resultados

1. **El objetivo está balanceado:** 432 clasificados (53,7 %) y 373 no clasificados (46,3 %). La línea base trivial es 53,7 %.
2. **No hay nulos, infinitos, constantes ni duplicados en los 16 predictores.** Los únicos nulos son 4 en asistencia (2021), variable de contexto excluida.
3. **La defensa eficiente es la asociación más fuerte:** `def_eFG%` r = −0,582, d = −1,435. Los clasificados permiten un eFG% menor que la media de su temporada.
4. **La eficiencia ofensiva es la segunda:** `off_eFG%` r = +0,511, d = +1,191.
5. **`Age` aparece tercero:** r = +0,452, d = +1,014, pero es una característica de plantilla, no una estadística de juego.
6. **Aportan señal moderada:** `3P%` (r = +0,349), `def_DRB%` (+0,317), `AST` (+0,250) y `TRB` (+0,211).
7. **Lastran la clasificación:** `off_TOV%` (r = −0,275), `def_FT/FGA` (−0,191) y, en menor medida, `Pace` (−0,124).
8. **`off_ORB%` no muestra señal lineal:** r = −0,006; su tasa por quintiles es prácticamente plana.
9. **Solo hay un par con |r| ≥ 0,70:** `off_eFG%`–`3P%` (0,709). No hay pares ≥ 0,80.
10. **Los atípicos son pocos:** máximo 15 casos (1,86 %) en `3P%`; no se eliminan.
11. **La tasa de playoffs es esencialmente fija:** 16 por temporada; 55,17 % con 29 equipos y 53,33 % con 30. No hay tendencia temporal que explicar.
12. **La época cambia las medias:** `3PAr` 0,167 → 0,415; `Pace` 93,09 → 99,35; `ORtg` 104,05 → 115,78; eFG% 0,478 → 0,546.
13. **El cuadrante élite separa mucho:** ataque y defensa mejores que la media → 90,4 % clasificó (n = 239); ambos peores → 12,5 % (n = 257).

### 6.2 Hipótesis (C) — no probadas en esta fase

- La eficiencia de tiro y la defensa podrían ser las dimensiones más útiles para el modelo, pero su importancia relativa debe estimarse con validación cruzada en Fase IV.
- `Age` podría estar capturando madurez, continuidad o calidad de plantilla; no se puede interpretar como “ser mayor causa la clasificación”.
- Las no linealidades de `Pace` y `off_FT/FGA` podrían hacer que un modelo lineal pierda señal; conviene comparar con árboles o términos no lineales.
- La correlación `off_eFG%`–`3P%` podría inflar la varianza de los coeficientes logísticos; la regularización o una decisión explícita sobre una de las dos variables debería evaluarse en Fase IV.

### 6.3 Interpretación general (C)

Los resultados son coherentes con la idea de que, en baloncesto, **anotar eficientemente y evitar que el rival anote eficientemente** son los ejes más asociados a ganar y, por tanto, a clasificar. Pero el diseño es observacional y el objetivo está determinado por la clasificación final: no se puede afirmar que una estadística “cause” los playoffs. Además, las estadísticas de la temporada regular y la clasificación comparten la misma temporada; hay confusión por calidad de plantilla, lesiones, calendario, entrenador y formato.

---

## 7. Implicaciones para la Fase IV (no ejecutada)

Estas son recomendaciones, no resultados de modelado:

1. **Mantener los 16 predictores actuales** y documentar que `Age` no es una estadística de juego.
2. **Vigilar `off_eFG%`–`3P%`** por colinealidad; comparar con y sin una de ellas solo como análisis de sensibilidad, no para elegir con el test.
3. **Probar no linealidades** en `Pace` y `off_FT/FGA` (por ejemplo, términos cuadráticos o modelos de árboles) y comparar por validación cruzada.
4. **Usar validación estratificada y, además, una prueba temporal** (entrenar con temporadas antiguas y evaluar con recientes) para ver si la relación se mantiene con el play-in y la era moderna.
5. **No usar el conjunto de test para elegir variables, hiperparámetros ni transformaciones.**
6. **Reportar la mejora (o ausencia de mejora) de GridSearchCV con honestidad**, tal como se hizo en la corrida histórica de 19 variables.

---

## 8. Reproducibilidad y archivos generados

### 8.1 Comando ejecutado

Desde la raíz del proyecto:

```powershell
& .\.venv\Scripts\python.exe exploracion.py
```

- **Intérprete:** `.\.venv\Scripts\python.exe` (ruta relativa a la raíz del proyecto)
- **Python:** 3.15.2
- **pandas:** 3.1.1
- **numpy:** 2.5.5
- **matplotlib:** 3.11.2
- **scikit-learn:** 1.9.1 (instalado; **no se usó** en esta fase)
- **Sistema:** Windows 11 (10.0.26300)
- **Duración total medida por el shell:** 11,98 s (incluye el arranque del intérprete; el log del script abarca 13:02:35–13:02:44)
- **Código de salida:** 0

### 8.2 Figuras (11)

| Archivo | Contenido |
|---|---|
| `01_balance_clases_16vars.png` | Balance 0/1. |
| `02_evolucion_playoffs_por_temporada_16vars.png` | Composición de la liga y tasa de clasificación por temporada. |
| `03_deriva_por_epoca_16vars.png` | Deriva de `3PAr`, `Pace` y `ORtg`. |
| `04_histogramas_16vars.png` | Distribuciones relativas de los 16 predictores por clase. |
| `05_correlacion_con_objetivo_16vars.png` | Pearson y Spearman con el objetivo. |
| `06_correlacion_entre_predictores_16vars.png` | Matriz de correlación entre predictores. |
| `07_dispersion_efg_ataque_defensa_16vars.png` | Dispersión eFG% propio vs permitido y cuadrantes. |
| `08_tasa_playoffs_por_quintil_16vars.png` | Tasa de clasificación por quintil dentro de temporada. |
| `09_atipicos_y_sesgo_16vars.png` | Atípicos (IQR) y sesgo. |
| `10_boxplots_cuatro_factores_16vars.png` | Boxplots de los 8 cuatro factores. |
| `11_boxplots_otras_variables_16vars.png` | Boxplots de las otras 8 variables. |

### 8.3 Tablas (14 CSV + resumen + metadatos)

| Archivo | Contenido |
|---|---|
| `eda_calidad_datos_16vars.csv` | Tipo, nulos, infinitos, únicos, constantes, mín/máx por columna. |
| `eda_descriptivas_absolutas_16vars.csv` | Descriptivas de los 16 predictores en unidades originales. |
| `eda_descriptivas_relativas_16vars.csv` | Descriptivas de los 16 predictores relativos. |
| `eda_balance_objetivo_16vars.csv` | Conteo y porcentaje de clases. |
| `eda_balance_por_temporada_16vars.csv` | Equipos, clasificados y tasa por temporada. |
| `eda_resumen_por_clase_16vars.csv` | Medias/medianas por clase, diferencia y d de Cohen. |
| `eda_correlacion_objetivo_16vars.csv` | Pearson y Spearman con el objetivo. |
| `eda_matriz_correlacion_predictores_16vars.csv` | Matriz completa 16 × 16. |
| `eda_pares_correlacionados_16vars.csv` | Pares con |r| ≥ 0,70. |
| `eda_atipicos_16vars.csv` | Conteo, límites, mínimo, máximo y sesgo. |
| `eda_tasa_playoffs_por_quintil_16vars.csv` | n, clasificados y tasa por quintil y variable. |
| `eda_cuadrantes_efg_16vars.csv` | Conteo y tasa por cuadrante de eFG%. |
| `eda_por_temporada_16vars.csv` | Volumen, objetivo y medias de liga por temporada. |
| `eda_partidos_por_temporada_16vars.csv` | Partidos por equipo y temporadas incompletas. |
| `eda_resumen_16vars.txt` | Resumen legible de la corrida. |
| `eda_resumen_ejecucion_16vars.json` | Metadatos: versiones, hash de entrada, features, archivos. |

### 8.4 Logs

- `outputs_corrida2_16vars/logs/eda_16vars_20261118_130235.log` — log final del script (UTF-8).
- `outputs_corrida2_16vars/logs/consola_eda_16vars_20261118_130233.txt` — captura de consola de la corrida final.
- Los logs de 12:58 y 13:00 son iteraciones intermedias; la corrida válida es la de **13:02**.

### 8.5 Verificación de separación de corridas

- `outputs_corrida2_16vars/` contiene solo la corrida de 16 predictores; todos los archivos llevan `_16vars`.
- `outputs/` y `outputs_corrida1_19vars/` se compararon archivo por archivo: **22 archivos históricos, 0 diferencias**. No se modificó ningún resultado. Solo se añadió `outputs_corrida1_19vars/LEEME_RESPALDO.md` como nota de identificación.
- Los archivos de Fase IV en `outputs/` conservan sus marcas de tiempo del 2026-11-18 12:08–12:09; no se ejecutó `modelado.py`.
- `data/processed/nba_teams_clean.csv` conserva su fecha del 2026-11-17 23:43 y su hash `c04704d9…`; no se modificó Fase I ni Fase II.

---

## 9. Limitaciones del EDA

1. **Asociación no es causalidad.** Ninguna correlación o boxplot identifica un efecto causal.
2. **Una sola fuente:** Basketball-Reference. No se contrastó con otra fuente independiente.
3. **Definición del objetivo:** se usa el marcador de la fuente; el tratamiento del play-in (desde 2021) no se verificó contra el reglamento.
4. **Temporadas incompletas:** 2012 (66 partidos), 2020 (64–75), 2021 (72) y dos equipos de 2013 con 81. Se usan tasas y promedios, pero la comparación entre temporadas no es perfecta.
5. **Variables relativas transductivas:** el promedio de temporada incluye todos los equipos; no usa el objetivo, pero es una transformación que debe declararse.
6. **Observaciones no independientes:** el mismo equipo aparece en varias temporadas; las filas no son una muestra aleatoria de equipos.
7. **Confusores no medidos:** calidad de plantilla, lesiones, calendario, entrenador, viajes, decisiones tácticas.
8. **Sin pruebas de significancia:** el EDA es descriptivo; no se calcularon intervalos de confianza ni valores p. No se afirma significancia estadística.
9. **Correlación con objetivo binario:** el coeficiente está acotado y depende del balance; no es una importancia multivariada.
10. **Multicolinealidad:** solo se evaluó con correlaciones pairwise; no se calcularon VIF ni se ajustaron modelos.
11. **Atípicos:** no se eliminaron; la regla IQR puede marcar equipos legítimamente extremos.
12. **`Age` no es una estadística de juego:** su asociación puede reflejar calidad o continuidad de la plantilla; se mantiene porque está en la lista actual de 16, pero se discute como limitación.

---

## 10. Pendientes para revisión del tutor

- Confirmar con el docente o con la documentación de Basketball-Reference la definición exacta de `playoffs` en temporadas con play-in.
- Decidir si `Age` debe mantenerse como predictor en la entrega final o solo como variable de contexto; **no se cambió en esta fase**.
- Decidir en Fase IV si se mantienen `off_eFG%` y `3P%` juntas o si se evalúa una versión de sensibilidad sin una de ellas.
- Revisar si las no linealidades de `Pace` y `off_FT/FGA` justifican términos adicionales en el modelo.
- Si se quiere explicar los 4 nulos de asistencia, verificarlos en la fuente original; no se atribuyen a ninguna causa.
- Revisar los términos de uso de Basketball-Reference antes de publicar el repositorio (no es una tarea de EDA, pero afecta la entrega).

---

**Fin de la Fase III.** No se avanzó a Fase IV en ese momento; la Fase IV se ejecutó después y se documenta en `docs/FASE_IV_MODELADO_16VARS.md`. Este cierre se conserva como registro histórico.
