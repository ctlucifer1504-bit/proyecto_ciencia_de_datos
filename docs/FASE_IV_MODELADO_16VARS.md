# Fase IV — Modelado y optimización (16 predictores)

**Datos: Sports Reference LLC / Basketball-Reference.com.** El CSV de entrada no se
publica; se regenera con `data/README.md`.

**Proyecto:** ¿Qué estadísticas de la NBA explican que un equipo llegue a playoffs?  
**Corrida documentada:** `corrida2_16vars_fase4`  
**Fecha de ejecución:** 2026-11-18, 13:46:13–13:47:11 (hora local)  
**Entrada:** `data/processed/nba_teams_clean.csv`  
**SHA256 de la entrada:** `c04704d9ecdd511b24bd81b1aef73250082e02bd1f63a501eed900f1f9ea3ea9`  
**Salida:** `outputs_corrida2_16vars_fase4/`  
**Código:** `modelado.py`  
**Estado:** ejecutada y verificada. Los artefactos históricos de 19 variables no se modificaron.

> **Trazabilidad.** La corrida histórica de 19 predictores (`FTr`, `PF`, `STL`) se conserva en `outputs/` y `outputs_corrida1_19vars/`. Esta corrida de 16 predictores es independiente y escribe en `outputs_corrida2_16vars_fase4/`. No se mezclan resultados ni se presentan los históricos como actuales.

---

## 1. Problema, unidad de análisis y momento de predicción

- **Tipo de problema:** clasificación binaria.
- **Variable objetivo:** `playoffs` (1 = clasificó, 0 = no clasificó).
- **Unidad de análisis:** equipo-temporada. Cada fila es un equipo en una temporada regular.
- **Población:** 805 equipo-temporada, 27 temporadas (2000–2026), 29 equipos hasta 2004 y 30 desde 2005.
- **Momento de predicción:** al terminar la temporada regular, cuando ya se conocen las estadísticas de todos los equipos y antes de que comiencen los playoffs. La clasificación ya está definida en ese momento: es justamente el resultado que el modelo intenta explicar. El modelo es **retrospectivo/explicativo**; la información usada está disponible antes de que se jueguen los playoffs.
- **Uso esperado:** identificar qué dimensiones del juego se asocian con clasificar y estimar probabilidades para un equipo con un perfil dado. No es un sistema de decisión causal ni una herramienta de pronóstico en vivo.

**Limitación del momento de predicción:** si el modelo se usara antes de terminar la temporada regular, las estadísticas de temporada completa y el promedio de liga de esa temporada no estarían disponibles. En ese escenario habría fuga de información. Esta corrida **no declara** ese uso.

---

## 2. Protocolo anti-leakage y de evaluación

### 2.1 Predictores

Se usan exactamente los 16 predictores actuales, en su versión relativa a la temporada:

```text
off_eFG%, off_TOV%, off_ORB%, off_FT/FGA,
def_eFG%, def_TOV%, def_DRB%, def_FT/FGA,
Age, Pace, 3PAr, 3P%, FT%, AST, BLK, TRB
```

Cada predictor relativo se define como:

```text
x_rel = x - promedio de la liga en esa temporada
```

No se usan `W`, `L`, `PW`, `PL`, `MOV`, `SOS`, `SRS`, `NRtg`, `win_pct`, `Rk`, `ORtg`, `DRtg`, `Attend.` ni `Attend./G`.

### 2.2 Controles aplicados

- `train` y `test` se separan **antes** de imputar, escalar o ajustar.
- La imputación (`mediana`) y el escalado (`StandardScaler`) viven dentro de un `Pipeline`; se ajustan solo con el train de cada fold.
- El umbral de decisión se elige en una **validación interna del train**, no en test.
- La importancia por permutación se calcula en esa validación interna, no en test.
- **Fuga de datos:** ningún modelo, hiperparámetro ni umbral se eligió con el conjunto de test; sobre test se calcularon varias variantes (base, optimizado con umbral 0,50 y con umbral elegido en validación interna) solo con fines de reporte.
- Se verifica que el objetivo sea binario, que no haya duplicados `(season, Team)`, que no haya nulos ni infinitos en los predictores y que no haya predictores prohibidos.

### 2.3 Protocolo principal: temporal

- **Train:** temporadas 2000–2019 (595 filas).
- **Test:** temporadas 2020–2026 (210 filas).
- **Validación cruzada:** `StratifiedGroupKFold` con 5 folds, agrupando por temporada. Ningún fold comparte una temporada entre train y validación.
- **Justificación:** es el escenario más realista para generalizar a temporadas futuras. Además, evita que equipos de la misma temporada estén a ambos lados del split.

**Limitación:** el test incluye las temporadas 2020 y 2021, afectadas por burbuja, calendario acortado y play-in. También incluye 2026, la temporada más reciente. El desempeño no es constante entre temporadas.

### 2.4 Protocolo secundario: estratificado 80/20

- **Split:** 80/20 estratificado por clase, `random_state=42`.
- **Validación cruzada:** `StratifiedKFold` con 5 folds.
- **Justificación:** replica el protocolo de la corrida histórica de 19 variables y permite una comparación descriptiva.
- **Uso:** no se usa para elegir el modelo final ni para las afirmaciones principales. Es un análisis de robustez.

### 2.5 Sobre las variables relativas

El promedio de temporada incluye a todos los equipos de esa temporada, también los del test. Es una transformación **transductiva**. No usa la variable objetivo, pero sí la distribución de los predictores del test. Para el momento de predicción declarado —final de la temporada regular— ese promedio está disponible. Aun así, se documenta como limitación y se compara con un modelo sobre variables absolutas.

---

## 3. Modelos, pipeline y grillas

### 3.1 Pipeline

```text
SimpleImputer(strategy="median")
→ StandardScaler()
→ clasificador
```

### 3.2 Modelos candidatos

| Modelo | Grilla | Combinaciones |
|---|---|---:|
| Regresión logística | `C ∈ {0.001, 0.01, 0.1, 1, 10, 100, 1000, 10000}` | 8 |
| Random Forest | `n_estimators ∈ {200, 400}`, `max_depth ∈ {3, 5, 8, None}`, `min_samples_leaf ∈ {1, 3, 5}`, `max_features ∈ {sqrt, 0.5}` | 48 |

- **Selección:** `GridSearchCV` con 5 folds, `refit="f1"`.
- **Métrica de selección:** F1 de la clase positiva. Se justifica porque el problema no está severamente desbalanceado (53,7 % / 46,3 %), pero interesa equilibrar precisión y recall.
- **Comparación:** modelo base con hiperparámetros por defecto vs. modelo optimizado, con los **mismos folds**.

### 3.3 Métricas reportadas

Accuracy, precision, recall, F1, ROC-AUC, PR-AUC, Brier, matriz de confusión, reporte de clasificación y curva de calibración.

- **ROC-AUC:** capacidad de ordenar probabilidades.
- **PR-AUC:** útil cuando interesa la clase positiva.
- **Brier:** error cuadrático medio de las probabilidades; menor es mejor.
- **F1:** equilibrio entre precisión y recall al umbral elegido.

---

## 4. Resultados

### 4.1 Línea base trivial

| Protocolo | Accuracy CV | F1 CV | ROC-AUC CV |
|---|---:|---:|---:|
| Temporal | 0,538 | 0,699 | 0,500 |
| Estratificado | 0,537 | 0,699 | 0,500 |

La regla trivial “siempre clasifica” acierta alrededor del 53,7 %. Cualquier modelo útil debe superar ampliamente esa referencia. La accuracy sola no basta: el F1 trivial es 0,699 y el ROC-AUC es 0,500.

### 4.2 Validación cruzada: base vs. optimizado

#### Protocolo temporal

| Modelo | Etapa | Accuracy | F1 | ROC-AUC | PR-AUC | Brier |
|---|---|---:|---:|---:|---:|---:|
| Logística | Base | 0,901 ± 0,006 | 0,908 ± 0,007 | 0,971 ± 0,008 | 0,976 ± 0,006 | 0,069 ± 0,007 |
| Logística | Optimizada (`C=0.1`) | 0,904 ± 0,009 | 0,912 ± 0,009 | 0,970 ± 0,007 | 0,975 ± 0,007 | 0,074 ± 0,008 |
| Random Forest | Base | 0,850 ± 0,013 | 0,865 ± 0,011 | 0,932 ± 0,006 | 0,942 ± 0,003 | 0,112 ± 0,005 |
| Random Forest | Optimizado | 0,857 ± 0,034 | 0,870 ± 0,030 | 0,937 ± 0,009 | 0,944 ± 0,004 | 0,109 ± 0,007 |

**Observación (B):** la regresión logística supera claramente al Random Forest en validación cruzada. La mejora de GridSearchCV en F1 es +0,004 para logística y +0,006 para Random Forest; ambas quedan **dentro de una desviación estándar** entre folds. El Brier de la logística optimizada empeora ligeramente (0,074 vs. 0,069).

#### Protocolo estratificado

| Modelo | Etapa | Accuracy | F1 | ROC-AUC | Brier |
|---|---|---:|---:|---:|---:|
| Logística | Base | 0,896 ± 0,023 | 0,904 ± 0,020 | 0,971 ± 0,010 | 0,068 ± 0,012 |
| Logística | Optimizada (`C=1`) | 0,896 ± 0,023 | 0,904 ± 0,020 | 0,971 ± 0,010 | 0,068 ± 0,012 |
| Random Forest | Base | 0,862 ± 0,027 | 0,875 ± 0,025 | 0,935 ± 0,019 | 0,110 ± 0,009 |
| Random Forest | Optimizado | 0,874 ± 0,022 | 0,886 ± 0,021 | 0,938 ± 0,020 | 0,108 ± 0,010 |

**Observación (B):** en el protocolo estratificado, la grilla de logística eligió `C=1`, que es el valor por defecto; por eso base y optimizado son idénticos. Random Forest mejoró +0,011 en F1, también dentro de una desviación.

### 4.3 Evaluación final en test: protocolo temporal (principal)

Modelo final elegido por CV: **regresión logística con `C=0.1`**.

**Cifra titular (decisión del equipo):** se reporta el **umbral 0,50** para el modelo base y el optimizado. El umbral **0,46** elegido en la validación interna se presenta como **análisis secundario**, porque cambia entre protocolos (0,46 en temporal; 0,57 en estratificado) y en el estratificado empeora el F1.

| Modelo / umbral | Accuracy | Precision | Recall | F1 | ROC-AUC | PR-AUC | Brier |
|---|---:|---:|---:|---:|---:|---:|---:|
| Logística base (`C=1`), 0,50 | **0,862** | 0,827 | 0,938 | **0,879** | **0,946** | 0,951 | 0,099 |
| Logística optimizada, 0,50 | 0,848 | 0,817 | 0,920 | 0,866 | 0,942 | 0,947 | **0,097** |
| Logística optimizada, 0,46 | **0,862** | 0,822 | **0,946** | **0,880** | 0,942 | 0,947 | **0,097** |

**Observación (B):** con el umbral titular 0,50, el modelo optimizado **no supera al modelo base** en test: el base tiene mejor accuracy (0,862 vs. 0,848), F1 (0,879 vs. 0,866) y ROC-AUC (0,946 vs. 0,942), mientras que el optimizado tiene un Brier ligeramente menor (0,097 vs. 0,099). Al bajar el umbral a 0,46, el optimizado iguala la accuracy y el F1 del base, pero no lo supera. La mejora de CV no se tradujo en mejora de test.

**Interpretación (C):** la grilla encontró una solución ligeramente mejor en validación cruzada, pero la diferencia está dentro del ruido entre folds y no generaliza. La regularización más fuerte (`C=0.1`) mejora el recall y reduce ligeramente el Brier en test, a costa de precisión. No hay evidencia suficiente para afirmar que GridSearchCV mejora el desempeño fuera de muestra.

**Matriz de confusión (optimizado, umbral interno 0,46):**

> Esta matriz corresponde al umbral secundario elegido en validación interna. Se conserva porque es la que generó la corrida; no se re-ejecutó el modelo (congelación técnica). La comparación titular sigue siendo la de umbral 0,50.

|  | Predijo 0 | Predijo 1 |
|---|---:|---:|
| Real 0 | 75 (TN) | 23 (FP) |
| Real 1 | 6 (FN) | 106 (TP) |

- **Recall de la clase 1:** 0,946. El modelo detecta casi todos los clasificados.
- **Precision de la clase 1:** 0,822. Aproximadamente 1 de cada 5 predicciones positivas es falsa.
- **Clase 0:** precision 0,926, recall 0,765. El modelo es conservador para descartar equipos.

**Reporte de clasificación (umbral 0,46, secundario):**

```text
              precision    recall  f1-score   support
No clasifico      0.926     0.765     0.838        98
   Clasifico      0.822     0.946     0.880       112
    accuracy                          0.862       210
   macro avg      0.874     0.856     0.859       210
weighted avg      0.870     0.862     0.860       210
```

### 4.4 Evaluación final en test: protocolo estratificado (secundario)

Modelo final: **regresión logística con `C=1`** (el valor por defecto). Umbral elegido en validación interna: **0,57**.

| Modelo / umbral | Accuracy | Precision | Recall | F1 | ROC-AUC | PR-AUC | Brier |
|---|---:|---:|---:|---:|---:|---:|---:|
| Logística base/optimizada, 0,50 | **0,876** | **0,893** | **0,872** | **0,882** | **0,949** | **0,952** | **0,097** |
| Logística optimizada, 0,57 | 0,839 | 0,885 | 0,802 | 0,841 | 0,949 | 0,952 | 0,097 |

**Observación (B):** el umbral elegido en la validación interna (0,57) **empeora** el F1 en test (0,841 vs. 0,882). El umbral 0,50 es mejor en este split. Esto muestra que la elección de umbral es inestable y depende de la muestra de validación.

### 4.5 Comparación descriptiva con la corrida histórica de 19 variables

La corrida histórica usó 19 predictores (incluía `FTr`, `PF`, `STL`), split 80/20 estratificado y `random_state=42`. Su test reportó F1 0,869 para la logística optimizada. En esta corrida, el protocolo estratificado equivalente reporta F1 0,882.

**Observación (B):** el F1 es similar o ligeramente superior con 16 variables.  
**Limitación:** **no es una comparación controlada**. Los hiperparámetros se ajustaron por separado, las variables son distintas y la corrida histórica no tuvo el mismo conjunto de controles. No se debe afirmar que quitar `FTr`, `PF` y `STL` “mejora” el modelo; solo que, en esta muestra, no se observa una caída.

### 4.6 Análisis de errores

Con el umbral secundario 0,46, hay **23 falsos positivos** y **6 falsos negativos**. El análisis es descriptivo y no se usa para elegir el modelo.

**Falsos positivos (predijo clasificado, no clasificó):** varios equipos de 2026 (Miami Heat, Los Angeles Clippers, Charlotte Hornets, Golden State Warriors), 2024 Golden State Warriors, 2023 Chicago Bulls y New Orleans Pelicans, 2021 Golden State Warriors y Toronto Raptors, 2022 Cleveland Cavaliers, entre otros.

**Falsos negativos (predijo no clasificado, sí clasificó):** 2020 Portland Trail Blazers, 2021 Washington Wizards, 2022 Chicago Bulls y New Orleans Pelicans, 2023 Atlanta Hawks, 2026 Portland Trail Blazers.

**Observación (B):** varios falsos negativos corresponden a equipos que entraron por el play-in o a temporadas con formato especial.  
**Hipótesis (C):** el modelo, entrenado con temporadas anteriores al play-in, puede subestimar equipos que clasifican por esa vía. No se probó esta hipótesis formalmente.  
**Limitación:** el análisis es descriptivo; no se ajustó por calidad de plantilla, lesiones ni calendario.

### 4.7 Calibración

- **Brier en test (temporal):** 0,097.
- **Curva de calibración:** el modelo es razonablemente calibrado en el rango medio, pero **sobreestima** las probabilidades altas: en el tramo de probabilidad predicha ≈0,68 la frecuencia observada fue ≈0,55; en el tramo ≈0,82 fue ≈0,75.
- **Interpretación (C):** las probabilidades sirven para ordenar equipos, pero no deben interpretarse como probabilidades exactas sin calibración adicional (Platt/isotonic dentro del CV).

### 4.8 Importancia de variables y coeficientes

#### Importancia por permutación (validación interna, caída del F1)

| Variable | Caída del F1 | Desv. |
|---|---:|---:|
| `def_eFG%` | **0,113** | 0,023 |
| `def_TOV%` | **0,065** | 0,020 |
| `off_FT/FGA` | 0,033 | 0,017 |
| `off_TOV%` | 0,027 | 0,020 |
| `off_eFG%` | 0,022 | 0,022 |
| `TRB` | 0,020 | 0,011 |
| `def_DRB%` | 0,011 | 0,010 |
| `off_ORB%` | 0,010 | 0,014 |
| `AST` | 0,007 | 0,011 |
| `Age` | 0,004 | 0,013 |
| `Pace` | 0,004 | 0,011 |
| `FT%` | −0,001 | 0,008 |
| `BLK` | −0,001 | 0,003 |
| `def_FT/FGA` | −0,002 | 0,015 |
| `3P%` | −0,016 | 0,010 |
| `3PAr` | −0,022 | 0,011 |

**Observación (B):** `def_eFG%` domina la importancia por permutación, seguida por `def_TOV%`. `off_eFG%` baja al quinto lugar en el modelo multivariado, aunque en el EDA era la segunda correlación marginal. `3P%` y `3PAr` tienen importancia negativa, lo que indica que permutarlas no empeora el F1 e incluso puede mejorarlo dentro del ruido.

**Interpretación (C):** la importancia por permutación mide dependencia conditional del modelo, no importancia causal. Con predictores correlacionados, una variable puede “absorber” el efecto de otra; `3P%` está correlacionada con `off_eFG%` (r = 0,709) y su importancia individual puede quedar enmascarada.

#### Coeficientes estandarizados (logística temporal, `C=0.1`)

| Variable | Coeficiente | Odds ratio por 1 SD |
|---|---:|---:|
| `off_eFG%` | +1,110 | 3,03 |
| `def_TOV%` | +1,071 | 2,92 |
| `off_FT/FGA` | +0,602 | 1,83 |
| `Age` | +0,394 | 1,48 |
| `TRB` | +0,377 | 1,46 |
| `def_DRB%` | +0,356 | 1,43 |
| `AST` | +0,334 | 1,40 |
| `off_ORB%` | +0,318 | 1,37 |
| `3PAr` | +0,242 | 1,27 |
| `FT%` | +0,163 | 1,18 |
| `3P%` | +0,149 | 1,16 |
| `BLK` | −0,004 | 1,00 |
| `def_FT/FGA` | −0,336 | 0,71 |
| `Pace` | −0,372 | 0,69 |
| `off_TOV%` | −0,660 | 0,52 |
| `def_eFG%` | −1,374 | 0,25 |

**Limitación importante:** estos coeficientes **no son interpretables como efectos causales ni como importancias estables** por la multicolinealidad. Por ejemplo, `off_ORB%` tiene coeficiente positivo pese a que su correlación marginal con el objetivo es ≈0; es un efecto de supresión.

### 4.9 Multicolinealidad y sensibilidad

#### VIF sobre el train temporal

| Variable | VIF |
|---|---:|
| `TRB` | **20,91** |
| `Pace` | **10,75** |
| `off_ORB%` | **10,39** |
| `def_eFG%` | 6,45 |
| `off_eFG%` | 4,11 |
| `def_DRB%` | 3,51 |
| `def_TOV%` | 2,53 |
| `3P%` | 2,26 |
| `AST` | 1,96 |
| `3PAr` | 1,79 |
| `def_FT/FGA` | 1,77 |
| `Age` | 1,76 |
| `BLK` | 1,68 |
| `off_FT/FGA` | 1,54 |
| `off_TOV%` | 1,50 |
| `FT%` | 1,32 |

**Observación (B):** `TRB` supera el umbral habitual de 10, y `Pace` y `off_ORB%` están en el límite. Esto era esperable: `TRB` es la suma de rebotes ofensivos y defensivos, y `off_ORB%`/`def_DRB%` miden componentes relacionados.

#### Sensibilidad (protocolo temporal, CV)

| Escenario | Predictores | F1 | Accuracy | ROC-AUC |
|---|---:|---:|---:|---:|
| Principal (16 relativas) | 16 | 0,912 ± 0,009 | 0,904 | 0,970 |
| Sin `Age` | 15 | 0,911 ± 0,010 | 0,904 | 0,971 |
| Sin `3P%` | 15 | 0,910 ± 0,010 | 0,903 | 0,970 |
| Sin `Age` y `3P%` | 14 | 0,912 ± 0,007 | 0,904 | 0,971 |
| Sin `TRB` | 15 | 0,909 ± 0,009 | 0,901 | 0,970 |
| Sin `TRB`, `Pace`, `off_ORB%` (VIF > 10) | 13 | 0,893 ± 0,007 | 0,884 | 0,964 |
| Variables absolutas | 16 | 0,908 ± 0,015 | 0,899 | 0,969 |

**Observación (B):** quitar `Age`, `3P%` o `TRB` apenas cambia el F1 (≤0,003). Quitar las tres variables con VIF > 10 reduce el F1 a 0,893 (−0,019), pero sigue muy por encima de la línea base. Usar variables absolutas en lugar de relativas baja el F1 a 0,908 (−0,004), una diferencia pequeña.

**Interpretación (C):** el modelo es robusto a la eliminación de variables individuales, pero la multicolinealidad afecta la interpretación de coeficientes. La transformación relativa aporta una mejora pequeña, no dramática.

---

## 5. Hallazgos

### 5.1 Observaciones respaldadas por la ejecución

1. La regresión logística supera al Random Forest en los dos protocolos.
2. La mejora de GridSearchCV es pequeña y está dentro de una desviación estándar entre folds.
3. En el protocolo temporal, el modelo optimizado **no supera** al modelo base en test; el F1 baja de 0,879 a 0,866 con umbral 0,50.
4. Con umbral 0,46, el modelo optimizado iguala al base (F1 0,880, accuracy 0,862) pero no lo supera.
5. El modelo tiene alto recall (0,946) y precisión moderada (0,822) para la clase “clasificó”.
6. La calibración es aceptable en el rango medio, pero sobreestima probabilidades altas.
7. `def_eFG%` es la variable más importante por permutación; `def_TOV%` es segunda.
8. `off_eFG%`, que era la segunda correlación marginal en el EDA, baja a quinto lugar en importancia multivariada.
9. `3P%` y `3PAr` tienen importancia negativa en el modelo con 16 variables; no aportan señal adicional clara.
10. Hay multicolinealidad alta en `TRB` (VIF 20,9), `Pace` (10,7) y `off_ORB%` (10,4).
11. El modelo es robusto a quitar `Age`, `3P%` o `TRB`; quitar las tres variables con VIF > 10 reduce el F1 en 0,019.
12. Las variables relativas funcionan ligeramente mejor que las absolutas (F1 0,912 vs. 0,908).

### 5.2 Hipótesis (no probadas)

- La defensa eficiente y la capacidad de forzar pérdidas podrían ser los ejes más útiles para predecir clasificación, pero el diseño observacional no permite afirmar causalidad.
- La importancia negativa de `3P%`/`3PAr` podría deberse a redundancia con `off_eFG%` y a la forma en que el modelo reparte el efecto entre variables correlacionadas.
- Los falsos negativos de equipos que entraron por play-in podrían reflejar un cambio de formato no capturado por las variables.
- Una calibración explícita (Platt/isotonic) podría mejorar el Brier y la interpretación de probabilidades.

### 5.3 Interpretación general

El modelo confirma que la eficiencia defensiva y el cuidado del balón son las dimensiones más asociadas a clasificar, seguidas por la eficiencia ofensiva y el componente de tiros libres. La regresión logística es suficiente; el Random Forest no aporta una mejora. La optimización de hiperparámetros no produce una mejora fuera de muestra, lo que es un resultado honesto y defendible: en un problema con 805 filas, 16 predictores y señales fuertes, la grilla tiene poco margen.

**No se afirma causalidad.** Las variables son descriptivas de la temporada regular y el objetivo es la clasificación final; hay confusores no medidos (calidad de plantilla, lesiones, entrenador, calendario, formato de playoffs).

---

## 6. Limitaciones

1. **Observacional, no causal.** Ningún coeficiente ni importancia identifica un efecto causal.
2. **Test pequeño:** 210 equipo-temporada en el protocolo temporal y 161 en el estratificado; las métricas tienen incertidumbre y no se reportaron intervalos de confianza.
3. **Importancia inestable:** se calculó en una validación interna de 119 filas (20 % de las 595 de train temporal); los intervalos de la importancia por permutación son anchos y se solapan entre casi todas las variables, excepto `def_eFG%`.
4. **Una sola fuente:** Basketball-Reference; no se validó con otra fuente.
5. **Cambios de formato:** play-in desde 2021, burbuja 2020, temporadas acortadas 2012, 2020 y 2021, y dos equipos con 81 partidos en 2013.
6. **Variables relativas transductivas:** usan el promedio de la temporada completa, que incluye a los equipos del test; se justifica por el momento de predicción, pero limita el uso antes del final de la temporada.
7. **Multicolinealidad:** VIF alto en `TRB` (20,9), `Pace` (10,7) y `off_ORB%` (10,4); los coeficientes individuales no son estables.
8. **Umbral inestable:** el umbral elegido en validación interna no siempre mejora el test (protocolo estratificado); por eso el titular usa 0,50.
9. **`best_score_` optimista:** sin validación anidada, la estimación de CV del modelo elegido es algo optimista; se mitiga reportando test.
10. **Dos familias de modelos:** no se probaron gradient boosting, SVM ni modelos regularizados alternativos.
11. **Sin validación externa:** no hay una temporada completamente nueva fuera del rango 2000–2026.
12. **Observaciones no independientes:** el mismo equipo aparece en varias temporadas; las filas no son una muestra aleatoria de equipos.
13. **Calibración:** probabilidades sobreestimadas en la cola alta; no se aplicó calibración.
14. **`Age` no es una estadística de juego:** su efecto es pequeño en el modelo multivariado, pero sigue siendo una variable de contexto.
15. **Selección de variables:** se mantuvieron las 16 por decisión de alcance; el análisis de sensibilidad muestra que algunas podrían eliminarse sin gran pérdida.

---

## 7. Recomendaciones

1. **No afirmar que GridSearchCV mejora el modelo** en este conjunto: la mejora de CV es pequeña y no se replica en test.
2. **Reportar siempre CV y test por separado**, con umbral explícito.
3. **Añadir calibración** (Platt/isotonic) dentro del CV si se van a interpretar probabilidades.
4. **Probar nested CV** para una estimación menos optimista del modelo elegido.
5. **Evaluar un modelo de ranking** que asigne probabilidades y seleccione los 16 mejores por temporada, en lugar de clasificar cada equipo de forma independiente.
6. **Mantener el análisis de sensibilidad** sin `Age`, sin `3P%` y sin las variables con VIF > 10.
7. **No usar los coeficientes para inferencia causal**; usar importancia por permutación solo como descriptiva.
8. **Documentar el momento de predicción** en el informe y el video.
9. **Si se busca generalización futura**, validar con una temporada realmente nueva y con el formato de play-in vigente.

---

## 8. Reproducibilidad y archivos

### 8.1 Comando

```powershell
& .\.venv\Scripts\python.exe modelado.py
```

- **Python:** 3.15.2
- **pandas:** 3.1.1
- **numpy:** 2.5.5
- **scikit-learn:** 1.9.1
- **matplotlib:** 3.11.2
- **Duración:** 57,60 s (medida por el script); 61,68 s de pared.
- **Código de salida:** 0.
- **Log final:** `outputs_corrida2_16vars_fase4/logs/modelado_16vars_20261118_134613.log`
- **Consola final:** `outputs_corrida2_16vars_fase4/logs/consola_modelado_16vars_20261118_134611.txt`

### 8.2 Figuras (10)

| Archivo | Contenido |
|---|---|
| `modelado_matriz_confusion_temporal_16vars.png` | Matriz de confusión, protocolo temporal. |
| `modelado_matriz_confusion_estratificado_16vars.png` | Matriz de confusión, protocolo estratificado. |
| `modelado_curva_roc_temporal_16vars.png` | ROC temporal. |
| `modelado_curva_roc_estratificado_16vars.png` | ROC estratificado. |
| `modelado_curva_pr_temporal_16vars.png` | Precision-recall temporal. |
| `modelado_curva_pr_estratificado_16vars.png` | Precision-recall estratificado. |
| `modelado_calibracion_temporal_16vars.png` | Calibración temporal. |
| `modelado_calibracion_estratificado_16vars.png` | Calibración estratificada. |
| `modelado_importancia_temporal_16vars.png` | Importancia por permutación temporal. |
| `modelado_importancia_estratificado_16vars.png` | Importancia por permutación estratificada. |

### 8.3 Tablas y metadatos

| Archivo | Contenido |
|---|---|
| `modelado_cv_base_vs_optimizado_{temporal,estratificado}_16vars.csv` | Base vs. optimizado, CV. |
| `modelado_test_{temporal,estratificado}_16vars.csv` | Métricas de test por modelo y umbral. |
| `modelado_gridsearch_{protocolo}_{modelo}_16vars.csv` | Resultados completos de la grilla. |
| `modelado_matriz_confusion_{protocolo}_16vars.csv` | Matriz de confusión. |
| `modelado_classification_report_{protocolo}_16vars.txt` | Reporte de clasificación. |
| `modelado_predicciones_test_{protocolo}_16vars.csv` | Predicciones con temporada, equipo y probabilidad. **No se publica** (fila a fila). |
| `modelado_importancia_{protocolo}_16vars.csv` | Importancia por permutación. |
| `modelado_coeficientes_{protocolo}_16vars.csv` | Coeficientes o importancia por impureza. |
| `modelado_vif_16vars.csv` | VIF sobre el train temporal. |
| `modelado_sensibilidad_16vars.csv` | Sensibilidad a la selección de variables. |
| `modelado_resumen_16vars.json` | Resumen completo de la corrida. |
| `modelado_resumen_16vars.txt` | Resumen legible. |
| `modelado_manifiesto_16vars.json` | Manifiesto con hash, versiones y outputs. |

### 8.4 Separación de corridas

- `outputs_corrida2_16vars_fase4/` contiene solo esta corrida.
- `outputs/` y `outputs_corrida1_19vars/` se compararon archivo por archivo: **22 archivos, 0 diferencias SHA256**. No se modificó ningún resultado histórico.
- Los archivos de Fase IV históricos en `outputs/` conservan sus marcas de tiempo del 2026-11-18 12:08–12:09.
- `data/processed/nba_teams_clean.csv` conserva su hash `c04704d9…ea3ea9`.

---

## 9. Conclusión de la fase

La Fase IV quedó ejecutada con 16 predictores, dos protocolos de evaluación y controles explícitos contra fuga de datos. El resultado principal es sobrio: **la regresión logística predice bien, pero GridSearchCV no mejora el desempeño fuera de muestra**. La defensa eficiente y la creación de pérdidas son las señales más importantes; la eficiencia ofensiva también aporta. La multicolinealidad obliga a no interpretar los coeficientes como efectos causales.

El proyecto queda listo para la etapa de documentación final, informe y sustentación. **No se avanzó a una fase posterior ni se modificaron los resultados históricos.**
