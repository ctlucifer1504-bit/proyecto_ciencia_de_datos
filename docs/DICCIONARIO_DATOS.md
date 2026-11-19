# Diccionario de datos

**Datos: Sports Reference LLC / Basketball-Reference.com.** El CSV no se publica.

**Archivo:** `data/processed/nba_teams_clean.csv`
**Filas:** 805 · **Columnas:** 52 · **Temporadas:** 27 (2000–2026)
**Unidad de análisis:** equipo-temporada (una temporada regular por fila)
**Clave única:** `(season, Team)`
**SHA256 del archivo:** `c04704d9ecdd511b24bd81b1aef73250082e02bd1f63a501eed900f1f9ea3ea9`
**Origen:** Basketball-Reference, tablas *Advanced* y *Per Game* por temporada, unidas en Fase II.

> **Convención de unidades.** Las tasas marcadas como «proporción 0–1» vienen así de la
> fuente. Los porcentajes marcados como «%» están en escala 0–100 (p. ej. `off_TOV% = 13.2`
> significa 13,2 %). Los promedios «por partido» son por equipo y partido.

> **Nota de trazabilidad.** Las columnas `x_rel` **no existen en el CSV**: se calculan en
> `exploracion.py` como `x_rel = x − promedio de la liga en esa temporada`. El modelo usa
> únicamente las 16 versiones relativas.

---

## 1. Identificadores y variable objetivo

| Columna | Tipo | Unidad | Descripción | Uso |
|---|---|---|---|---|
| `season` | entero | año | Año de cierre de la temporada (2026 = temporada 2025-26). | Identificador y grupo de validación. No es predictor. |
| `Team` | texto | — | Nombre de la franquicia tal como aparece en la fuente. | Identificador. No es predictor. |
| `playoffs` | entero 0/1 | — | 1 = clasificó a playoffs; 0 = no clasificó. | **Variable objetivo.** |

**Distribución del objetivo:** 432 clasificados (53,66 %) y 373 no clasificados (46,34 %).
Cada temporada aporta exactamente 16 clasificados.

---

## 2. Los 16 predictores

Todos tienen **805 valores, 0 nulos y 0 infinitos**. Estadísticos calculados sobre el CSV completo.

### 2.1 Cuatro factores ofensivos

| Columna | Tipo | Unidad | Media | Mín | Máx | Qué mide | Dirección esperada |
|---|---|---:|---:|---:|---:|---|---|
| `off_eFG%` | float | proporción 0–1 | 0,506 | 0,428 | 0,578 | Effective Field Goal %: acierto de tiro ajustando que el triple vale más. | Mayor es mejor. |
| `off_TOV%` | float | % de posesiones | 13,260 | 9,900 | 18,000 | Porcentaje de posesiones que terminan en pérdida. | Menor es mejor. |
| `off_ORB%` | float | % de rebotes | 25,751 | 17,900 | 35,300 | Porcentaje de rebotes ofensivos disponibles que el equipo captura. | Mayor es mejor (segundas oportunidades). |
| `off_FT/FGA` | float | razón | 0,216 | 0,143 | 0,303 | Tiros libres intentados por tiro de campo intentado. Mide agresividad y estilo. | Mayor = más agresivo; no es «mejor» per se. |

### 2.2 Cuatro factores defensivos

| Columna | Tipo | Unidad | Media | Mín | Máx | Qué mide | Dirección esperada |
|---|---|---:|---:|---:|---:|---|---|
| `def_eFG%` | float | proporción 0–1 | 0,506 | 0,433 | 0,578 | Effective Field Goal % **permitido** al rival. | Menor es mejor. |
| `def_TOV%` | float | % de posesiones | 13,261 | 10,300 | 16,500 | Porcentaje de posesiones del rival que terminan en pérdida (forzadas). | Mayor es mejor. |
| `def_DRB%` | float | % de rebotes | 74,234 | 66,100 | 81,600 | Porcentaje de rebotes defensivos disponibles que el equipo captura. | Mayor es mejor. |
| `def_FT/FGA` | float | razón | 0,216 | 0,145 | 0,340 | Tiros libres permitidos por tiro de campo del rival. | Menor es mejor (menos faltas). |

### 2.3 Otras ocho variables

| Columna | Tipo | Unidad | Media | Mín | Máx | Qué mide | Nota |
|---|---|---:|---:|---:|---:|---|---|
| `Age` | float | años | 26,632 | 22,100 | 32,000 | Edad promedio de la plantilla ponderada por minutos. | **No es una estadística de juego**; es contexto de plantilla. |
| `Pace` | float | posesiones/48 min | 94,562 | 86,200 | 105,100 | Ritmo estimado de posesiones por 48 minutos. | Estilo, no calidad. |
| `3PAr` | float | proporción 0–1 | 0,277 | 0,095 | 0,536 | Proporción de triples sobre tiros de campo intentados. | Estilo de tiro. |
| `3P%` | float | proporción 0–1 | 0,356 | 0,278 | 0,416 | Porcentaje de acierto en triples. | Correlacionada con `off_eFG%` (r = 0,709). |
| `FT%` | float | proporción 0–1 | 0,763 | 0,660 | 0,839 | Porcentaje de acierto en tiros libres. | Aporte directo al puntaje. |
| `AST` | float | por partido | 22,840 | 17,400 | 31,000 | Asistencias por partido. | Indicador de circulación de balón. |
| `BLK` | float | por partido | 4,902 | 2,400 | 8,200 | Tapones por partido. | Protección del aro. |
| `TRB` | float | por partido | 42,864 | 36,900 | 51,700 | Rebotes totales por partido (ofensivos + defensivos). | **VIF 20,9**: redundante con `off_ORB%` y `def_DRB%`. |

---

## 3. Columnas excluidas del modelo

Se conservan en el CSV para auditoría, EDA y análisis de sensibilidad, pero **no entran como predictores**.

### 3.1 Fuga de información (revelan el resultado)

| Columna | Descripción | Motivo de exclusión |
|---|---|---|
| `W` | Victorias. | El récord determina la clasificación; usarlo sería casi usar el objetivo. |
| `L` | Derrotas. | Complemento exacto de `W`. |
| `PW`, `PL` | Victorias y derrotas «Pythagorean». | Estimación del récord esperado; misma fuga. |
| `MOV` | Margen promedio de puntos. | Mide directamente cuánto gana; muy cercano al resultado. |
| `SOS` | Strength of Schedule. | Ajuste del calendario ligado al récord. |
| `SRS` | Simple Rating System. | Combina margen y calendario; equivalente práctico a la calidad-resultado. |
| `NRtg` | Net Rating (puntos por 100 posesiones). | Diferencial de anotación; casi el resultado. |
| `win_pct` | Porcentaje de victorias (`W / G`). | Derivado directo del récord. |
| `ORtg` | Offensive Rating (puntos por 100 posesiones). | Se usa solo como referencia externa; mide anotación, no el estilo de los cuatro factores. |
| `DRtg` | Defensive Rating. | Igual que `ORtg`. |

> `Rk` aparece en la fuente pero **no existe como columna** en el CSV procesado.

### 3.2 Excluidas por otras razones

| Columna | Descripción | Motivo |
|---|---|---|
| `Attend.` | Asistencia total de la temporada. | Causalidad inversa (el éxito atrae público) y **4 nulos**. |
| `Attend./G` | Asistencia promedio por partido. | Igual que `Attend.`; **4 nulos**. |
| `TS%` | True Shooting %. | Queda fuera del alcance de 16 variables; redundante con `off_eFG%` y `FT%`. |
| `FTr` | Free Throw Rate (`FTA / FGA`). | Excluida en la corrida actual de 16 variables (estaba en la histórica de 19). |
| `STL` | Robos por partido. | Excluida en la corrida actual (estaba en la histórica de 19). |
| `PF` | Faltas personales por partido. | Excluida en la corrida actual (estaba en la histórica de 19). |

### 3.3 Conteos y totales de la temporada

| Columna | Descripción | Nota |
|---|---|---|
| `G` | Partidos jugados. | Varía por temporada (66 en 2012; 64–75 en 2020; 72 en 2021). Usar tasas, no totales. |
| `MP` | Minutos por partido. | Contexto; no predictor. |
| `FG`, `FGA`, `FG%` | Tiros de campo convertidos, intentados y porcentaje. | Totales o tasas ya representadas por los cuatro factores. |
| `3P`, `3PA`, `3P%` | Triples convertidos, intentados y porcentaje. | `3P%` sí es predictor; `3P` y `3PA` no. |
| `2P`, `2PA`, `2P%` | Tiros de dos. | No usados. |
| `FT`, `FTA`, `FT%` | Tiros libres. | `FT%` sí es predictor; `FT` y `FTA` no. |
| `ORB`, `DRB`, `TRB` | Rebotes ofensivos, defensivos y totales. | `TRB` sí es predictor. |
| `AST`, `STL`, `BLK`, `TOV`, `PF`, `PTS` | Totales o promedios por partido. | Solo `AST` y `BLK` entran como predictores. |

---

## 4. Calidad de datos

| Comprobación | Resultado |
|---|---|
| Filas | 805 |
| Columnas | 52 |
| Duplicados exactos | 0 |
| Duplicados `(season, Team)` | 0 |
| Nulos en los 16 predictores | 0 |
| Nulos en el objetivo | 0 |
| Nulos en columnas de contexto | `Attend.` = 4, `Attend./G` = 4 |
| Infinitos en predictores | 0 |
| Valores del objetivo | Solo 0 y 1 |
| Temporadas con menos de 82 partidos | 2012 (66), 2020 (64–75), 2021 (72); en 2013 dos equipos jugaron 81 |

**Tratamiento de nulos:** no se imputa nada en Fase II. Si en el futuro apareciera un nulo
en un predictor, el `Pipeline` de Fase IV lo imputa con la **mediana aprendida solo del
train** de cada fold.

---

## 5. Variables derivadas en el código

| Nombre | Fórmula | Dónde se crea | Uso |
|---|---|---|---|
| `x_rel` | `x − mean(x de todos los equipos de esa temporada)` | `exploracion.py::add_relative_features` | Predictor del modelo. |
| `win_pct` | `W / G` | `limpieza.py` | Excluida (fuga). |

**Ejemplo:** si en 2026 el promedio de liga de `3PAr` es 0,415 y un equipo tiene 0,380,
su `3PAr_rel` es −0,035: dispara triples por debajo del promedio de su época.

> **Limitación declarada:** el promedio de temporada incluye a todos los equipos, también
> los del conjunto de test. Es una transformación **transductiva**: no usa el objetivo,
> pero sí la distribución de los predictores del test. Se justifica porque el momento de
> predicción es el final de la temporada regular. El análisis de sensibilidad con variables
> absolutas muestra una diferencia pequeña (F1 CV 0,908 vs. 0,912).
