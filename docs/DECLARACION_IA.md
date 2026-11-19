# Declaración de uso de inteligencia artificial

**Proyecto:** ¿Qué estadísticas de juego explican que un equipo de la NBA llegue a playoffs?
**Integrantes:** Mauricio Villafañe y Santiago de la Hoz
**Institución:** Universidad Americana de Barranquilla — Facultad de Ingeniería de Sistemas
**Asignatura:** Ciencia de Datos con Python · **Docente:** Edgar Morillo Vergel
**Periodo:** 7.º semestre · 2026

**Datos: Sports Reference LLC / Basketball-Reference.com.**

---

## 1. Herramientas utilizadas

| Herramienta | Versión / modelo | Uso declarado | Integrantes | Fechas |
|---|---|---|---|---|
| OpenCode | DeepSeek V4.1 Flash (proveedor OpenCode) | Agente de código: revisión, corrección y ejecución de scripts; documentación y pruebas | Ambos | 2026, antes de la entrega (fechas exactas no registradas) |
| Claude | Claude Sonnet 5.5 (claude.ai) | Diseño metodológico, código de las cuatro fases, documentos, prompts, auditoría y revisión de términos | Ambos | 17 y 18 de noviembre de 2026 |
| ChatGPT | ChatGPT (GPT-6) | Guía principal y recomendaciones generales; no generó código | Ambos | 2026 (fechas exactas no registradas) |

## 2. Uso de Claude (detalle)

Claude se usó en las siguientes tareas, según lo declarado por el equipo:

- **Diseño metodológico:** discusión del problema, los protocolos de evaluación y los
  controles anti-fuga.
- **Código de las cuatro fases:** apoyo en `scraping.py`, `limpieza.py`, `exploracion.py`
  y `modelado.py`. El código se **revisó y corrigió**; no se copió sin revisión.
- **Documentos e informe:** apoyo en la redacción y revisión de `docs/` y del informe.
- **Prompts:** diseño de instrucciones para las herramientas de IA.
- **Fuente y términos:** verificó la viabilidad de Basketball-Reference revisando páginas
  del sitio y sus términos de uso, y analizó la cláusula 5.
- **Entorno:** ayudó a depurar errores de `pip` y del entorno virtual.
- **Auditoría:** ejecutó las 23 pruebas y reprodujo `modelado.py` en un entorno
  independiente.
- **Límite explícito:** Claude **no ejecutó el scraping sobre el sitio real**; esa
  extracción la ejecutaron los integrantes.

## 3. Uso de ChatGPT (detalle)

ChatGPT se usó como **guía principal y para recomendaciones generales**. No generó código
que se haya incorporado al proyecto. Las fechas exactas no se registraron.

## 4. Uso de OpenCode (detalle)

OpenCode/DeepSeek se usó como agente de código: revisión y corrección de los scripts de las
cuatro fases, reescritura de `exploracion.py` para 16 predictores, reescritura de
`modelado.py` con controles anti-fuga y métricas ampliadas, redacción de borradores de
`docs/`, guion y pruebas, y auditoría de integridad de los archivos históricos.

## 5. Para qué NO se usó

- No se generaron datos, métricas ni ejecuciones ficticias.
- No se usó IA para crear, completar o alterar las observaciones: los datos provienen de
  la extracción.
- No se inventaron nombres de integrantes, institución, fechas ni enlaces.
- No se sustituyó la comprensión del equipo: cada integrante debe poder explicar el código.
- No se usó para evadir los límites de acceso de Basketball-Reference.

## 6. Verificación humana

| Verificación | Responsable | Estado |
|---|---|---|
| Ejecutar los cuatro scripts y revisar salidas | Ambos | Pendiente de confirmación explícita |
| Revisar que las métricas del informe coincidan con los CSV | Ambos | Pendiente de confirmación explícita |
| Entender y poder explicar cada decisión metodológica | Ambos | Pendiente de confirmación explícita |
| Revisar la redacción final del informe | Ambos | Pendiente de confirmación explícita |

> Las firmas se incorporan en la versión PDF de entrega. Este repositorio publica la
> declaración sin imágenes de firma.

## 7. Trazabilidad de afirmaciones

El proyecto usa cuatro etiquetas:

- **(A)** confirmado por una fuente.
- **(B)** resultado observado al ejecutar.
- **(C)** inferencia razonada.
- **(D)** propuesta pendiente de validar.

Los informes de fase distinguen explícitamente entre observación, interpretación e hipótesis.

## 8. Declaración

Declaramos que:

1. El uso de IA se limitó a asistencia técnica, metodológica y de redacción.
2. Los resultados presentados provienen de ejecuciones reales registradas en `outputs*/`.
3. Las limitaciones del proyecto se documentan sin ocultarlas.
4. Asumimos la responsabilidad académica por el contenido entregado.

> **Nota:** si el curso prohíbe total o parcialmente el uso de IA, esta declaración debe
> ajustarse antes de entregar. El equipo indicó que no recibió una prohibición expresa.
