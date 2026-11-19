"""Genera la presentación horizontal (16:9) del video de sustentación.

Uso:
    & .\\.venv\\Scripts\\python.exe tools\\build_slides.py

Salida: docs/PRESENTACION_VIDEO.pdf (13 páginas: 11 narradas + 2 anexos).
Requiere Google Chrome o Microsoft Edge (impresión headless) y pypdf.
No re-ejecuta el pipeline ni modifica cifras: solo maqueta figuras y métricas ya
registradas en outputs/ y outputs_corrida2_16vars_fase4/.
"""

from __future__ import annotations

import base64
import subprocess
import sys
import tempfile
from pathlib import Path

from pypdf import PdfReader, PdfWriter

ROOT = Path(__file__).resolve().parents[1]
OUT_PATH = ROOT / "docs" / "PRESENTACION_VIDEO.pdf"
REPO = "https://github.com/ctlucifer1504-bit/proyecto_ciencia_de_datos"
TOTAL = 13

CHROME_CANDIDATES = [
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    Path("/usr/bin/google-chrome"),
    Path("/usr/bin/chromium"),
]

CSS = """
@page { size: 13.333in 7.5in; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  font-family: "Segoe UI", Helvetica, Arial, sans-serif;
  color: #17313f;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}
a { color: inherit; text-decoration: none; }
.slide {
  position: relative;
  width: 13.333in;
  height: 7.5in;
  padding: 0.42in 0.55in 0.42in;
  overflow: hidden;
  background: #ffffff;
  page-break-after: always;
  break-after: page;
}
.slide:last-child { page-break-after: auto; break-after: auto; }
.head {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  border-bottom: 2pt solid #0b3d5c;
  padding-bottom: 7pt;
}
.kicker {
  font-size: 8.8pt;
  letter-spacing: 1.4pt;
  text-transform: uppercase;
  color: #5c7280;
  font-weight: 600;
}
h2 {
  font-size: 24pt;
  line-height: 1.06;
  color: #0b3d5c;
  margin: 4pt 0 0;
  font-weight: 700;
  letter-spacing: -0.2pt;
}
.pageno { font-size: 19pt; color: #c6d5df; font-weight: 700; line-height: 1; }
.content {
  height: 5.5in;
  padding-top: 0.2in;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.foot {
  position: absolute;
  left: 0.55in;
  right: 0.55in;
  bottom: 0.17in;
  display: flex;
  justify-content: space-between;
  font-size: 7.8pt;
  color: #8a9aa6;
  letter-spacing: 0.3pt;
}
h3 { font-size: 12.5pt; color: #0b3d5c; margin: 0 0 6pt; }
p { margin: 0 0 7pt; font-size: 11.5pt; line-height: 1.35; }
small { font-size: 9pt; }
strong { color: #0b3d5c; }

.g2 { display: grid; grid-template-columns: 1fr 1fr; gap: 0.22in; }
.g2.duo { grid-template-columns: 0.82fr 1.18fr; }
.g3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.2in; }
.g4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.16in; }
.stack { display: flex; flex-direction: column; gap: 0.14in; }

.stat {
  background: #f3f8fb;
  border-left: 4pt solid #0b3d5c;
  padding: 11pt 14pt;
}
.stat .n { font-size: 30pt; font-weight: 700; color: #0b3d5c; line-height: 0.95; }
.stat .l {
  font-size: 8.2pt;
  text-transform: uppercase;
  letter-spacing: 0.9pt;
  color: #5c7280;
  margin-top: 5pt;
  font-weight: 600;
}
.stat .s { font-size: 9pt; color: #5c7280; margin-top: 4pt; line-height: 1.3; }
.stat.warn { border-left-color: #b45309; background: #fdf6ec; }
.stat.warn .n { color: #b45309; }
.stat.ok { border-left-color: #0f766e; background: #f1faf8; }
.stat.ok .n { color: #0f766e; }

.fig {
  background: #ffffff;
  border: 1pt solid #d7e2ea;
  padding: 7pt 8pt 5pt;
  display: flex;
  flex-direction: column;
  min-height: 0;
}
.imgh {
  height: 3.55in;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}
.imgh img { max-width: 100%; max-height: 100%; object-fit: contain; }
.fig figcaption {
  font-size: 8.3pt;
  color: #5c7280;
  line-height: 1.25;
  margin-top: 5pt;
  border-top: 0.6pt solid #e4edf3;
  padding-top: 4pt;
}
.fig.wide .imgh { height: 3.05in; }
.fig.med .imgh { height: 3.85in; }
.fig.tall .imgh { height: 4.2in; }

.flow { display: flex; align-items: stretch; justify-content: center; gap: 10pt; }
.node {
  flex: 1;
  background: #f3f8fb;
  border: 1pt solid #c9dbe8;
  padding: 14pt 10pt;
  text-align: center;
  font-size: 12pt;
  font-weight: 600;
  color: #0b3d5c;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
.node small { display: block; font-weight: 400; color: #5c7280; margin-top: 4pt; }
.node.alt { background: #0b3d5c; border-color: #0b3d5c; color: #ffffff; }
.node.alt small { color: #cfe0ec; }
.arrow {
  display: flex;
  align-items: center;
  font-size: 20pt;
  color: #9db4c5;
  font-weight: 700;
}

.chips { display: flex; flex-wrap: wrap; gap: 8pt; }
.chip {
  background: #eef5f9;
  border: 0.8pt solid #c9dbe8;
  color: #0b3d5c;
  font-size: 9.2pt;
  padding: 5pt 9pt;
  font-weight: 600;
}
.chip.amber { background: #fdf6ec; border-color: #e8c79a; color: #9a4a06; }
.chip.green { background: #eef8f5; border-color: #a9d5cc; color: #0f665e; }

.callout {
  border-left: 4pt solid #b45309;
  background: #fdf6ec;
  padding: 9pt 12pt;
  font-size: 10.5pt;
  color: #6b3a10;
  line-height: 1.3;
}
.callout.blue { border-left-color: #0b3d5c; background: #f3f8fb; color: #24485c; }

table { width: 100%; border-collapse: collapse; font-size: 9.6pt; }
th, td { border: 0.6pt solid #b9cbd8; padding: 6pt 7pt; text-align: left; }
th { background: #e8f0f6; color: #0b3d5c; font-weight: 600; }
td.num, th.num { text-align: right; font-variant-numeric: tabular-nums; }
tr.total td { background: #f3f8fb; font-weight: 700; }

.mono {
  font-family: Consolas, "Courier New", monospace;
  font-size: 8.8pt;
  line-height: 1.45;
  background: #f5f7f9;
  border-left: 3pt solid #9fb3c8;
  padding: 8pt 11pt;
  white-space: pre-wrap;
  color: #24485c;
}
.mono .ok { color: #0f665e; font-weight: 700; }

/* Portada */
.title-slide { height: 100%; display: flex; gap: 0.45in; align-items: stretch; }
.ts-left { flex: 1.55; display: flex; flex-direction: column; }
.ts-right {
  flex: 0.75;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 9pt;
  border-left: 0.8pt solid #d7e2ea;
  padding-left: 0.32in;
}
.inst { font-size: 11.5pt; letter-spacing: 1.1pt; color: #0b3d5c; font-weight: 700; }
.fac { font-size: 9.2pt; color: #5c7280; margin-top: 3pt; }
.rule { width: 1.35in; border-top: 2.4pt solid #0b3d5c; margin: 0.33in 0 0.3in; }
.ts-left h1 {
  font-size: 31pt;
  line-height: 1.1;
  color: #0b3d5c;
  margin: 0 0 0.18in;
  letter-spacing: -0.4pt;
}
.ts-left h1 em { font-style: normal; color: #0f766e; }
.sub { font-size: 12pt; color: #33556b; margin-bottom: 0.26in; }
.authors { font-size: 14pt; color: #17313f; margin-bottom: 5pt; font-weight: 600; }
.meta { font-size: 9.2pt; color: #5c7280; line-height: 1.45; }
.big-stat { border-left: 4pt solid #0b3d5c; padding-left: 12pt; }
.big-stat span { display: block; font-size: 30pt; font-weight: 700; color: #0b3d5c; line-height: 1; }
.big-stat small {
  display: block;
  font-size: 8.2pt;
  text-transform: uppercase;
  letter-spacing: 0.9pt;
  color: #5c7280;
  margin-top: 4pt;
}
.ts-quote {
  margin-top: 0.26in;
  border-left: 3pt solid #0f766e;
  padding-left: 12pt;
  font-size: 10.5pt;
  line-height: 1.4;
  color: #33556b;
  max-width: 5.6in;
}
.phases { display: flex; align-items: center; gap: 6pt; margin-top: 0.2in; }
.phases span {
  font-size: 7.8pt;
  text-transform: uppercase;
  letter-spacing: 0.6pt;
  color: #5c7280;
  background: #f3f8fb;
  border: 0.6pt solid #d7e2ea;
  padding: 4pt 7pt;
  font-weight: 600;
}
.phases i { color: #9db4c5; font-style: normal; font-size: 10pt; }
.ts-foot {
  margin-top: auto;
  font-size: 8.2pt;
  color: #6b7c8a;
  border-top: 0.6pt solid #d7e2ea;
  padding-top: 8pt;
  line-height: 1.45;
}
.ts-foot b { color: #0b3d5c; font-weight: 600; }

/* Comparaciones */
.cmp { display: flex; flex-direction: column; gap: 10pt; }
.cmp-row {
  display: grid;
  grid-template-columns: 2.35in 0.75in 0.35in 0.95in 0.9in;
  align-items: center;
  gap: 8pt;
  background: #f7fafc;
  border: 0.8pt solid #d7e2ea;
  padding: 10pt 12pt;
}
.cmp-name { font-size: 10.5pt; font-weight: 600; color: #33556b; }
.cmp-row .v { font-size: 16pt; font-weight: 600; color: #5c7280; text-align: right; }
.cmp-row .v.big { font-size: 22pt; color: #0b3d5c; }
.cmp-row .ar { text-align: center; color: #9db4c5; font-size: 15pt; }
.delta { font-size: 11pt; font-weight: 700; color: #0f766e; text-align: right; }
.delta.neg { color: #b45309; }

.kpi { text-align: center; background: #f3f8fb; border-top: 4pt solid #0b3d5c; padding: 12pt 8pt; }
.kpi .v { font-size: 28pt; font-weight: 700; color: #0b3d5c; line-height: 1; }
.kpi .l { font-size: 8.5pt; text-transform: uppercase; letter-spacing: 0.7pt; color: #5c7280; margin-top: 6pt; }
.kpi .s { font-size: 9pt; color: #5c7280; margin-top: 3pt; }
.kpi.amber { border-top-color: #b45309; background: #fdf6ec; }
.kpi.amber .v { color: #b45309; }

.bigq {
  font-size: 15pt;
  line-height: 1.35;
  color: #33556b;
  border-left: 4pt solid #0f766e;
  padding-left: 14pt;
}
.num-badge {
  display: inline-flex;
  width: 26pt;
  height: 26pt;
  align-items: center;
  justify-content: center;
  background: #0b3d5c;
  color: #fff;
  font-weight: 700;
  font-size: 12pt;
  margin-right: 9pt;
  flex: none;
}
.concl { display: flex; flex-direction: column; gap: 8pt; }
.concl-row {
  display: flex;
  align-items: flex-start;
  background: #f7fafc;
  border: 0.8pt solid #d7e2ea;
  padding: 9pt 12pt;
}
.concl-row h3 { margin: 0 0 2pt; font-size: 12pt; }
.concl-row p { margin: 0; font-size: 9.8pt; color: #466072; }
.close-strip {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 0.8pt solid #d7e2ea;
  margin-top: 0.16in;
  padding-top: 9pt;
}
.close-strip .url { font-size: 10pt; color: #0b3d5c; font-weight: 600; }
.close-strip .bye { font-size: 15pt; font-weight: 700; color: #0b3d5c; }
"""


def data_uri(relative: str) -> str:
    payload = (ROOT / relative).read_bytes()
    return "data:image/png;base64," + base64.b64encode(payload).decode("ascii")


def fig(relative: str, caption: str, extra: str = "") -> str:
    return (
        f'<figure class="fig {extra}"><div class="imgh">'
        f'<img src="{data_uri(relative)}" alt="">'
        f"</div><figcaption>{caption}</figcaption></figure>"
    )


def slide(num: int, kicker: str, title: str, body: str) -> str:
    return f"""<section class="slide">
  <header class="head">
    <div><div class="kicker">{kicker}</div><h2>{title}</h2></div>
    <div class="pageno">{num:02d}</div>
  </header>
  <div class="content">{body}</div>
  <footer class="foot"><span>NBA y playoffs · 2000–2026</span><span>{num:02d} / {TOTAL}</span></footer>
</section>"""


def build_html() -> str:
    slides: list[str] = []

    # 1. Portada
    slides.append(f"""<section class="slide">
  <div class="title-slide">
    <div class="ts-left">
      <div class="inst">UNIVERSIDAD AMERICANA DE BARRANQUILLA</div>
      <div class="fac">Facultad de Ingeniería de Sistemas · Ciencia de Datos con Python</div>
      <div class="rule"></div>
      <h1>¿Qué estadísticas explican que un equipo de la NBA llegue a <em>playoffs</em>?</h1>
      <p class="sub">805 equipo-temporadas · 27 temporadas · 16 predictores</p>
      <p class="authors">Mauricio Villafañe · Santiago de la Hoz</p>
      <p class="meta">Docente: Edgar Morillo Vergel · 7.º semestre<br>Barranquilla · 19 de noviembre de 2026</p>
      <div class="ts-quote">«No usamos victorias ni margen de puntos: son la respuesta, no el perfil estadístico que queremos estudiar.»</div>
      <div class="phases">
        <span>I · Scraping</span><i>→</i><span>II · Limpieza</span><i>→</i><span>III · EDA</span><i>→</i><span>IV · Modelado</span>
      </div>
      <div class="ts-foot">
        <b>Repositorio:</b> <a href="{REPO}">{REPO}</a><br>
        <b>Datos:</b> Sports Reference LLC / Basketball-Reference.com
      </div>
    </div>
    <div class="ts-right">
      <div class="big-stat"><span>805</span><small>equipo-temporada</small></div>
      <div class="big-stat"><span>27</span><small>temporadas</small></div>
      <div class="big-stat"><span>16</span><small>predictores</small></div>
      <div class="big-stat"><span>2</span><small>clases: 1 / 0</small></div>
    </div>
  </div>
</section>""")

    # 2. Problema
    slides.append(slide(2, "El problema", "Predecir playoffs sin mirar el marcador", """
<div class="g3" style="margin-bottom:0.2in">
  <div class="stat"><div class="n">805</div><div class="l">equipo-temporada</div><div class="s">Todas las filas de 2000 a 2026</div></div>
  <div class="stat"><div class="n">53,7 %</div><div class="l">clasificó a playoffs</div><div class="s">46,3 % no clasificó: no hay desbalance severo</div></div>
  <div class="stat"><div class="n">16</div><div class="l">estadísticas de juego</div><div class="s">Relativas al promedio de su temporada</div></div>
</div>
<div class="flow" style="margin-bottom:0.18in">
  <div class="node">Perfil del equipo<small>16 estadísticas, sin victorias ni margen</small></div>
  <div class="arrow">→</div>
  <div class="node alt">Modelo<small>clasificación binaria</small></div>
  <div class="arrow">→</div>
  <div class="node">1 = clasifica<small>0 = no clasifica</small></div>
</div>
<div class="callout"><strong>Excluimos W, L y NRtg:</strong> contienen la respuesta. Si el modelo los usa, no aprende: copia.</div>
"""))

    # 3. Fuente y ética
    slides.append(slide(3, "Fuente y ética", "Un dato público, recolectado con respeto", """
<div class="g2">
  <div class="stack">
    <div class="stat"><div class="l">Fuente</div><div class="n" style="font-size:22pt">Basketball-Reference</div><div class="s">Una página por temporada: <strong>/leagues/NBA_AAAA.html</strong></div></div>
    <div class="callout blue" style="font-size:10pt">
      <strong>Datos: Sports Reference LLC / Basketball-Reference.com.</strong><br>
      El repositorio no redistribuye HTML, CSV crudos, el dataset ni predicciones fila a fila.
    </div>
    <div class="stat ok"><div class="n" style="font-size:20pt">Datos agregados</div><div class="s">Por equipo y temporada. Sin información personal ni médica.</div></div>
  </div>
  <div class="stack">
    <h3>Reglas de recolección</h3>
    <div class="flow" style="gap:8pt">
      <div class="node" style="padding:11pt 8pt"><strong style="font-size:17pt">4 s</strong><small>entre peticiones</small></div>
      <div class="node" style="padding:11pt 8pt"><strong style="font-size:17pt">Caché</strong><small>reanudar sin repetir</small></div>
    </div>
    <div class="flow" style="gap:8pt">
      <div class="node" style="padding:11pt 8pt"><strong style="font-size:17pt">UA</strong><small>User-Agent identificable</small></div>
      <div class="node" style="padding:11pt 8pt;background:#fdf6ec;border-color:#e8c79a"><strong style="font-size:17pt;color:#9a4a06">403/429</strong><small>detener, no evadir</small></div>
    </div>
    <p style="font-size:10pt;color:#5c7280">Sin CAPTCHA, sin autenticación, sin reintentos agresivos. Si el sitio bloquea, se usa lo ya descargado.</p>
  </div>
</div>
"""))

    # 4. Fases I y II
    slides.append(slide(4, "Fases I y II · Datos", "De 27 páginas a 805 × 52", """
<div class="flow" style="margin-bottom:0.18in">
  <div class="node">27 páginas<small>una por temporada</small></div>
  <div class="arrow">→</div>
  <div class="node">54 tablas<small>Advanced + Per Game</small></div>
  <div class="arrow">→</div>
  <div class="node alt">805 × 52<small>dataset limpio</small></div>
</div>
<div class="g2">
  <div class="stack">
    <h3>Fase I · scraping</h3>
    <div class="chips">
      <span class="chip">4 s entre peticiones</span>
      <span class="chip amber">403/429 → detener</span>
      <span class="chip">Título y 29/30 equipos</span>
      <span class="chip green">27/27 descargas «ok»</span>
      <span class="chip">Tablas en comentarios HTML</span>
    </div>
    <p style="font-size:10pt;color:#5c7280">El bucle valida, registra y permite reanudar con caché: no es una lista de URLs.</p>
  </div>
  <div class="stack">
    <h3>Fase II · limpieza</h3>
    <div class="g2" style="gap:0.1in">
      <div class="stat ok" style="padding:9pt 12pt"><div class="n">0</div><div class="l">duplicados</div></div>
      <div class="stat ok" style="padding:9pt 12pt"><div class="n">0</div><div class="l">infinitos</div></div>
      <div class="stat" style="padding:9pt 12pt"><div class="n">8</div><div class="l">nulos</div><div class="s">Solo asistencia (4 + 4)</div></div>
      <div class="stat warn" style="padding:9pt 12pt"><div class="n">53</div><div class="l">casos límite</div><div class="s">Récord perdedor o dif. negativo</div></div>
    </div>
  </div>
</div>
<div class="callout blue" style="margin-top:0.16in"><strong>No imputamos en Fase II:</strong> si hubiera nulos en predictores, la mediana se aprende <strong>solo del train</strong>, dentro del pipeline. Asistencia queda fuera por nulos y por causalidad inversa.</div>
"""))

    # 5. Fase III
    slides.append(slide(5, "Fase III · EDA", "El rival a vencer es el 53,7 %", f"""
<div class="g2 duo">
  {fig("outputs_corrida2_16vars/figures/01_balance_clases_16vars.png", "Balance del objetivo: 432 clasificados (53,7 %) y 373 no clasificados (46,3 %).", "tall")}
  {fig("outputs_corrida2_16vars/figures/05_correlacion_con_objetivo_16vars.png", "Correlación de cada predictor con playoffs. La defensa domina en signo negativo.", "tall")}
</div>
<div class="chips" style="margin-top:0.14in">
  <span class="chip green">def_eFG% −0,582</span>
  <span class="chip">off_eFG% +0,511</span>
  <span class="chip">Age +0,452</span>
  <span class="chip">off_eFG% ↔ 3P% = 0,709</span>
  <span class="chip">3PAr 0,167 → 0,415: todo es relativo</span>
  <span class="chip amber">«Siempre clasifica» acierta 53,7 %</span>
</div>
"""))

    # 6. Metodología
    slides.append(slide(6, "Fase IV · Modelado", "Un pipeline, dos protocolos, cero fuga", """
<div class="g2">
  <div class="stack">
    <h3>Pipeline: todo se ajusta dentro del fold</h3>
    <div class="flow" style="flex-direction:column;gap:6pt">
      <div class="node" style="padding:9pt">Imputación por mediana<small>aprendida solo del train</small></div>
      <div class="arrow" style="justify-content:center">↓</div>
      <div class="node" style="padding:9pt">Escalado<small>media y desviación del train</small></div>
      <div class="arrow" style="justify-content:center">↓</div>
      <div class="node alt" style="padding:9pt">Regresión logística · Random Forest<small>8 y 48 combinaciones de hiperparámetros</small></div>
    </div>
    <div class="chips">
      <span class="chip green">Split antes de ajustar</span>
      <span class="chip green">Nada elegido con test</span>
      <span class="chip green">Umbral en validación interna</span>
    </div>
  </div>
  <div class="stack">
    <h3>Dos lecturas del mismo problema</h3>
    <div class="stat"><div class="l">Protocolo principal · temporal</div><div class="n" style="font-size:17pt">2000–2019 → 2020–2026</div><div class="s">210 filas de test · 5 folds agrupados por temporada</div></div>
    <div class="stat"><div class="l">Protocolo secundario · estratificado</div><div class="n" style="font-size:17pt">80 / 20</div><div class="s">161 filas de test · replica el protocolo histórico</div></div>
    <div class="callout blue"><strong>StratifiedGroupKFold(5):</strong> ningún fold comparte una temporada entre train y validación.</div>
  </div>
</div>
"""))

    # 7. CV
    slides.append(slide(7, "Fase IV · Validación cruzada", "En validación cruzada, la grilla sí mejora", """
<div class="cmp" style="margin-bottom:0.2in">
  <div class="cmp-row">
    <div class="cmp-name">Regresión logística</div>
    <div class="v">0,908</div><div class="ar">→</div><div class="v big">0,912</div><div class="delta">+0,004</div>
  </div>
  <div class="cmp-row">
    <div class="cmp-name">Random Forest</div>
    <div class="v">0,865</div><div class="ar">→</div><div class="v big">0,870</div><div class="delta">+0,005</div>
  </div>
</div>
<div class="g3">
  <div class="kpi"><div class="v">0,970</div><div class="l">ROC-AUC</div><div class="s">Logística optimizada</div></div>
  <div class="kpi"><div class="v">±0,009</div><div class="l">desviación del F1</div><div class="s">La mejora cabe dentro de una desviación</div></div>
  <div class="kpi"><div class="v">5</div><div class="l">folds agrupados</div><div class="s">Por temporada, sin compartir año</div></div>
</div>
<div class="callout blue" style="margin-top:0.2in"><strong>La logística gana en ambos protocolos:</strong> mejor F1, mejor ROC-AUC y más estable entre folds. El Random Forest se queda en 0,870.</div>
"""))

    # 8. Test
    slides.append(slide(8, "Fase IV · Test temporal", "En test, la mejora no se replica", """
<div class="g3" style="margin-bottom:0.18in">
  <div class="kpi"><div class="v">0,879</div><div class="l">F1 · base 0,50</div><div class="s">ROC-AUC 0,946 · recall 0,938</div></div>
  <div class="kpi amber"><div class="v">0,866</div><div class="l">F1 · optimizado 0,50</div><div class="s">ROC-AUC 0,942 · cae frente a la base</div></div>
  <div class="kpi"><div class="v">0,880</div><div class="l">F1 · optimizado 0,46</div><div class="s">ROC-AUC 0,942 · umbral secundario</div></div>
</div>
<div class="flow" style="margin-bottom:0.16in">
  <div class="node" style="padding:10pt">CV<small>+0,004</small></div>
  <div class="arrow">→</div>
  <div class="node" style="padding:10pt;background:#fdf6ec;border-color:#e8c79a;color:#9a4a06">Test, umbral 0,50<small style="color:#9a4a06">−0,013 en F1</small></div>
  <div class="arrow">→</div>
  <div class="node" style="padding:10pt">Test, umbral 0,46<small>+0,001 frente a la base</small></div>
</div>
<div class="callout"><strong>No forzamos una mejora que no existe.</strong> El modelo base ya era fuerte y la grilla tenía poco margen: 805 filas y señales claras. Reportarlo es el resultado.</div>
"""))

    # 9. Errores e importancia
    slides.append(slide(9, "Fase IV · Errores e importancia", "Dónde acierta y qué pesa", f"""
<div class="g2">
  {fig("outputs_corrida2_16vars_fase4/figures/modelado_matriz_confusion_temporal_16vars.png", "Matriz de confusión en test temporal, umbral 0,46: TN 75, FP 23, FN 6, TP 106. ROC-AUC 0,942.", "med")}
  {fig("outputs_corrida2_16vars_fase4/figures/modelado_importancia_temporal_16vars.png", "Importancia por permutación en validación interna. Se muestran las 12 de 16 variables con mayor caída del F1.", "med")}
</div>
<div class="chips" style="margin-top:0.14in">
  <span class="chip green">106 de 112 clasificados</span>
  <span class="chip amber">23 falsos positivos</span>
  <span class="chip">6 se escapan</span>
  <span class="chip">Precisión 0,822 · recall 0,946</span>
  <span class="chip green">def_eFG% 0,113</span>
  <span class="chip">def_TOV% 0,065</span>
</div>
"""))

    # 10. Límites
    slides.append(slide(10, "Límites", "Lo que este modelo no puede decir", """
<div class="g2" style="gap:0.18in">
  <div class="stat"><div class="n" style="font-size:19pt">Observacional</div><div class="l">no causal</div><div class="s">La importancia por permutación mide asociación; no prueba que cambiar una estadística cambie la clasificación.</div></div>
  <div class="stat"><div class="n" style="font-size:19pt">210 filas</div><div class="l">test temporal</div><div class="s">Suficiente para comparar, corto para conclusiones finas. El intervalo de confianza no es estrecho.</div></div>
  <div class="stat warn"><div class="n" style="font-size:19pt">TRB · VIF 20,9</div><div class="l">multicolinealidad</div><div class="s">El coeficiente de una variable no se lee de forma aislada; la sensibilidad sin VIF&gt;10 baja a F1 0,893.</div></div>
  <div class="stat warn"><div class="n" style="font-size:19pt">0,46 vs 0,57</div><div class="l">umbral inestable</div><div class="s">El umbral cambia entre protocolos. Por eso la cifra titular es 0,50 y el resto es análisis secundario.</div></div>
</div>
<div class="callout blue" style="margin-top:0.2in"><strong>Play-in desde 2021:</strong> «clasificar» ya no significa lo mismo en todas las temporadas. Se documenta, no se corrige con una variable inventada.</div>
"""))

    # 11. Conclusiones y cierre
    slides.append(slide(11, "Conclusiones", "Tres ideas y cierre", f"""
<div class="concl">
  <div class="concl-row"><span class="num-badge">1</span><div><h3>Sí se puede predecir con alta discriminación</h3><p>ROC-AUC 0,946 y F1 0,879 con el modelo base y umbral 0,50, usando solo 16 estadísticas relativas.</p></div></div>
  <div class="concl-row"><span class="num-badge">2</span><div><h3>La señal está en la defensa</h3><p>def_eFG% (0,113) y def_TOV% (0,065) pesan más que el ataque en el modelo multivariado.</p></div></div>
  <div class="concl-row"><span class="num-badge">3</span><div><h3>Optimizar no garantiza mejorar fuera de muestra</h3><p>La grilla sube +0,004 en CV y baja −0,013 en test con el umbral 0,50. Es un resultado honesto, no un fracaso que se esconde.</p></div></div>
</div>
<div class="close-strip">
  <div>
    <div class="kicker" style="margin-bottom:4pt">Repositorio · informe · video</div>
    <div class="url"><a href="{REPO}">https://github.com/ctlucifer1504-bit/proyecto_ciencia_de_datos</a></div>
  </div>
  <div class="bye">Gracias · ¿Preguntas?</div>
</div>
<div class="ts-foot" style="border-top:0.6pt solid #d7e2ea;padding-top:7pt;font-size:8pt;color:#6b7c8a;margin-top:0.12in">
  <strong>Datos:</strong> Sports Reference LLC / Basketball-Reference.com. · Código MIT · Documentación CC BY 4.0.
</div>
"""))

    # 12. Anexo: evidencias
    slides.append(slide(12, "Anexo · Evidencia", "Ejecución y repositorio", f"""
<div class="g2">
  <div>
    <table>
      <thead><tr><th>Evidencia</th><th>Valor</th></tr></thead>
      <tbody>
        <tr><td>Temporadas descargadas</td><td><strong>27 / 27 «ok»</strong></td></tr>
        <tr><td>Fragmentos</td><td>54 (2 tablas × 27)</td></tr>
        <tr><td>Dataset final</td><td>805 filas × 52 columnas</td></tr>
        <tr><td>Duplicados / infinitos</td><td>0 / 0</td></tr>
        <tr><td>SHA-256</td><td style="font-size:7.6pt">c04704d9…1f9ea3ea9</td></tr>
        <tr><td>Pruebas</td><td>23 ejecutadas · 13 omitidas sin datos</td></tr>
        <tr><td>Repositorio</td><td>PUBLIC · main · 144 archivos</td></tr>
      </tbody>
    </table>
    <p style="font-size:8.4pt;color:#5c7280;margin-top:6pt">El repositorio no incluye HTML, CSV crudos, dataset ni predicciones fila a fila.</p>
  </div>
  <div class="stack">
    <div class="mono">$ python -m unittest discover -s tests
Ran 23 tests in 0.166s
<span class="ok">OK</span></div>
    <div class="mono">$ Get-FileHash data\\processed\\nba_teams_clean.csv
c04704d9ecdd511b24bd81b1aef73250082e02bd1f63a501eed900f1f9ea3ea9</div>
    <div class="callout blue" style="font-size:9.4pt">Clon limpio verificado: 23 pruebas ejecutadas, 13 omitidas por ausencia de datos, sin fallos.</div>
  </div>
</div>
<div class="ts-foot" style="border-top:0.6pt solid #d7e2ea;padding-top:7pt;font-size:8pt;color:#6b7c8a;margin-top:0.12in">
  <a href="{REPO}">{REPO}</a>
</div>
"""))

    # 13. Anexo: métricas
    slides.append(slide(13, "Anexo · Evidencia", "Métricas exactas del test temporal", """
<table style="font-size:10.2pt">
  <thead><tr><th>Configuración</th><th class="num">Accuracy</th><th class="num">Precisión</th><th class="num">Recall</th><th class="num">F1</th><th class="num">ROC-AUC</th><th class="num">Brier</th></tr></thead>
  <tbody>
    <tr><td>Línea base trivial</td><td class="num">0,533</td><td class="num">0,533</td><td class="num">1,000</td><td class="num">0,696</td><td class="num">0,500</td><td class="num">0,467</td></tr>
    <tr><td>Logística base · 0,50</td><td class="num">0,862</td><td class="num">0,827</td><td class="num">0,938</td><td class="num"><strong>0,879</strong></td><td class="num"><strong>0,946</strong></td><td class="num">0,099</td></tr>
    <tr><td>Logística optimizada · 0,50</td><td class="num">0,848</td><td class="num">0,817</td><td class="num">0,920</td><td class="num">0,866</td><td class="num">0,942</td><td class="num">0,097</td></tr>
    <tr class="total"><td>Logística optimizada · 0,46</td><td class="num">0,862</td><td class="num">0,822</td><td class="num">0,946</td><td class="num">0,880</td><td class="num">0,942</td><td class="num">0,097</td></tr>
  </tbody>
</table>
<div class="g3" style="margin-top:0.2in">
  <div class="kpi"><div class="v">210</div><div class="l">filas de test</div><div class="s">Temporadas 2020–2026</div></div>
  <div class="kpi"><div class="v">112</div><div class="l">clasificados reales</div><div class="s">98 no clasificados</div></div>
  <div class="kpi"><div class="v">0,46</div><div class="l">umbral secundario</div><div class="s">Elegido en validación interna</div></div>
</div>
<div class="callout blue" style="margin-top:0.18in"><strong>Cómo se lee:</strong> la línea base trivial ya acierta 53,3 % y su F1 es 0,696. El modelo base sube a F1 0,879; la grilla no lo supera en test con 0,50.</div>
"""))

    body = "\n".join(slides)
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Presentación de sustentación — NBA playoffs</title>
<style>{CSS}</style>
</head>
<body>
{body}
</body>
</html>
"""


def find_browser() -> Path:
    for candidate in CHROME_CANDIDATES:
        if candidate.is_file():
            return candidate
    raise SystemExit("No se encontró Chrome ni Edge para imprimir el PDF.")


def print_pdf(browser: Path, html_path: Path, pdf_path: Path) -> None:
    cmd = [
        str(browser),
        "--headless=new",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check",
        "--no-pdf-header-footer",
        "--print-to-pdf-no-header",
        f"--print-to-pdf={pdf_path}",
        "--virtual-time-budget=20000",
        "--allow-file-access-from-files",
        html_path.as_uri(),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if not pdf_path.is_file():
        raise SystemExit(
            "La impresión a PDF falló.\n"
            f"stdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-2000:]}"
        )


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    temp_dir = Path(tempfile.mkdtemp(prefix="presentacion_"))
    html_path = temp_dir / "presentacion.html"
    raw_pdf = temp_dir / "presentacion.pdf"
    html_path.write_text(build_html(), encoding="utf-8")

    browser = find_browser()
    print(f"Navegador: {browser}")
    print(f"HTML: {html_path}")
    print_pdf(browser, html_path, raw_pdf)

    reader = PdfReader(str(raw_pdf))
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.add_metadata(
        {
            "/Title": "Presentación de sustentación — NBA playoffs",
            "/Author": "Mauricio Villafañe; Santiago de la Hoz",
            "/Subject": "Ciencia de Datos con Python — video de sustentación",
            "/Creator": "tools/build_slides.py",
        }
    )
    titles = [
        "Portada",
        "El problema",
        "Fuente y ética",
        "Fases I y II — Datos",
        "Fase III — EDA",
        "Fase IV — Metodología",
        "Fase IV — Validación cruzada",
        "Fase IV — Test temporal",
        "Fase IV — Errores e importancia",
        "Límites",
        "Conclusiones y cierre",
        "Anexo — Evidencias",
        "Anexo — Métricas exactas",
    ]
    for index, title in enumerate(titles[: len(reader.pages)]):
        writer.add_outline_item(title=title, page_number=index)
    with OUT_PATH.open("wb") as handle:
        writer.write(handle)

    result = PdfReader(str(OUT_PATH))
    width = float(result.pages[0].mediabox.width)
    height = float(result.pages[0].mediabox.height)
    print(f"PDF: {OUT_PATH}")
    print(f"Páginas: {len(result.pages)}")
    print(f"Tamaño: {width:.0f} × {height:.0f} pt ({width / 72:.2f} × {height / 72:.2f} in)")
    print(f"Peso: {OUT_PATH.stat().st_size / 1024:.0f} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
