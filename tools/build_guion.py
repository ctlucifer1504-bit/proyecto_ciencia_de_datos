"""Genera el guion de la presentación en PDF (una columna, estética sobria).

Uso:
    & .\\.venv\\Scripts\\python.exe tools\\build_guion.py

Salida: docs/GUION_PRESENTACION_VIDEO.pdf
No recalcula nada: el texto y las cifras son los de la presentación ya generada
por tools/build_slides.py.
"""

from __future__ import annotations

import sys
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = ROOT / "docs" / "GUION_PRESENTACION_VIDEO.pdf"

AZUL = HexColor("#0B3D5C")
VERDE = HexColor("#0F766E")
GRIS = HexColor("#5C7280")
GRIS_CLARO = HexColor("#8A9AA6")
LINEA = HexColor("#D7E2EA")
FONDO = HexColor("#F3F8FB")
AMBAR = HexColor("#B45309")

ANCHO, ALTO = A4
MARGEN_L = MARGEN_R = 2.1 * cm
MARGEN_T = 1.9 * cm
MARGEN_B = 1.9 * cm
UTIL = ANCHO - MARGEN_L - MARGEN_R

# --------------------------------------------------------------------------
# Texto del guion
# --------------------------------------------------------------------------

SLIDES = [
    {
        "n": 1,
        "titulo": "Portada",
        "tiempo": "0:00 - 0:25",
        "quien": "Mauricio",
        "ver": "Título, la columna de cifras (805 / 27 / 16 / 2) y el repositorio al pie.",
        "decir": (
            "«Buenos días. Somos Mauricio Villafañe y Santiago de la Hoz. En este video "
            "presentamos nuestro proyecto de Ciencia de Datos con Python: qué estadísticas "
            "explican que un equipo de la NBA llegue a playoffs. Usamos 805 equipo-temporadas, "
            "de 2000 a 2026, y 16 predictores.»"
        ),
        "apuntar": "El título y la columna de cifras de la derecha.",
    },
    {
        "n": 2,
        "titulo": "El problema",
        "tiempo": "0:25 - 1:20",
        "quien": "Mauricio",
        "ver": "805 registros, 53,7 % clasificados, 16 estadísticas; flujo perfil, modelo, 1/0.",
        "decir": (
            "«La pregunta es concreta: al terminar la temporada regular, ¿podemos anticipar si "
            "un equipo clasificará usando solo su perfil estadístico? Es clasificación binaria: "
            "uno si clasifica, cero si no. La unidad es equipo-temporada, no partido: 805 filas. "
            "El 53,7 % clasificó y el 46,3 % no; no hay desbalance severo, pero la accuracy sola "
            "no basta. Excluimos victorias, derrotas y margen de puntos porque contienen la "
            "respuesta: si el modelo los usa, no aprende, copia. Nos quedan 16 estadísticas de "
            "juego, y cada una se expresa relativa al promedio de su temporada, para que el "
            "modelo no confunda época con calidad.»"
        ),
        "apuntar": "El flujo y la franja naranja que explica por qué se excluyen W, L y NRtg.",
    },
    {
        "n": 3,
        "titulo": "Fuente y ética",
        "tiempo": "1:20 - 2:05",
        "quien": "Mauricio",
        "ver": "Basketball-Reference y las cuatro reglas: 4 s, caché, UA, 403/429.",
        "decir": (
            "«La fuente es Basketball-Reference, una página por temporada. Respetamos sus "
            "límites: pausa de cuatro segundos entre peticiones, caché local y un User-Agent "
            "identificable. Si el sitio responde 403 o 429, el script se detiene; no evadimos "
            "bloqueos ni CAPTCHA. Los datos son agregados por equipo: no hay información "
            "personal ni médica. El repositorio no redistribuye los HTML, los CSV crudos ni el "
            "dataset; solo código, figuras y métricas agregadas, con la atribución a Sports "
            "Reference.»"
        ),
        "apuntar": "El recuadro «403/429: detener, no evadir» y la línea de atribución.",
    },
    {
        "n": 4,
        "titulo": "Fases I y II: de 27 páginas a 805 × 52",
        "tiempo": "2:05 - 3:35",
        "quien": "Mauricio",
        "ver": "27 páginas, 54 tablas, 805 × 52; contadores de limpieza y chips del log.",
        "decir": (
            "«En la Fase I recorremos 27 temporadas con un bucle: para cada año construimos la "
            "URL, descargamos la página y extraemos dos tablas, Advanced y Per Game. Algunas "
            "tablas están dentro de comentarios HTML y el script las descomenta antes de "
            "leerlas, porque si no, pandas no las ve. Validamos el título y el número de equipos, "
            "29 hasta 2004 y 30 desde 2005. El log registra 27 de 27 descargas en ok: el bucle "
            "valida, registra y permite reanudar con caché. No es una lista de URLs. "
            "En la Fase II unimos los 54 fragmentos: cero duplicados exactos y cero por la clave "
            "temporada-equipo. El conteo de conversiones fallidas fue cero y no hay infinitos. "
            "Los únicos nulos están en asistencia, cuatro y cuatro; no la usamos como predictora "
            "porque tiene nulos y porque el éxito atrae público, así que la causalidad podría ir "
            "al revés. También aplicamos filtros con condiciones múltiples: 53 equipos "
            "clasificaron con récord perdedor o diferencial negativo. El resultado es un dataset "
            "de 805 por 52.»"
        ),
        "apuntar": "La fila 27 páginas, 54 tablas, 805 × 52 y los cuatro contadores de limpieza.",
    },
    {
        "n": 5,
        "titulo": "Fase III: el rival a vencer es el 53,7 %",
        "tiempo": "3:35 - 4:45",
        "quien": "Mauricio",
        "ver": "Figura de balance y barras de correlación; chips con las cifras clave.",
        "decir": (
            "«Mi parte termina con la exploración: 11 figuras y 14 tablas. El balance es 53,7 "
            "contra 46,3 %. La correlación más fuerte con el objetivo es def_eFG%, con menos "
            "0,582: menos eficiencia de tiro permitida, más probabilidad de clasificar. Le siguen "
            "off_eFG% con 0,511 y Age con 0,452, aunque Age es contexto de plantilla, no una "
            "estadística de juego. Detectamos redundancia: off_eFG% y 3P% correlacionan 0,709. "
            "No eliminamos variables; lo documentamos y lo tratamos con VIF y análisis de "
            "sensibilidad. También vimos deriva de época: el uso del triple pasó de 0,167 a "
            "0,415 y el ritmo de 93,1 a 99,4 posesiones, y por eso todo se usa relativo a su "
            "temporada. Y una advertencia: una regla que siempre diga clasifica acierta 53,7 %, "
            "así que usamos F1, no solo accuracy.»"
        ),
        "apuntar": "Las dos primeras barras de correlación y el chip naranja del 53,7 %.",
    },
    {
        "n": 6,
        "titulo": "Fase IV: un pipeline, dos protocolos, cero fuga",
        "tiempo": "4:45 - 5:55",
        "quien": "Santiago",
        "ver": "Pipeline imputación, escalado, modelo; protocolo temporal y estratificado.",
        "decir": (
            "«Mi parte es el modelado. Usamos 16 predictores y comparamos regresión logística, "
            "con 8 combinaciones de C, y Random Forest, con 48. El pipeline es imputación por "
            "mediana, escalado y clasificador, y todo vive dentro del pipeline: en cada fold, "
            "imputación y escalado se ajustan solo con el train. Eso evita fuga. Hay dos "
            "protocolos. El principal es temporal: entrenamos con 2000 a 2019 y probamos con "
            "2020 a 2026, 210 filas. La validación agrupa por temporada con StratifiedGroupKFold "
            "de 5 folds, para que ningún fold comparta un año entre train y validación. El "
            "estratificado 80-20 es secundario. Y el umbral se elige en una validación interna "
            "del train: ningún modelo, hiperparámetro ni umbral se eligió con el test.»"
        ),
        "apuntar": "El diagrama del pipeline y los tres chips verdes anti-fuga.",
    },
    {
        "n": 7,
        "titulo": "Fase IV: en validación cruzada, la grilla sí mejora",
        "tiempo": "5:55 - 6:35",
        "quien": "Santiago",
        "ver": "0,908 a 0,912; 0,865 a 0,870; ROC-AUC 0,970; desviación ±0,009.",
        "decir": (
            "«En validación cruzada la grilla sí mejora. La logística pasa de F1 0,908 a 0,912, "
            "y el Random Forest de 0,865 a 0,870. La logística optimizada alcanza ROC-AUC 0,970. "
            "La mejora es de cuatro milésimas y la desviación del F1 es nueve milésimas: cabe "
            "dentro de una desviación estándar. La logística gana en ambos protocolos: mejor F1, "
            "mejor ROC-AUC y más estable entre folds.»"
        ),
        "apuntar": "Las dos filas de comparación y la tarjeta del ±0,009.",
    },
    {
        "n": 8,
        "titulo": "Fase IV: en test, la mejora no se replica",
        "tiempo": "6:35 - 7:25",
        "quien": "Santiago",
        "ver": "Tres tarjetas: 0,879 base; 0,866 optimizado 0,50; 0,880 optimizado 0,46.",
        "decir": (
            "«Pero en test la mejora no se replica, y lo decimos claro. Con el umbral titular "
            "0,50, el modelo base tiene F1 0,879 y ROC-AUC 0,946; el optimizado baja a F1 0,866 "
            "y ROC-AUC 0,942. Con el umbral 0,46, elegido en validación interna, el optimizado "
            "llega a F1 0,880, prácticamente igual que la base. La mejora en CV fue más 0,004; "
            "en test, con 0,50, es menos 0,013. No forzamos una mejora que no existe: con 805 "
            "filas y señales fuertes, la grilla tenía poco margen. Reportarlo es el resultado.»"
        ),
        "apuntar": "La tarjeta naranja de 0,866 y la flecha «test, umbral 0,50: -0,013».",
    },
    {
        "n": 9,
        "titulo": "Fase IV: dónde acierta y qué pesa",
        "tiempo": "7:25 - 8:15",
        "quien": "Santiago",
        "ver": "Matriz 75 / 23 / 6 / 106 e importancia por permutación.",
        "decir": (
            "«Este es el modelo optimizado con umbral 0,46. Acierta 106 de los 112 clasificados "
            "y deja escapar 6. Genera 23 falsos positivos: equipos con buen perfil que no "
            "clasificaron. Precisión 0,822; recall 0,946. El AUC global es 0,942: detecta casi "
            "todos los clasificados con una de cada seis alertas falsa. "
            "En importancia por permutación, la defensa manda: def_eFG% cae 0,113 en F1 y "
            "def_TOV% 0,065. Forzar pérdidas y defender el tiro pesan más que el ataque. Ojo: "
            "es asociación, no causalidad, porque el diseño es observacional.»"
        ),
        "apuntar": "La celda 106 de la matriz y las dos primeras barras de importancia.",
    },
    {
        "n": 10,
        "titulo": "Límites: lo que el modelo no puede decir",
        "tiempo": "8:15 - 9:05",
        "quien": "Santiago",
        "ver": "Cuatro tarjetas: observacional, 210 filas, VIF 20,9, umbral inestable.",
        "decir": (
            "«Tres límites que no ocultamos. Primero: observacional, no causal; la importancia "
            "no prueba que cambiar una estadística cambie la clasificación. Segundo: el test "
            "temporal tiene 210 filas, suficiente para comparar pero corto para conclusiones "
            "finas. Tercero: hay multicolinealidad; TRB tiene VIF 20,9, así que su coeficiente "
            "no se lee aislado, y sin las variables con VIF mayor a 10 el F1 baja a 0,893. "
            "Añadimos que el umbral es inestable entre protocolos, 0,46 y 0,57; por eso la cifra "
            "titular es 0,50. Y el play-in, desde 2021, cambia el significado de clasificar.»"
        ),
        "apuntar": "Las tarjetas naranjas y la franja azul del play-in.",
    },
    {
        "n": 11,
        "titulo": "Conclusiones y cierre",
        "tiempo": "9:05 - 10:00",
        "quien": "Ambos",
        "ver": "Tres filas numeradas, la URL del repositorio y «Gracias · ¿Preguntas?».",
        "decir": (
            "«Tres ideas. Uno: sí se puede predecir con alta discriminación; ROC-AUC 0,946 y "
            "F1 0,879 con el modelo base y umbral 0,50. Dos: la señal está en la defensa; "
            "def_eFG% y def_TOV% pesan más que el ataque. Tres: optimizar hiperparámetros no "
            "garantiza mejorar fuera de muestra; sube cuatro milésimas en validación y baja "
            "trece en test. La pregunta no era quién gana, sino qué perfil anticipa la "
            "clasificación. Todo el proyecto es reproducible: scripts por fase, versiones "
            "fijadas, pruebas automáticas y resultados con hash. El repositorio, el informe y "
            "esta presentación están enlazados en la descripción. Gracias. ¿Preguntas?»"
        ),
        "apuntar": "El número 3 y, al final, la URL del repositorio en pantalla.",
    },
]

TIEMPOS = [
    ("1", "Portada", "Pregunta, alcance y autores", "0:00 - 0:25", "Mauricio"),
    ("2", "El problema", "Clasificación binaria sin fuga", "0:25 - 1:20", "Mauricio"),
    ("3", "Fuente y ética", "Basketball-Reference y sus límites", "1:20 - 2:05", "Mauricio"),
    ("4", "Fases I y II", "De 27 páginas a 805 × 52", "2:05 - 3:35", "Mauricio"),
    ("5", "Fase III", "Balance, correlaciones y deriva", "3:35 - 4:45", "Mauricio"),
    ("6", "Fase IV", "Pipeline, protocolos y anti-fuga", "4:45 - 5:55", "Santiago"),
    ("7", "Fase IV", "Validación cruzada", "5:55 - 6:35", "Santiago"),
    ("8", "Fase IV", "Test temporal", "6:35 - 7:25", "Santiago"),
    ("9", "Fase IV", "Errores e importancia", "7:25 - 8:15", "Santiago"),
    ("10", "Límites", "Lo que el modelo no puede decir", "8:15 - 9:05", "Santiago"),
    ("11", "Conclusiones", "Tres ideas y cierre", "9:05 - 10:00", "Ambos"),
]

ANEXOS = [
    ("12", "Ejecución y repositorio", "27/27 descargas, 805 × 52, hash, 23 pruebas"),
    ("13", "Métricas exactas del test", "Accuracy, precisión, recall, F1, ROC-AUC y Brier"),
]

# --------------------------------------------------------------------------
# Estilos
# --------------------------------------------------------------------------

S = {
    "titulo": ParagraphStyle(
        "titulo", fontName="Helvetica-Bold", fontSize=21, leading=25,
        textColor=AZUL, spaceAfter=2,
    ),
    "bajada": ParagraphStyle(
        "bajada", fontName="Helvetica", fontSize=10.5, leading=14.5,
        textColor=GRIS, spaceAfter=10,
    ),
    "h2": ParagraphStyle(
        "h2", fontName="Helvetica-Bold", fontSize=12, leading=15,
        textColor=AZUL, spaceBefore=8, spaceAfter=6,
    ),
    "cuerpo": ParagraphStyle(
        "cuerpo", fontName="Helvetica", fontSize=9.8, leading=14.2,
        textColor=HexColor("#24485C"), alignment=TA_LEFT,
    ),
    "celda": ParagraphStyle(
        "celda", fontName="Helvetica", fontSize=8.4, leading=10.6,
        textColor=HexColor("#24485C"),
    ),
    "celda_b": ParagraphStyle(
        "celda_b", fontName="Helvetica-Bold", fontSize=8.4, leading=10.6,
        textColor=AZUL,
    ),
    "num": ParagraphStyle(
        "num", fontName="Helvetica-Bold", fontSize=13, leading=15,
        textColor=HexColor("#FFFFFF"), alignment=1,
    ),
    "slide_t": ParagraphStyle(
        "slide_t", fontName="Helvetica-Bold", fontSize=15, leading=18,
        textColor=AZUL,
    ),
    "meta": ParagraphStyle(
        "meta", fontName="Helvetica-Bold", fontSize=8.2, leading=10,
        textColor=VERDE,
    ),
    "etiqueta": ParagraphStyle(
        "etiqueta", fontName="Helvetica-Bold", fontSize=7.6, leading=9,
        textColor=GRIS_CLARO, spaceBefore=5, spaceAfter=2,
    ),
    "decir": ParagraphStyle(
        "decir", fontName="Helvetica", fontSize=9.9, leading=14.6,
        textColor=HexColor("#1B3A4B"),
    ),
    "nota": ParagraphStyle(
        "nota", fontName="Helvetica-Oblique", fontSize=8.8, leading=12.2,
        textColor=GRIS,
    ),
    "mini": ParagraphStyle(
        "mini", fontName="Helvetica", fontSize=8.8, leading=12.6,
        textColor=HexColor("#24485C"),
    ),
}


class NumberedCanvas(canvas.Canvas):
    """Dibuja el pie con «página N de M» sin conocer el total de antemano."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._states: list[dict] = []

    def showPage(self):  # noqa: N802
        self._states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._states)
        for state in self._states:
            self.__dict__.update(state)
            self._pie(total)
            super().showPage()
        super().save()

    def _pie(self, total: int) -> None:
        self.saveState()
        self.setStrokeColor(LINEA)
        self.setLineWidth(0.6)
        self.line(MARGEN_L, MARGEN_B - 0.55 * cm, ANCHO - MARGEN_R, MARGEN_B - 0.55 * cm)
        self.setFont("Helvetica", 7.4)
        self.setFillColor(GRIS_CLARO)
        self.drawString(MARGEN_L, MARGEN_B - 0.95 * cm, "Guion de la presentación · NBA y playoffs 2000-2026")
        self.drawRightString(
            ANCHO - MARGEN_R, MARGEN_B - 0.95 * cm, f"{self._pageNumber} / {total}"
        )
        self.restoreState()


CIFRAS = [
    ("Validación cruzada", "F1 0,912 ± 0,009 · ROC-AUC 0,970 (logística optimizada)"),
    ("Test temporal, base 0,50", "F1 0,879 · accuracy 0,862 · ROC-AUC 0,946 · Brier 0,099"),
    ("Test temporal, optimizado 0,50", "F1 0,866 · accuracy 0,848 · ROC-AUC 0,942 · Brier 0,097"),
    ("Test temporal, optimizado 0,46", "F1 0,880 · TN 75 · FP 23 · FN 6 · TP 106"),
    ("Línea base trivial", "F1 0,696 · accuracy 0,533 · ROC-AUC 0,500"),
    ("Variables", "16 predictoras; dataset 805 × 52; SHA-256 c04704d9...1f9ea3ea9"),
    ("Sensibilidad", "Sin VIF mayor a 10: F1 0,893 · con valores absolutos: F1 0,908"),
]


def tabla_cifras() -> Table:
    filas = [[Paragraph("Bloque", S["celda_b"]), Paragraph("Cifras", S["celda_b"])]]
    for bloque, cifras in CIFRAS:
        filas.append([Paragraph(bloque, S["celda"]), Paragraph(cifras, S["celda"])])
    tabla = Table(filas, colWidths=[4.8 * cm, UTIL - 4.8 * cm], repeatRows=1)
    estilo = [
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#E8F0F6")),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#B9CBD8")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    for i in range(1, len(filas)):
        if i % 2 == 0:
            estilo.append(("BACKGROUND", (0, i), (-1, i), HexColor("#F7FAFC")))
    tabla.setStyle(TableStyle(estilo))
    return tabla


def _caja_uso() -> Table:
    """Explica en una caja cómo se lee cada bloque del guion."""
    filas = [
        [Paragraph("<b>SE VE</b>", S["mini"]), Paragraph("Lo que aparece en la diapositiva.", S["mini"])],
        [Paragraph("<b>DECIR</b>", S["mini"]), Paragraph("El texto literal. Se puede leer tal cual.", S["mini"])],
        [Paragraph("<b>APUNTAR</b>", S["mini"]), Paragraph("Qué señalar con el cursor mientras se habla.", S["mini"])],
    ]
    tabla = Table(filas, colWidths=[2.4 * cm, UTIL - 2.4 * cm - 0.6 * cm])
    tabla.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), FONDO),
                ("LINEBEFORE", (0, 0), (0, -1), 3, VERDE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 9),
                ("RIGHTPADDING", (0, 0), (-1, -1), 9),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return KeepTogether(
        [
            Paragraph("Cómo se lee este guion", S["h2"]),
            tabla,
            Spacer(1, 5),
            Paragraph(
                "Regla de oro: una idea por diapositiva. No leer la diapositiva; decir la idea y "
                "señalar la figura o el número que la respalda.",
                S["nota"],
            ),
        ]
    )


def bloque_slide(s: dict) -> KeepTogether:
    badge = Table([[Paragraph(str(s["n"]), S["num"])]], colWidths=[0.86 * cm], rowHeights=[0.86 * cm])
    badge.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), AZUL),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    cab = Table(
        [[badge, Paragraph(s["titulo"], S["slide_t"])]],
        colWidths=[1.15 * cm, UTIL - 1.15 * cm],
    )
    cab.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )

    caja = Table([[Paragraph(s["decir"], S["decir"])]], colWidths=[UTIL])
    caja.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), FONDO),
                ("LINEBEFORE", (0, 0), (0, -1), 3, VERDE),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )

    return KeepTogether(
        [
            Spacer(1, 8),
            cab,
            Paragraph(f"{s['tiempo']}  ·  {s['quien']}", S["meta"]),
            Spacer(1, 6),
            Paragraph("SE VE", S["etiqueta"]),
            Paragraph(s["ver"], S["cuerpo"]),
            Spacer(1, 6),
            Paragraph("DECIR", S["etiqueta"]),
            caja,
            Spacer(1, 5),
            Paragraph("APUNTAR", S["etiqueta"]),
            Paragraph(s["apuntar"], S["nota"]),
            Spacer(1, 10),
        ]
    )


def tabla_tiempos() -> Table:
    filas = [[
        Paragraph("#", S["celda_b"]),
        Paragraph("Diapositiva", S["celda_b"]),
        Paragraph("Idea central", S["celda_b"]),
        Paragraph("Minutos", S["celda_b"]),
        Paragraph("Quién", S["celda_b"]),
    ]]
    for n, diapo, idea, tiempo, quien in TIEMPOS:
        filas.append(
            [
                Paragraph(n, S["celda"]),
                Paragraph(diapo, S["celda"]),
                Paragraph(idea, S["celda"]),
                Paragraph(tiempo, S["celda"]),
                Paragraph(quien, S["celda"]),
            ]
        )
    tabla = Table(
        filas,
        colWidths=[0.8 * cm, 4.3 * cm, 6.3 * cm, 2.7 * cm, 2.6 * cm],
        repeatRows=1,
    )
    estilo = [
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#E8F0F6")),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#B9CBD8")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    for i in range(1, len(filas)):
        if i % 2 == 0:
            estilo.append(("BACKGROUND", (0, i), (-1, i), HexColor("#F7FAFC")))
    tabla.setStyle(TableStyle(estilo))
    return tabla


def construir() -> None:
    doc = BaseDocTemplate(
        str(OUT_PATH),
        pagesize=A4,
        leftMargin=MARGEN_L,
        rightMargin=MARGEN_R,
        topMargin=MARGEN_T,
        bottomMargin=MARGEN_B,
        title="Guion de la presentación — NBA playoffs",
        author="Mauricio Villafañe; Santiago de la Hoz",
        subject="Ciencia de Datos con Python — guion del video",
        creator="tools/build_guion.py",
    )
    frame = Frame(MARGEN_L, MARGEN_B, UTIL, ALTO - MARGEN_T - MARGEN_B, id="cuerpo")
    doc.addPageTemplates([PageTemplate(id="una-columna", frames=[frame])])

    historia = [
        Paragraph("Guion de la presentación", S["titulo"]),
        Paragraph(
            "Video de sustentación · 10:00 minutos · 11 diapositivas narradas y 2 anexos",
            S["bajada"],
        ),
        Paragraph(
            "A es Mauricio (diapositivas 1 a 5). B es Santiago (6 a 10). El cierre, 11, lo hacen "
            "los dos. Una idea por diapositiva: señalarla y decirla, sin leer el texto en pantalla.",
            S["cuerpo"],
        ),
        Spacer(1, 12),
        Paragraph("Mapa de tiempos", S["h2"]),
        tabla_tiempos(),
        Spacer(1, 4),
        Paragraph(
            "Los anexos 12 y 13 no se narran: quedan listos por si el docente pide pruebas.",
            S["nota"],
        ),
        Spacer(1, 14),
        _caja_uso(),
        PageBreak(),
    ]

    for s in SLIDES:
        historia.append(bloque_slide(s))

    # Anexos
    filas = [[Paragraph("Anexo", S["celda_b"]), Paragraph("Para qué sirve", S["celda_b"])]]
    for n, titulo, uso in ANEXOS:
        filas.append([Paragraph(f"{n} · {titulo}", S["celda"]), Paragraph(uso, S["celda"])])
    tabla_anexos = Table(filas, colWidths=[6.2 * cm, UTIL - 6.2 * cm])
    tabla_anexos.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), HexColor("#E8F0F6")),
                ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#B9CBD8")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )

    historia += [
        Paragraph("Anexos: no se narran", S["h2"]),
        tabla_anexos,
        Spacer(1, 4),
        Paragraph(
            "Si preguntan por el hash del dataset: c04704d9ecdd511b24bd81b1aef73250082e02bd1f63a501eed900f1f9ea3ea9. "
            "Si preguntan por sensibilidad: sin las variables con VIF mayor a 10 el F1 baja a 0,893; "
            "con valores absolutos en vez de relativos, a 0,908.",
            S["nota"],
        ),
        PageBreak(),
        Paragraph("Cifras para responder preguntas", S["h2"]),
        tabla_cifras(),
        Spacer(1, 8),
        Paragraph("Antes de grabar", S["h2"]),
        Paragraph(
            "1. Abrir la presentación en pantalla completa, sin barra de herramientas.<br/>"
            "2. Probar micrófono y compartir pantalla a 1080p.<br/>"
            "3. Ensayar una vez con cronómetro: si pasa de 10:30, recortar ejemplos, no resultados.<br/>"
            "4. Tener el repositorio abierto en el navegador para el cierre.<br/>"
            "5. Grabar cámara al inicio y al final, y hacer zoom a las figuras de las diapositivas 5 y 9.",
            S["mini"],
        ),
        Paragraph("Después de grabar", S["h2"]),
        Paragraph(
            "1. Subir a YouTube como <b>No listado</b> o <b>Público</b>, nunca «Privado».<br/>"
            "2. Título: «¿Qué estadísticas explican que un equipo de la NBA llegue a playoffs? — Sustentación».<br/>"
            "3. Descripción con integrantes, institución, repositorio y atribución a Sports Reference.<br/>"
            "4. Abrir el enlace en incógnito y comprobar que se reproduce.<br/>"
            "5. Enviar la URL para regenerar el PDF final del informe y actualizar el README.",
            S["mini"],
        ),
        Paragraph("Cómo se regenera este guion", S["h2"]),
        Paragraph(
            "&nbsp;&nbsp;&nbsp;&nbsp;&amp; .\\.venv\\Scripts\\python.exe tools\\build_guion.py",
            ParagraphStyle(
                "cmd", fontName="Courier", fontSize=8.6, leading=12,
                textColor=HexColor("#24485C"), backColor=HexColor("#F5F7F9"),
                borderPadding=(5, 6, 5, 6),
            ),
        ),
    ]

    doc.build(historia, canvasmaker=NumberedCanvas)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    construir()
    from pypdf import PdfReader

    reader = PdfReader(str(OUT_PATH))
    print(f"PDF: {OUT_PATH}")
    print(f"Páginas: {len(reader.pages)}")
    print(f"Peso: {OUT_PATH.stat().st_size / 1024:.0f} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
