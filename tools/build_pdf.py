"""Genera el PDF del informe final a partir de docs/INFORME_FINAL.md.

Uso:
    & .\\.venv\\Scripts\\python.exe tools\\build_pdf.py

Requiere Google Chrome o Microsoft Edge instalado (se usa en modo headless para
imprimir el HTML a PDF). Las dependencias Python (markdown, reportlab, pypdf) no
forman parte de los scripts del proyecto: solo se usan para construir el PDF.
"""

from __future__ import annotations

import html
import io
import re
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

import markdown
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
MD_PATH = ROOT / "docs" / "INFORME_FINAL.md"
OUT_PATH = ROOT / "docs" / "INFORME_FINAL_BORRADOR.pdf"

TITULO = "¿Qué estadísticas de juego explican que un equipo de la NBA llegue a playoffs?"
AUTORES = "Mauricio Villafañe · Santiago de la Hoz"
REPO = "https://github.com/ctlucifer1504-bit/proyecto_ciencia_de_datos"
VIDEO = "[ENLACE DE YOUTUBE: pendiente]"
FOOTER = "NBA y playoffs · Informe final"

CHROME_CANDIDATES = [
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    Path("/usr/bin/google-chrome"),
    Path("/usr/bin/chromium"),
]


def find_browser() -> Path:
    for candidate in CHROME_CANDIDATES:
        if candidate.is_file():
            return candidate
    raise SystemExit("No se encontró Chrome ni Edge para imprimir el PDF.")


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower()
    return re.sub(r"\s+", " ", text).strip()


def linkify(fragment: str) -> str:
    """Convierte URLs sueltas en enlaces, sin tocar bloques de código."""
    parts = re.split(r"(<code>.*?</code>|<pre>.*?</pre>)", fragment, flags=re.S)
    pattern = re.compile(r"(?<![\"'=])(https?://[^\s<>\"']+)")

    def replace(match: re.Match[str]) -> str:
        url = match.group(1)
        trailing = ""
        while url and url[-1] in ".,;:":
            trailing = url[-1] + trailing
            url = url[:-1]
        while url.endswith(")") and url.count("(") < url.count(")"):
            trailing = ")" + trailing
            url = url[:-1]
        return f'<a href="{url}">{url}</a>{trailing}'

    for index in range(0, len(parts), 2):
        parts[index] = pattern.sub(replace, parts[index])
    return "".join(parts)


CSS = """
@page { size: Letter; margin: 20mm 18mm 22mm 18mm; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body {
  font-family: Georgia, "Times New Roman", serif;
  font-size: 10.6pt; line-height: 1.45; color: #1a1a1a; margin: 0;
}
h1, h2, h3, h4 { font-family: "Segoe UI", Helvetica, Arial, sans-serif; color: #0b3d5c; }
h2 {
  font-size: 15pt; margin: 0 0 10pt; padding-bottom: 4pt;
  border-bottom: 1.2pt solid #0b3d5c;
  page-break-before: always; break-before: page;
}
h3 { font-size: 11.8pt; margin: 14pt 0 6pt; }
h4 { font-size: 10.6pt; margin: 12pt 0 5pt; }
p { margin: 0 0 7pt; text-align: left; orphans: 2; widows: 2; }
ul, ol { margin: 0 0 8pt 16pt; padding: 0; }
li { margin-bottom: 3pt; }
a { color: #0b5c8a; text-decoration: none; overflow-wrap: anywhere; }
hr { border: none; border-top: 0.6pt solid #c9d5df; margin: 12pt 0; }
code {
  font-family: Consolas, "Courier New", monospace; font-size: 9pt;
  background: #f2f5f8; padding: 1pt 3pt; border-radius: 2pt;
  overflow-wrap: anywhere;
}
pre {
  font-family: Consolas, "Courier New", monospace; font-size: 8.8pt;
  background: #f5f7f9; border-left: 3pt solid #9fb3c8;
  padding: 7pt 9pt; margin: 6pt 0 10pt; white-space: pre-wrap;
}
pre code { background: none; padding: 0; }
blockquote {
  margin: 8pt 0 10pt; padding: 6pt 10pt; background: #f4f8fb;
  border-left: 3pt solid #0b3d5c; font-size: 9.9pt;
}
blockquote p:last-child { margin-bottom: 0; }
table {
  width: 100%; border-collapse: collapse; margin: 6pt 0 12pt;
  font-family: "Segoe UI", Helvetica, Arial, sans-serif; font-size: 9.1pt;
}
thead { display: table-header-group; }
tr { break-inside: avoid; page-break-inside: avoid; }
th, td { border: 0.5pt solid #a9bccd; padding: 4pt 6pt; vertical-align: top; }
th { background: #e8f0f6; text-align: left; font-weight: 600; }
td { text-align: left; }
img { max-width: 100%; height: auto; display: block; margin: 8pt auto 4pt; }
p > em:only-child {
  display: block; text-align: left; color: #4a5a66; font-size: 8.8pt;
  border-left: 2pt solid #c9d5df; padding-left: 8pt; margin: 4pt 0 12pt;
}

/* Portada */
.cover { height: 200mm; display: flex; flex-direction: column; }
.cover-inst { font-family: "Segoe UI", Helvetica, sans-serif; font-size: 13pt;
  letter-spacing: 1.6pt; color: #0b3d5c; font-weight: 700; }
.cover-fac { font-family: "Segoe UI", Helvetica, sans-serif; font-size: 11pt;
  color: #33556b; margin-top: 3pt; }
.cover-rule { border-top: 2pt solid #0b3d5c; width: 38mm; margin: 22pt 0 26pt; }
.cover-kicker { font-family: "Segoe UI", Helvetica, sans-serif; font-size: 10pt;
  color: #6b7c8a; text-transform: uppercase; letter-spacing: 1.1pt; }
.cover-title { font-size: 26pt; line-height: 1.16; margin: 10pt 0 12pt; color: #0b3d5c; }
.cover-sub { font-family: "Segoe UI", Helvetica, sans-serif; font-size: 12pt;
  color: #33556b; margin-bottom: 30pt; }
.cover-authors { font-size: 14pt; margin-bottom: 6pt; }
.cover-meta { font-family: "Segoe UI", Helvetica, sans-serif; font-size: 10.2pt;
  color: #33556b; line-height: 1.6; }
.cover-links { margin-top: auto; border: 0.8pt solid #b8c9d8; background: #f6fafd;
  padding: 11pt 13pt; font-family: "Segoe UI", Helvetica, sans-serif; font-size: 10pt; }
.cover-links div { margin: 3pt 0; }
.cover-links span.tag { display: inline-block; width: 30mm; color: #6b7c8a;
  text-transform: uppercase; font-size: 8pt; letter-spacing: 0.7pt; }
.cover-note { margin-top: 12pt; font-family: "Segoe UI", Helvetica, sans-serif;
  font-size: 8.4pt; color: #6b7c8a; line-height: 1.5; }

/* Índice */
.toc { break-before: page; page-break-before: always; }
.toc h1 { font-family: "Segoe UI", Helvetica, sans-serif; font-size: 15pt;
  color: #0b3d5c; border-bottom: 1.2pt solid #0b3d5c; padding-bottom: 4pt;
  margin: 0 0 14pt; }
.toc ul { list-style: none; margin: 0; padding: 0; }
.toc li { display: flex; align-items: baseline; gap: 6pt; margin: 0 0 8pt; font-size: 10.4pt; }
.toc .dots { flex: 1; border-bottom: 0.8pt dotted #9aa9b5; }
.toc .pageno { font-family: "Segoe UI", Helvetica, sans-serif; font-size: 9.6pt; color: #33556b; }
"""


def build_html(body_html: str, toc_html: str) -> str:
    base = (ROOT / "docs").as_uri() + "/"
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<base href="{base}">
<title>{html.escape(TITULO)}</title>
<style>{CSS}</style>
</head>
<body>
<section class="cover">
  <div class="cover-inst">UNIVERSIDAD AMERICANA DE BARRANQUILLA</div>
  <div class="cover-fac">Facultad de Ingeniería de Sistemas</div>
  <div class="cover-rule"></div>
  <div class="cover-kicker">Ciencia de Datos con Python · 7.º semestre</div>
  <h1 class="cover-title">{html.escape(TITULO)}</h1>
  <div class="cover-sub">Informe final · 16 predictores · NBA 2000–2026</div>
  <div class="cover-authors">{html.escape(AUTORES)}</div>
  <div class="cover-meta">
    Docente: Edgar Morillo Vergel<br>
    Barranquilla, Colombia · 19 de noviembre de 2026
  </div>
  <div class="cover-links">
    <div><span class="tag">Repositorio</span><a href="{REPO}">{REPO}</a></div>
    <div><span class="tag">Video</span>{html.escape(VIDEO)}</div>
  </div>
  <div class="cover-note">
    Datos: Sports Reference LLC / Basketball-Reference.com.<br>
    Versión borrador del 18 de noviembre de 2026. El enlace de YouTube se añade en la
    versión final.
  </div>
</section>
<section class="toc">
  <h1>Índice</h1>
  {toc_html}
</section>
{body_html}
</body>
</html>
"""


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
        "--virtual-time-budget=15000",
        "--allow-file-access-from-files",
        html_path.as_uri(),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if not pdf_path.is_file():
        raise SystemExit(
            "La impresión a PDF falló.\n"
            f"stdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-2000:]}"
        )


def find_page_numbers(pdf_path: Path, entries: list[dict]) -> dict[str, int]:
    reader = PdfReader(str(pdf_path))
    texts = [normalize(page.extract_text() or "") for page in reader.pages]
    toc_index = next((i for i, text in enumerate(texts) if "indice" in text), 0)
    start = toc_index + 1
    numbers: dict[str, int] = {}
    cursor = start
    for entry in entries:
        key = normalize(entry["name"])
        for index in range(cursor, len(texts)):
            if key and key in texts[index]:
                numbers[entry["id"]] = index + 1
                cursor = index
                break
    return numbers


def add_footer(src: Path, dst: Path, numbers: dict[str, int], entries: list[dict]) -> None:
    writer = PdfWriter(clone_from=str(src))
    total = len(writer.pages)
    for index, page in enumerate(writer.pages):
        width = float(page.mediabox.width)
        if index > 0:
            buffer = io.BytesIO()
            pdf_canvas = canvas.Canvas(buffer, pagesize=(width, float(page.mediabox.height)))
            pdf_canvas.setStrokeGray(0.82)
            pdf_canvas.setLineWidth(0.5)
            pdf_canvas.line(51, 34, width - 51, 34)
            pdf_canvas.setFillGray(0.38)
            pdf_canvas.setFont("Helvetica", 7.4)
            pdf_canvas.drawString(51, 24, FOOTER)
            pdf_canvas.drawRightString(width - 51, 24, f"Página {index + 1} de {total}")
            pdf_canvas.save()
            buffer.seek(0)
            page.merge_page(PdfReader(buffer).pages[0])

    writer.add_metadata(
        {
            "/Title": TITULO,
            "/Author": "Mauricio Villafañe; Santiago de la Hoz",
            "/Subject": "Informe final — Ciencia de Datos con Python",
            "/Creator": "tools/build_pdf.py",
        }
    )
    for entry in entries:
        page_number = numbers.get(entry["id"])
        if page_number:
            writer.add_outline_item(title=entry["name"], page_number=page_number - 1)
    with dst.open("wb") as handle:
        writer.write(handle)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    text = MD_PATH.read_text(encoding="utf-8")
    marker = "## Enlaces de acceso"
    if marker not in text:
        marker = "## Resumen"
    if marker not in text:
        raise SystemExit("No se encontró el inicio del cuerpo en el informe.")
    body_md = text[text.index(marker):]

    md = markdown.Markdown(
        extensions=["tables", "fenced_code", "sane_lists", "attr_list", "toc"],
        extension_configs={"toc": {"toc_depth": "2-2", "title": ""}},
    )
    body_html = linkify(md.convert(body_md))
    entries = [token for token in md.toc_tokens if token["level"] == 2]

    def make_toc(numbers: dict[str, int] | None = None) -> str:
        rows = []
        for entry in entries:
            name = html.unescape(re.sub(r"<[^>]+>", "", entry["name"]))
            page = str(numbers.get(entry["id"], "")) if numbers else ""
            rows.append(
                f'<li><a href="#{entry["id"]}">{name}</a>'
                f'<span class="dots"></span><span class="pageno">{page}</span></li>'
            )
        return "<ul>" + "".join(rows) + "</ul>"

    temp_dir = Path(tempfile.mkdtemp(prefix="informe_pdf_"))
    browser = find_browser()

    first_html = temp_dir / "informe_paso1.html"
    first_pdf = temp_dir / "informe_paso1.pdf"
    first_html.write_text(build_html(body_html, make_toc()), encoding="utf-8")
    print(f"Navegador: {browser}")
    print(f"Paso 1: {first_html}")
    print_pdf(browser, first_html, first_pdf)

    numbers = find_page_numbers(first_pdf, entries)
    missing = [entry["name"] for entry in entries if entry["id"] not in numbers]
    if missing:
        print("Aviso: sin número de página para: " + ", ".join(missing))

    final_html = temp_dir / "informe_paso2.html"
    raw_pdf = temp_dir / "informe_paso2.pdf"
    final_html.write_text(build_html(body_html, make_toc(numbers)), encoding="utf-8")
    print_pdf(browser, final_html, raw_pdf)

    add_footer(raw_pdf, OUT_PATH, numbers, entries)

    result = PdfReader(str(OUT_PATH))
    pages = len(result.pages)
    print(f"PDF: {OUT_PATH}")
    print(f"Páginas: {pages}")
    print(f"Tamaño: {OUT_PATH.stat().st_size / 1024:.0f} KB")
    print("Índice:")
    for entry in entries:
        print(f"  {numbers.get(entry['id'], '?'):>3}  {entry['name']}")
    links = sum(len(page.get("/Annots", []) or []) for page in result.pages)
    print(f"Anotaciones (enlaces): {links}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
