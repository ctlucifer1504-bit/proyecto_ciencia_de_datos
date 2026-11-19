"""
FASE I - Extraccion automatizada (web scraping)
Proyecto: que estadisticas de equipo explican que un equipo NBA llegue a playoffs.

Fuente: Basketball-Reference, una pagina por temporada:
    https://www.basketball-reference.com/leagues/NBA_{year}.html

Que hace:
  1. Recorre las temporadas con un ciclo for (variable dinamica: year).
  2. Descarga cada pagina con pausas (limite del sitio: 20 peticiones/minuto)
     y la guarda en cache local para no volver a pedirla nunca.
  3. Extrae con pandas.read_html la tabla "Advanced Stats" y "Per Game Stats"
     (equipos), incluyendo tablas que el sitio esconde dentro de comentarios HTML.
  4. Consolida los fragmentos en un diccionario de listas de DataFrames y los
     guarda como CSV (datos crudos, como texto) mas un registro de extraccion.

La concatenacion (pd.concat), limpieza y conversion de tipos son de la Fase II.

Uso:
    pip install pandas requests lxml
    python scraping.py
"""
from __future__ import annotations

import logging
import re
import time
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path

import pandas as pd
import requests

# --------------------------------------------------------------------------
# Configuracion
# --------------------------------------------------------------------------
BASE_URL = "https://www.basketball-reference.com/leagues/NBA_{year}.html"
FIRST_SEASON = 2000      # temporada 1999-00
LAST_SEASON = 2026       # temporada 2025-26 (ya terminada)

SLEEP_SECONDS = 4        # pausa tras cada peticion real (maximo ~15 por minuto)
MAX_RETRIES = 2          # reintentos ante errores de red o respuestas 5xx
TIMEOUT = 30             # segundos

RAW_HTML_DIR = Path("data/raw/html")
FRAGMENTS_DIR = Path("data/raw/fragments")
LOGS_DIR = Path("outputs/logs")

# Identificate de forma honesta; cambia el correo por el tuyo.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; student-data-science-project; "
        "contact: https://github.com/ctlucifer1504-bit/proyecto_ciencia_de_datos)"
    )
}

# Columnas que identifican cada tabla (despues de aplanar los encabezados)
ADVANCED_COLS = {"Team", "Age", "ORtg", "DRtg", "Pace", "off_eFG%", "def_eFG%"}
PER_GAME_COLS = {"Team", "MP", "FG%", "3P%", "FT%", "TRB", "AST", "PTS"}

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("scraping")


class RateLimitedError(Exception):
    """El sitio respondio 403/429: hay que parar para no empeorar el bloqueo."""


# --------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------
def season_url(year: int) -> str:
    return BASE_URL.format(year=year)


def season_label(year: int) -> str:
    """2025 -> '2024-25' (formato que aparece en el titulo de la pagina)."""
    return f"{year - 1}-{str(year)[2:]}"


def download_html(year: int, session: requests.Session) -> tuple[str, bool]:
    """Devuelve (html, desde_cache). Solo hace peticion si no hay copia local."""
    cache_file = RAW_HTML_DIR / f"NBA_{year}.html"
    if cache_file.exists():
        return cache_file.read_text(encoding="utf-8"), True

    url = season_url(year)
    for attempt in range(1, MAX_RETRIES + 2):
        try:
            resp = session.get(url, headers=HEADERS, timeout=TIMEOUT)
        except requests.RequestException as exc:
            log.warning("Error de red en %s (intento %d): %s", url, attempt, exc)
            time.sleep(SLEEP_SECONDS * attempt)
            continue

        if resp.status_code in (403, 429):
            raise RateLimitedError(
                f"HTTP {resp.status_code} en {url}. Deten el script. Opcion sin "
                f"riesgo: abre la pagina en tu navegador, guardala como "
                f"{cache_file} y vuelve a ejecutar."
            )
        if resp.status_code == 200:
            resp.encoding = "utf-8"
            cache_file.write_text(resp.text, encoding="utf-8")
            time.sleep(SLEEP_SECONDS)
            return resp.text, False

        log.warning("HTTP %s en %s (intento %d)", resp.status_code, url, attempt)
        time.sleep(SLEEP_SECONDS * attempt)

    raise RuntimeError(f"No se pudo descargar {url} tras {MAX_RETRIES + 1} intentos")


def check_season_in_title(html: str, year: int) -> None:
    """Comprueba que la pagina corresponde a la temporada pedida."""
    match = re.search(r"<title>(.*?)</title>", html, flags=re.S | re.I)
    title = match.group(1) if match else ""
    if season_label(year) not in title:
        raise ValueError(f"El titulo '{title.strip()}' no corresponde a {season_label(year)}")


def read_all_tables(html: str) -> list[pd.DataFrame]:
    """Lee todas las tablas HTML, incluidas las escondidas en comentarios."""
    uncommented = html.replace("<!--", "").replace("-->", "")
    try:
        return pd.read_html(StringIO(uncommented))
    except ValueError:  # "No tables found"
        return []


def flatten_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Aplana encabezados de dos niveles.

    En 'Advanced Stats' hay dos grupos (Offense/Defense Four Factors) con
    columnas repetidas (eFG%, TOV%, FT/FGA); se prefijan con off_ y def_.
    """
    df = df.copy()
    if isinstance(df.columns, pd.MultiIndex):
        names = []
        for top, name in df.columns:
            top, name = str(top), str(name)
            if name.startswith("Unnamed") or not name.strip():
                names.append("")
            elif "Offense" in top:
                names.append(f"off_{name}")
            elif "Defense" in top:
                names.append(f"def_{name}")
            else:
                names.append(name)
        df.columns = names
    else:
        df.columns = [("" if str(c).startswith("Unnamed") else str(c)) for c in df.columns]
    df.columns = [c.strip() for c in df.columns]
    return df


def pick_table(tables: list[pd.DataFrame], required: set[str], per_game: bool = False):
    """Devuelve la primera tabla que contiene las columnas requeridas."""
    for raw in tables:
        flat = flatten_columns(raw)
        if not required.issubset(set(flat.columns)):
            continue
        if per_game:
            # Distingue 'Per Game' (MP ~ 240) de 'Totals' y 'Per 100 Poss' (MP ~ 19 700)
            if pd.to_numeric(flat["MP"], errors="coerce").mean() >= 1000:
                continue
        return flat
    return None


def tidy_team_table(df: pd.DataFrame, year: int, url: str, scraped_at: str) -> pd.DataFrame:
    """Limpieza minima de estructura (no de contenido): quita columnas
    espaciadoras y filas de promedio, y agrega trazabilidad.

    Los valores se guardan como texto; la conversion numerica explicita se hace
    en la Fase II. 'playoffs' sale del asterisco que el sitio pone a los equipos
    que clasificaron.
    """
    df = df.loc[:, [c for c in df.columns if c]]          # columnas sin nombre
    df = df[df["Team"].notna()]
    df = df[~df["Team"].astype(str).isin(["Team", "League Average"])].copy()

    team = df["Team"].astype(str).str.strip()
    df["playoffs"] = team.str.endswith("*").astype(int)
    df["Team"] = team.str.rstrip("*").str.strip()

    df = df.astype("string")
    df.insert(0, "season", year)
    df["source_url"] = url
    df["scraped_at"] = scraped_at
    return df.reset_index(drop=True)


def validate_fragment(df: pd.DataFrame, year: int, kind: str) -> None:
    """Controles minimos de calidad por fragmento."""
    n_teams = len(df)
    if not 29 <= n_teams <= 30:
        raise ValueError(f"{kind} {year}: {n_teams} filas (se esperaban 29 o 30)")
    n_playoffs = int(df["playoffs"].astype(int).sum())
    if not 14 <= n_playoffs <= 20:
        log.warning("%s %d: %d equipos marcados con playoffs (revisar)", kind, year, n_playoffs)


# --------------------------------------------------------------------------
# Bucle principal
# --------------------------------------------------------------------------
def run_scraping(first: int = FIRST_SEASON, last: int = LAST_SEASON):
    """Recorre las temporadas y devuelve (fragmentos, registro).

    fragmentos = {"advanced": [df_2000, df_2001, ...], "per_game": [...]}
    """
    for folder in (RAW_HTML_DIR, FRAGMENTS_DIR, LOGS_DIR):
        folder.mkdir(parents=True, exist_ok=True)

    fragments: dict[str, list[pd.DataFrame]] = {"advanced": [], "per_game": []}
    log_rows: list[dict] = []

    with requests.Session() as session:
        for year in range(first, last + 1):            # variable dinamica: year
            url = season_url(year)
            row = {"season": year, "url": url, "from_cache": None,
                   "advanced_rows": 0, "per_game_rows": 0,
                   "status": "ok", "error": ""}
            try:
                html, from_cache = download_html(year, session)
                row["from_cache"] = from_cache
                check_season_in_title(html, year)

                tables = read_all_tables(html)
                advanced = pick_table(tables, ADVANCED_COLS)
                per_game = pick_table(tables, PER_GAME_COLS, per_game=True)
                if advanced is None or per_game is None:
                    raise ValueError("No se encontro la tabla Advanced o Per Game (estructura cambiada?)")

                scraped_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
                adv_df = tidy_team_table(advanced, year, url, scraped_at)
                pg_df = tidy_team_table(per_game, year, url, scraped_at)
                validate_fragment(adv_df, year, "advanced")
                validate_fragment(pg_df, year, "per_game")

                fragments["advanced"].append(adv_df)
                fragments["per_game"].append(pg_df)
                adv_df.to_csv(FRAGMENTS_DIR / f"advanced_{year}.csv", index=False)
                pg_df.to_csv(FRAGMENTS_DIR / f"per_game_{year}.csv", index=False)
                row.update(advanced_rows=len(adv_df), per_game_rows=len(pg_df))
                log.info("%s OK | advanced=%d per_game=%d | cache=%s",
                         season_label(year), len(adv_df), len(pg_df), from_cache)

            except RateLimitedError as exc:
                row.update(status="bloqueado", error=str(exc))
                log_rows.append(row)
                log.error(str(exc))
                break                                   # no seguir insistiendo
            except Exception as exc:                    # un fallo no tumba todo el recorrido
                row.update(status="error", error=repr(exc))
                log.error("%s FALLO: %r", season_label(year), exc)
            log_rows.append(row)

    scrape_log = pd.DataFrame(log_rows)
    scrape_log.to_csv(LOGS_DIR / "scrape_log.csv", index=False)
    return fragments, scrape_log


if __name__ == "__main__":
    frags, scrape_log = run_scraping()
    print(scrape_log[["season", "status", "from_cache", "advanced_rows", "per_game_rows"]].to_string(index=False))
    ok = int((scrape_log["status"] == "ok").sum())
    print(f"\nTemporadas extraidas: {ok}/{len(scrape_log)}")
