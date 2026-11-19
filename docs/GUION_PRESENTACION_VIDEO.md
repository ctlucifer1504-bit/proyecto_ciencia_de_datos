# Guion de la presentación en video

> **Presentación:** `docs/PRESENTACION_VIDEO.pdf` — 18 diapositivas horizontales (16:9):
> 15 para narrar y 3 de anexo para preguntas.
> **Duración objetivo:** 14:10 (máximo del curso: 15:00).
> **Reparto A/B:** se asigna antes de grabar. A cubre las diapositivas 1–5; B, de la 6 a la 12;
> ambos cierran de la 13 a la 15. Si se prefiere, se intercambian los roles sin cambiar el texto.
> **Regla:** una idea por diapositiva. Señalar la figura o el número; no leer la diapositiva.

---

## Mapa de tiempos

| # | Diapositiva | Tema | Inicio–fin | Quién |
|---:|---|---|---|---|
| 1 | Portada | Pregunta, alcance y autores | 0:00–0:25 | A |
| 2 | El problema | Clasificación binaria sin fuga | 0:25–1:30 | A |
| 3 | Fuente y ética | Basketball-Reference y límites | 1:30–2:20 | A |
| 4 | Fase I | Scraping: 27 temporadas, 54 tablas | 2:20–3:50 | A |
| 5 | Fase II | Limpieza: 805 × 52 | 3:50–5:10 | A |
| 6 | Fase III | Balance y correlaciones | 5:10–6:40 | B |
| 7 | Fase III | Deriva de época | 6:40–7:25 | B |
| 8 | Fase IV | Pipeline, protocolos y anti-fuga | 7:25–8:50 | B |
| 9 | Fase IV | Validación cruzada | 8:50–9:45 | B |
| 10 | Fase IV | Test temporal: la mejora no se replica | 9:45–10:55 | B |
| 11 | Fase IV | Matriz de confusión y ROC | 10:55–11:40 | B |
| 12 | Fase IV | Importancia y VIF | 11:40–12:30 | B |
| 13 | Límites | Lo que el modelo no puede decir | 12:30–13:10 | Ambos |
| 14 | Conclusiones | Tres ideas | 13:10–13:50 | Ambos |
| 15 | Cierre | Repositorio y preguntas | 13:50–14:10 | Ambos |
| 16–18 | Anexos | Evidencias y métricas exactas | — | No se narran |

> Los anexos 16–18 no forman parte del discurso: se dejan listos para mostrar si el docente
> pide pruebas de ejecución, métricas exactas o verificación del repositorio.

---

## 1. Portada (0:00–0:25) — A

**Se ve:** título, 805 / 27 / 16 / 2, nombres y repositorio.

**Decir:**
> «Buenos días. Somos Mauricio Villafañe y Santiago de la Hoz. Presentamos nuestro proyecto de
> Ciencia de Datos con Python: *¿qué estadísticas explican que un equipo de la NBA llegue a
> playoffs?* Trabajamos con 805 equipo-temporadas, de 2000 a 2026, y 16 predictores. Todo está
> en el repositorio y en el informe que acompañan este video.»

**Apuntar:** el título y la fila de cifras de la derecha, no la lista de autores.

---

## 2. El problema (0:25–1:30) — A

**Se ve:** 805 registros, 53,7 % clasificados, 16 estadísticas; flujo perfil → modelo → 1/0.

**Decir:**
> «La pregunta es concreta: al terminar la temporada regular, ¿podemos anticipar si un equipo
> clasificará usando solo su perfil estadístico? Es clasificación binaria: uno si clasifica, cero
> si no. La unidad es equipo-temporada, no partido. Excluimos victorias, derrotas y margen de
> puntos porque contienen la respuesta; si el modelo los usa, no aprende: copia. Nos quedan 16
> estadísticas de juego, y cada una se expresa relativa al promedio de su temporada. El balance es
> 53,7 % clasificados y 46,3 % no clasificados; no hay desbalance severo, pero la accuracy sola no
> basta.»

**Apuntar:** el flujo y la frase «Excluimos W, L y NRtg».

---

## 3. Fuente y ética (1:30–2:20) — A

**Se ve:** Basketball-Reference, reglas 4 s / caché / UA / 403-429, datos agregados.

**Decir:**
> «La fuente es Basketball-Reference, una página por temporada. Es un portal público con datos
> oficiales de la liga. Respetamos sus límites: pausa de cuatro segundos entre peticiones, caché
> local y un User-Agent identificable. Si el sitio responde 403 o 429, el script se detiene; no
> evadimos bloqueos ni CAPTCHA. Los datos son agregados por equipo: no hay información personal ni
> médica. Y el repositorio no redistribuye los HTML ni el dataset: solo código, documentación,
> figuras y métricas agregadas.»

**Apuntar:** el recuadro «403/429: detener, no evadir» y la atribución a Sports Reference.

---

## 4. Fase I: scraping (2:20–3:50) — A

**Se ve:** 27 páginas → 54 tablas → 805 filas → 0 fallos; validaciones y log.

**Decir:**
> «El requisito era un scraping automatizado con bucles. Recorremos 27 temporadas con un `for`;
> para cada año construimos la URL, descargamos la página y extraemos dos tablas: *Advanced* y
> *Per Game*. Un detalle técnico: algunas tablas están dentro de comentarios HTML; el script las
> descomenta antes de leerlas, porque si no, pandas no las ve. Validamos el título de la página y
> el número de equipos: 29 hasta 2004 y 30 desde 2005. Guardamos 54 fragmentos y un log con el
> estado de cada descarga: 27 de 27 salieron `ok`. El bucle no solo descarga: valida, registra y
> permite reanudar con caché.»

**Apuntar:** la tabla del log y los chips de validación.

**Frase de defensa:** «No es una lista de URLs: cada descarga se valida y se registra.»

---

## 5. Fase II: limpieza (3:50–5:10) — A

**Se ve:** 0 duplicados, 0 infinitos, 8 nulos, 53 casos límite; flujo hasta 805 × 52.

**Decir:**
> «Unimos los 54 fragmentos con `pd.concat` y verificamos duplicados: cero exactos y cero por la
> clave temporada-equipo. Convertimos texto a número de forma explícita y auditada; el conteo de
> conversiones fallidas fue cero. Los únicos nulos están en asistencia: cuatro en `Attend.` y
> cuatro en `Attend./G`. No las usamos como predictoras: tienen nulos y el éxito atrae público,
> así que la causalidad podría ir al revés. También aplicamos filtros con condiciones múltiples
> entre paréntesis; por ejemplo, 53 equipos clasificaron con récord perdedor o diferencial
> negativo. El resultado es un dataset de 805 por 52.»

**Apuntar:** los cuatro contadores y el bloque azul «805 × 52».

**Frase de defensa:** «No imputamos aquí: la mediana se aprende solo del train, dentro del pipeline.»

---

## 6. Fase III: balance y correlaciones (5:10–6:40) — B

**Se ve:** figura de balance y barras de correlación con el objetivo.

**Decir:**
> «Mi parte es la exploración: 11 figuras y 14 tablas. El balance es 53,7 contra 46,3 %.
> La correlación más fuerte con el objetivo es `def_eFG%`: menos eficiencia de tiro permitida,
> más probabilidad de clasificar; su correlación es menos 0,582. Le sigue `off_eFG%` con más
> 0,511, y `Age` con 0,452, aunque `Age` es contexto de plantilla, no una estadística de juego.
> Detectamos una redundancia: `off_eFG%` y `3P%` correlacionan 0,709. No eliminamos variables: lo
> documentamos y lo tratamos en el modelo con VIF y análisis de sensibilidad. Una advertencia:
> una regla que siempre diga “clasifica” acierta 53,7 %; por eso usamos F1 y no solo accuracy.»

**Apuntar:** las dos barras naranjas (`def_eFG%` y `def_FT/FGA`) y el chip del 53,7 %.

---

## 7. Fase III: deriva de época (6:40–7:25) — B

**Se ve:** tres series por temporada; 3PAr 0,167 → 0,415; Pace 93,1 → 99,4.

**Decir:**
> «También vimos deriva de época. El uso del triple pasó de 0,167 a 0,415: de 16,7 a 41,5 % de
> los tiros. El ritmo subió de 93,1 a 99,4 posesiones. Comparar valores absolutos confundiría
> época con calidad. Por eso todos los predictores se usan relativos al promedio de su temporada.
> La transformación no usa el objetivo: usa el promedio de la temporada, y lo declaramos como
> limitación transductiva.»

**Apuntar:** la curva del triple, que es la más pronunciada.

---

## 8. Fase IV: metodología (7:25–8:50) — B

**Se ve:** pipeline imputación → escalado → modelo; protocolo temporal y estratificado; chips anti-fuga.

**Decir:**
> «El requisito era scikit-learn, train y test, modelo base, `GridSearchCV` y validación cruzada
> de al menos cinco folds, comparando antes y después. Usamos 16 predictores. El pipeline es
> imputación por mediana, escalado y clasificador. Importante: imputación y escalado viven dentro
> del pipeline, así que en cada fold se ajustan solo con el train; eso evita fuga. Comparamos
> regresión logística, con 8 combinaciones de `C`, y Random Forest, con 48. Todos con los mismos
> cinco folds. El protocolo principal es temporal: entrenamos con 2000 a 2019 y probamos con 2020
> a 2026. La validación agrupa por temporada con `StratifiedGroupKFold`, para que ningún fold
> comparta un año entre train y validación. El estratificado 80-20 es secundario. El umbral se
> elige en una validación interna del train: ningún modelo, hiperparámetro ni umbral se eligió con
> el test.»

**Apuntar:** el diagrama del pipeline y los tres chips verdes.

**Frase de defensa:** «Tres decisiones anti-fuga: split antes de ajustar, preprocesamiento dentro del pipeline y nada elegido con test.»

---

## 9. Fase IV: validación cruzada (8:50–9:45) — B

**Se ve:** 0,908 → 0,912; 0,865 → 0,870; ROC-AUC 0,970; ±0,009.

**Decir:**
> «En validación cruzada, la grilla sí mejora. La logística pasa de F1 0,908 a 0,912, y el Random
> Forest de 0,865 a 0,870. La logística optimizada alcanza ROC-AUC 0,970. La mejora es de cuatro
> milésimas, y la desviación del F1 es nueve milésimas: cabe dentro de una desviación. La logística
> gana en ambos protocolos: mejor F1, mejor ROC-AUC y más estable entre folds.»

**Apuntar:** las dos filas de comparación y el ±0,009.

---

## 10. Fase IV: test temporal (9:45–10:55) — B

**Se ve:** F1 0,879 base; 0,866 optimizado 0,50; 0,880 optimizado 0,46; CV +0,004 → test −0,013.

**Decir:**
> «Pero en test la mejora no se replica, y lo decimos claro. Con el umbral titular 0,50, el modelo
> base tiene F1 0,879 y ROC-AUC 0,946; el optimizado baja a F1 0,866 y ROC-AUC 0,942. Con el
> umbral 0,46, elegido en validación interna, el optimizado llega a F1 0,880, prácticamente igual
> que la base. No forzamos una mejora que no existe: con 805 filas y señales fuertes, la grilla
> tenía poco margen. Reportarlo es el resultado.»

**Apuntar:** la tarjeta naranja de 0,866 y la flecha «test, umbral 0,50: −0,013».

**Frase de defensa:** «La mejora en CV fue +0,004, dentro de una desviación; en test no aparece.»

---

## 11. Fase IV: matriz y ROC (10:55–11:40) — B

**Se ve:** matriz 75 / 23 / 6 / 106 y curva ROC con AUC 0,942.

**Decir:**
> «Este es el modelo optimizado con umbral 0,46. Acierta 106 de los 112 clasificados y deja
> escapar 6. Genera 23 falsos positivos: equipos con buen perfil que no clasificaron. La precisión
> es 0,822 y el recall 0,946. La curva ROC resume la discriminación: AUC 0,942. Detecta casi todos
> los clasificados, con una de cada seis alertas falsa.»

**Apuntar:** la celda 106 y el recuadro de la leyenda `AUC=0.942`.

---

## 12. Fase IV: importancia y VIF (11:40–12:30) — B

**Se ve:** barras de importancia por permutación; def_eFG% 0,113; def_TOV% 0,065; VIF 20,9.

**Decir:**
> «En importancia por permutación, la defensa manda. `def_eFG%` es la variable más importante, con
> una caída de F1 de 0,113; le sigue `def_TOV%`, con 0,065. Forzar pérdidas y defender el tiro
> pesan más que el ataque en el modelo multivariado. Ojo: es asociación, no causalidad, porque el
> diseño es observacional. Y hay multicolinealidad: `TRB` tiene VIF 20,9, así que su coeficiente
> no se lee de forma aislada.»

**Apuntar:** las dos primeras barras y la tarjeta naranja del VIF.

---

## 13. Límites (12:30–13:10) — Ambos

**Se ve:** cuatro tarjetas: observacional, 210 filas, VIF 20,9, umbral 0,46 vs 0,57.

**Decir:**
> «Tres límites que no ocultamos. Primero: observacional, no causal; la importancia no prueba que
> cambiar una estadística cambie la clasificación. Segundo: el test temporal tiene 210 filas,
> suficiente para comparar pero corto para conclusiones finas. Tercero: el umbral es inestable
> entre protocolos, 0,46 y 0,57; por eso la cifra titular es 0,50 y el resto es análisis
> secundario. Añadimos que el play-in, desde 2021, cambia el significado de “clasificar”.»

**Apuntar:** las tarjetas naranjas y la franja del play-in.

---

## 14. Conclusiones (13:10–13:50) — Ambos

**Se ve:** tres filas numeradas y la frase de cierre.

**Decir:**
> «Tres ideas. Uno: sí se puede predecir con alta discriminación; ROC-AUC 0,946 y F1 0,879 con el
> modelo base y umbral 0,50. Dos: la señal está en la defensa; `def_eFG%` y `def_TOV%` pesan más
> que el ataque. Tres: optimizar hiperparámetros no garantiza mejorar fuera de muestra; sube cuatro
> milésimas en validación y baja trece en test. La pregunta no era quién gana, sino qué perfil
> anticipa la clasificación.»

**Apuntar:** el número 3, porque es el resultado más honesto del proyecto.

---

## 15. Cierre (13:50–14:10) — Ambos

**Se ve:** repositorio, licencias, «¿Preguntas?».

**Decir:**
> «Todo el proyecto es reproducible: scripts por fase, versiones fijadas, pruebas automáticas y
> resultados con hash. El repositorio, el informe y esta presentación están enlazados en la
> descripción. Gracias. ¿Preguntas?»

**Apuntar:** la URL del repositorio en pantalla, para que quede legible en el video.

---

## Anexos (no se narran)

| # | Diapositiva | Para qué sirve |
|---:|---|---|
| 16 | Ejecución verificable | Mostrar 27/27 descargas, 805 × 52, hash y 23 pruebas si preguntan «¿cómo sabemos que corrió?» |
| 17 | Métricas exactas del test | Mostrar accuracy, precisión, recall, F1, ROC-AUC y Brier de las cuatro configuraciones |
| 18 | Repositorio público y sin datos | Mostrar `PUBLIC`, `main`, 144 archivos y que `data/` solo tiene el README |

**Si preguntan por el hash:** el dataset usado tiene SHA-256
`c04704d9ecdd511b24bd81b1aef73250082e02bd1f63a501eed900f1f9ea3ea9`.

**Si preguntan por la sensibilidad:** sin las variables con VIF > 10 el F1 baja a 0,893; con
valores absolutos en vez de relativos, a 0,908.

---

## Antes de grabar

- [ ] Asignar A y B y decirlo al inicio.
- [ ] Abrir `docs/PRESENTACION_VIDEO.pdf` en pantalla completa, sin barra de herramientas.
- [ ] Probar micrófono y compartir pantalla a 1080p.
- [ ] Ensayar una vez con cronómetro: si pasa de 14:30, recortar ejemplos, no resultados.
- [ ] Tener abierto el repositorio en el navegador para el cierre.
- [ ] Grabar cámara al inicio y al cierre.
- [ ] Revisar que se entiendan las cifras: hacer zoom a las figuras 6, 11 y 12.

## Después de grabar

- [ ] Subir a YouTube como **No listado** o **Público** (nunca «Privado»).
- [ ] Título: `¿Qué estadísticas explican que un equipo de la NBA llegue a playoffs? — Sustentación`.
- [ ] Descripción con integrantes, institución, repositorio y atribución a Sports Reference.
- [ ] Abrir el enlace en incógnito y comprobar que se reproduce.
- [ ] Enviar la URL para regenerar el PDF final y actualizar el README.

## Cómo se regenera la presentación

```powershell
& .\.venv\Scripts\python.exe tools\build_slides.py
```

Salida: `docs/PRESENTACION_VIDEO.pdf` (18 páginas, 960 × 540 pt). Requiere Chrome o Edge y
`pypdf`. El script solo maqueta figuras y métricas ya registradas; no recalcula nada.
