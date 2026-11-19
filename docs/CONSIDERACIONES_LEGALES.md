# Consideraciones legales y éticas sobre los datos

**Proyecto:** ¿Qué estadísticas explican que un equipo de la NBA llegue a playoffs?
**Integrantes:** Mauricio Villafañe y Santiago de la Hoz
**Consulta de términos:** 2026-11-18

> **Aviso:** este documento es información para la entrega académica, **no asesoría
> legal**. No se ha recibido permiso expreso de Sports Reference LLC. Ante una duda
> concreta, la decisión corresponde al equipo y, si se requiere certeza, a un asesor
> legal o a la propia Sports Reference.

**Datos: Sports Reference LLC / Basketball-Reference.com.**

## 1. Qué dicen los términos

Los *Sports Reference Terms of Use* (última actualización: 19 de mayo de 2023) incluyen,
en la cláusula 5, una restricción sobre inteligencia artificial. El texto pertinente
(cláusula 5(k), conservado en inglés para no alterar su sentido) dice:

> “copy or use any material or Content from the Site, including without limitation any
> statistics, data, text, graphics, or images, for purposes of training, fine-tuning,
> prompting, or instructing artificial intelligence models or technologies in any
> manner, including without limitation for purposes of (i) generating answers, text,
> scores, statistics, notes, graphics, images, or any other output; or (ii) supporting
> machine learning methods used to predict, classify, label, or score inputs into the
> models”

Fuente: https://www.sports-reference.com/termsofuse.html (consultada el 2026-11-18).

La misma cláusula 5 permite compartir y reutilizar datos de páginas individuales con
atribución, pero sujeta esa reutilización a las restricciones expresas, en particular
las de 5(i) y 5(j) (no crear una base de datos o servicio que compita con el sitio) y
la de 5(k) (IA).

La página de uso de datos resume la restricción así:

> “This means that you should not create websites or tools based on data you scrape
> from Sports Reference or any of our sites or use our data to train generative
> artificial intelligence models without our permission.”

Fuente: https://www.sports-reference.com/data_use.html (consultada el 2026-11-18).

Esa misma página también recuerda que, conforme al derecho de autor, los hechos no son
objeto de derechos de autor y pueden reutilizarse conforme a la ley.

## 2. La ambigüedad, declarada

- La cláusula 5(k) es **amplia**: habla de «cualquier manera» y menciona expresamente
  «métodos de aprendizaje automático usados para predecir, clasificar, etiquetar o
  puntuar». Leída literalmente, un proyecto académico que entrena una regresión
  logística o un Random Forest para clasificar equipos podría quedar dentro de (ii).
- La página de uso de datos pone el énfasis en **IA generativa** y en no crear
  herramientas que compitan con el sitio; no aclara el caso de un trabajo académico de
  clasificación sin redistribución.
- No hay una excepción académica general en los términos. La cláusula 6 permite a los
  docentes imprimir páginas para distribuir a estudiantes con atribución, pero no
  autoriza a crear y publicar una base de datos derivada.
- Por eso **no afirmamos** que el proyecto esté autorizado por los términos, ni que esté
  prohibido. Lo documentamos como **incertidumbre**.

## 3. Qué hizo este proyecto

- Extrajo 27 páginas públicas de Basketball-Reference (temporadas 2000–2026) con un
  script propio, pausas de 4 s y caché local.
- Construyó un dataset de 805 filas equipo-temporada y entrenó modelos de clasificación
  con fines **explicativos y académicos**.
- No creó una base de datos pública, no ofrece un servicio que sustituya al sitio y no
  vende ni redistribuye los datos.
- El uso de asistentes de IA se declara en `docs/DECLARACION_IA.md`. No se usó IA
  generativa para crear, completar o alterar las observaciones: los datos provienen de
  la extracción. La asistencia se aplicó a código, revisión y redacción.

## 4. Mitigaciones aplicadas

1. **Sin redistribución de datos crudos.** El repositorio público no incluye HTML,
   fragmentos, CSV crudos, el dataset procesado ni predicciones fila a fila. Solo se
   publican código, documentación, figuras y métricas agregadas.
2. **Ritmo bajo y caché.** Pausa de 4 s entre peticiones (por debajo del límite de ~20
   por minuto), 27 páginas en total y reutilización de los HTML ya descargados.
3. **Sin datos personales.** No se recogen nombres, correos ni datos de personas; la
   unidad es equipo-temporada.
4. **Sin IA generativa para los datos.** No se usó IA para inventar, completar o alterar
   observaciones ni resultados; las cifras provienen de ejecuciones registradas.
5. **Uso educativo y no comercial.** El proyecto es una entrega de curso, no un producto.
6. **Atribución visible.** README y documentos indican «Datos: Sports Reference LLC /
   Basketball-Reference.com».
7. **Instrucciones de regeneración.** `data/README.md` explica cómo obtener los datos sin
   publicarlos.
8. **Trazabilidad.** Hashes, manifiestos y logs permiten verificar que las cifras
   publicadas corresponden a la corrida documentada.

## 5. Decisión sobre los datos

**No se redistribuyen.** Las licencias MIT (código) y CC BY 4.0 (documentación) no se
aplican a los datos. Si en el futuro se quisiera publicar el dataset, habría que obtener
permiso de Sports Reference o sustituir la fuente por una que permita redistribución.

## 6. Referencias

- Sports Reference LLC. *Sports Reference Terms of Use*. Cláusula 5(k).
  https://www.sports-reference.com/termsofuse.html
- Sports Reference LLC. *SR and Data Use*.
  https://www.sports-reference.com/data_use.html
- Creative Commons. *CC BY 4.0*.
  https://creativecommons.org/licenses/by/4.0/
