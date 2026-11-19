# Guion del video de sustentación

> **PLANTILLA — ASIGNAR «A» Y «B» ANTES DE GRABAR.**
> El equipo se encarga de la grabación; falta decidir qué integrante cubre cada bloque.
> Duración objetivo: **13–14 minutos** (máximo permitido: 15).
> Requisito del curso: cámara encendida al inicio, todos los integrantes se presentan y
> explican activamente una sección técnica. Publicar en YouTube como público u oculto
> (no Drive, no archivo local).

---

## Reparto

| Bloque | Minutos | Quién |
|---|---:|---|
| 1. Presentación y problema | 0:00–1:30 | Integrante A |
| 2. Fuente y ética | 1:30–2:30 | Integrante A |
| 3. Fase I: scraping | 2:30–4:30 | Integrante A |
| 4. Fase II: limpieza | 4:30–6:00 | Integrante A |
| 5. Fase III: EDA | 6:00–8:00 | Integrante B |
| 6. Fase IV: modelado | 8:00–11:30 | Integrante B |
| 7. Resultados y límites | 11:30–13:00 | Integrante B |
| 8. Cierre y preguntas | 13:00–14:00 | Ambos |

**Antes de grabar:** probar pantalla, micrófono, foco y que las figuras abran. Tener el
proyecto abierto en VS Code y una terminal en la raíz.

---

## 1. Presentación y problema (0:00–1:30) — Integrante A

**Cámara encendida. Saludo y nombres.**

> «Buenos días. Somos Mauricio Villafañe y Santiago de la Hoz. Presentamos nuestro proyecto de Ciencia
> de Datos con Python: *¿Qué estadísticas de juego explican que un equipo de la NBA llegue a
> playoffs?*»

> «La pregunta es concreta: al terminar la temporada regular, ¿podemos predecir si un equipo
> clasificará, usando solo su perfil estadístico? No usamos victorias ni margen de puntos,
> porque eso sería casi usar la respuesta.»

> «Es un problema de **clasificación binaria**: 1 si clasifica, 0 si no. La unidad es
> equipo-temporada. Tenemos 805 registros de 27 temporadas, de 2000 a 2026.»

**Mostrar:** `README.md` y el diagrama de fases.

---

## 2. Fuente y ética (1:30–2:30) — Integrante A

> «La fuente es Basketball-Reference, una página por temporada. Es un portal real, público y
> con datos oficiales de la liga.»

> «Respetamos sus límites: pausas de cuatro segundos, caché local y un User-Agent
> identificable. Si el sitio responde 403 o 429, el script se detiene; no evadimos bloqueos
> ni CAPTCHA.»

> «Los datos son agregados por equipo: no hay información personal ni médica.»

**Mostrar:** `scraping.py`, constante `SLEEP_SECONDS = 4`.

---

## 3. Fase I: scraping (2:30–4:30) — Integrante A

> «El requisito era un scraping automatizado con bucles. Recorremos 27 temporadas con un
> `for year in range(2000, 2027)`. Para cada año construimos la URL, descargamos la página y
> extraemos dos tablas: *Advanced* y *Per Game*.»

> «Un detalle técnico: algunas tablas están dentro de comentarios HTML. El script las
> descomenta antes de `read_html`. Sin eso, pandas no las ve.»

> «Validamos el título de la página y el número de equipos: 29 hasta 2004 y 30 desde 2005.
> Guardamos fragmentos por temporada y un log con el resultado de cada descarga.»

**Mostrar:** `data/raw/html/` (27 archivos), `data/raw/fragments/` (54), y
`outputs/logs/scrape_log.csv`.

**Frase de defensa:** «El bucle no solo descarga: valida, registra y permite reanudar con
caché. Eso es consolidación limpia, no una lista de URLs.»

---

## 4. Fase II: limpieza (4:30–6:00) — Integrante A

> «Unimos los 54 fragmentos con `pd.concat`. Luego verificamos duplicados: cero exactos y cero
> por la clave `(season, Team)`.»

> «Convertimos texto a número de forma explícita y auditada: contamos cuántos valores no se
> pudieron convertir. El resultado fue cero conversiones fallidas.»

> «Los únicos nulos están en asistencia: cuatro en `Attend.` y cuatro en `Attend./G`. No las
> usamos como predictoras por dos razones: tienen nulos y el éxito atrae público, así que la
> causalidad podría ir al revés.»

> «También aplicamos filtros con condiciones múltiples agrupadas con paréntesis. Por ejemplo:
> equipos que clasificaron con récord perdedor o diferencial negativo: 53 casos.»

**Mostrar:** `limpieza.py` (filtros), `outputs/metrics/limpieza_resumen.csv`, y el dataset
805 × 52.

**Frase de defensa:** «No imputamos en Fase II. Si hubiera nulos en predictores, se imputarían
con la mediana aprendida solo del train, dentro del pipeline.»

---

## 5. Fase III: EDA (6:00–8:00) — Integrante B

> «Mi parte es la exploración. Generamos 11 figuras y 14 tablas.»

> «El balance es 53,7 % clasificados y 46,3 % no clasificados. No hay desbalance severo, pero
> la accuracy sola no basta: una regla que siempre diga “clasifica” acierta 53,7 %.»

> «Las correlaciones más fuertes con el objetivo son `def_eFG%` con −0,582 —menor eficiencia
> de tiro permitida, más probabilidad de clasificar— y `off_eFG%` con +0,511. `Age` aparece
> con +0,452, pero es contexto de plantilla, no una estadística de juego.»

> «Detectamos una redundancia: `off_eFG%` y `3P%` correlacionan 0,709. No eliminamos variables;
> lo documentamos y luego lo tratamos en el modelo con VIF y sensibilidad.»

> «También vimos deriva de época: el uso del triple pasó de 0,167 a 0,415. Por eso todos los
> predictores se usan **relativos al promedio de su temporada**.»

**Mostrar:** figuras de balance, correlaciones y deriva de época en
`outputs_corrida2_16vars/figures/`.

**Frase de defensa:** «La transformación relativa no usa el objetivo; usa el promedio de la
temporada. Es transductiva y lo declaramos como limitación.»

---

## 6. Fase IV: modelado (8:00–11:30) — Integrante B

> «El requisito era scikit-learn, train/test, modelo base, `GridSearchCV` y validación cruzada
> de al menos 5 folds, comparando antes y después.»

> «Usamos 16 predictores. El pipeline es imputación por mediana, escalado y clasificador.
> Importante: la imputación y el escalado viven **dentro** del pipeline, así que en cada fold
> se ajustan solo con el train. Eso evita fuga de datos.»

> «Comparamos regresión logística y Random Forest. La logística tiene 8 combinaciones de `C`;
> el Random Forest, 48. Todos con los mismos 5 folds.»

> «Nuestro protocolo principal es **temporal**: entrenamos con 2000–2019 y probamos con
> 2020–2026. La validación cruzada agrupa por temporada, para que ningún fold comparta una
> temporada entre train y validación. Es el escenario más realista.»

> «El protocolo estratificado 80/20 es secundario: replica el protocolo histórico y sirve para
> comparar, pero no para elegir el modelo final.»

> «El umbral de decisión se elige en una validación interna del train. Ningún modelo,
> hiperparámetro ni umbral se eligió con el test; sobre el test calculamos algunas variantes
> solo para reportar. La importancia por permutación también se calcula en validación, no en test.»

**Mostrar:** `modelado.py` (secciones de `run_protocol`, `StratifiedGroupKFold`), y
`outputs_corrida2_16vars_fase4/metrics/modelado_cv_base_vs_optimizado_temporal_16vars.csv`.

**Frase de defensa:** «Hay tres decisiones anti-fuga: split antes de ajustar, preprocesamiento
dentro del pipeline y ningún modelo, hiperparámetro ni umbral elegido con el test.»

---

## 7. Resultados y límites (11:30–13:00) — Integrante B

> «En validación cruzada, la logística optimizada logra F1 0,912 y ROC-AUC 0,970. El Random
> Forest queda en F1 0,870; la logística gana.»

> «Pero hay un resultado incómodo y lo decimos claro: **la mejora de `GridSearchCV` no se
> replica en test**. Con el umbral titular 0,50, el modelo base tiene F1 0,879 y ROC-AUC 0,946;
> el optimizado baja a F1 0,866 y ROC-AUC 0,942. Con el umbral 0,46, elegido en validación
> interna, el optimizado llega a F1 0,880, prácticamente igual. No forzamos una mejora que no
> existe.»

> «Lo que sí es sólido: ROC-AUC 0,946, recall 0,938 y precisión 0,827 con el modelo base y
> umbral 0,50. Detecta casi todos los clasificados, con una de cada cinco alertas falsa.»

> «Las variables más importantes son `def_eFG%` y `def_TOV%`. La eficiencia defensiva y forzar
> pérdidas pesan más que el ataque en el modelo multivariado.»

> «Limitaciones: es observacional, no causal; el test tiene 210 filas; hay multicolinealidad
> alta en `TRB` con VIF 20,9; y el play-in cambia el significado de “clasificar” desde 2021.»

**Mostrar:** matriz de confusión, curva ROC, importancia por permutación y tabla de VIF.

**Frase de defensa:** «Reportar que la optimización no mejora el test es un resultado honesto.
El modelo base ya era fuerte y la grilla tenía poco margen.»

---

## 8. Cierre y preguntas (13:00–14:00) — Ambos

> «En conclusión: sí se puede predecir la clasificación con alta discriminación usando 16
> estadísticas relativas; la defensa eficiente es la señal más importante; y la optimización de
> hiperparámetros no garantiza mejorar fuera de muestra.»

> «Todo el proyecto es reproducible: scripts separados por fase, versiones fijadas, pruebas
> automáticas y resultados con hash. El repositorio y el informe están en la descripción.»

> «Gracias. ¿Preguntas?»

---

## Preguntas previsibles y respuestas cortas

| Pregunta | Respuesta |
|---|---|
| ¿Usaron victorias o margen de puntos? | No. Los excluimos por fuga de información; están en el diccionario de datos. |
| ¿Por qué variables relativas? | Para no medir la época. El triple pasó de 0,167 a 0,415; comparar valores absolutos confunde época con calidad. |
| ¿No es fuga usar el promedio de la temporada? | Es transductivo, no usa el objetivo. Se justifica porque predecimos al final de la temporada. Lo comparamos con variables absolutas: F1 0,912 vs. 0,908. |
| ¿Por qué no mejoró `GridSearchCV`? | La mejora en CV fue +0,004, dentro de una desviación. Con 805 filas y señales fuertes, la grilla tiene poco margen. Lo reportamos sin inflarlo. |
| ¿Por qué logística y no Random Forest? | Mejor F1 y ROC-AUC en ambos protocolos, y más estable entre folds. |
| ¿Por qué F1 y no accuracy? | Porque la accuracy sola premia decir “clasifica” (53,7 %). F1 equilibra precisión y recall. |
| ¿Cómo evitan fuga de datos? | Split antes de ajustar, preprocesamiento dentro del pipeline y ningún modelo, hiperparámetro ni umbral elegido con el test. |
| ¿Qué es el VIF? | Factor de inflación de varianza; mide cuánto se infla la varianza de un coeficiente por correlación con las demás. `TRB` tiene 20,9. |
| ¿Pueden afirmar causalidad? | No. Es un diseño observacional; la importancia es asociación. |
| ¿Qué harían con más tiempo? | Calibración, validación anidada, ranking por temporada e incorporar el play-in. |

---

## Lista de verificación antes de publicar

- [ ] Nombres y roles correctos en el reparto.
- [ ] Cámara encendida al inicio y presentación de ambos.
- [ ] Duración total ≤ 15 minutos.
- [ ] Audio claro y pantalla legible (zoom a las tablas).
- [ ] Se muestran archivos reales, no capturas inventadas.
- [ ] Se mencionan las limitaciones sin ocultarlas.
- [ ] Video subido a YouTube como público u oculto.
- [ ] Enlace del video pegado en el PDF y en el README.
- [ ] Enlace del repositorio verificado en una ventana sin sesión.
