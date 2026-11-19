# Datos — no incluidos en el repositorio

**Datos: Sports Reference LLC / Basketball-Reference.com.**

Este directorio está excluido del repositorio público. No se publican las páginas HTML,
los fragmentos, los CSV crudos ni el dataset procesado porque los datos pertenecen a
Sports Reference LLC y sus términos de uso restringen su redistribución. Las licencias
MIT y CC BY 4.0 del proyecto **no** se aplican a los datos.

## Cómo regenerarlos

Desde la raíz del proyecto, en este orden:

```powershell
& .\.venv\Scripts\python.exe scraping.py     # ~2 min; 27 páginas con pausa de 4 s
& .\.venv\Scripts\python.exe limpieza.py
& .\.venv\Scripts\python.exe exploracion.py
& .\.venv\Scripts\python.exe modelado.py
```

`scraping.py` crea:

- `data/raw/html/NBA_AAAA.html` — caché de las 27 páginas.
- `data/raw/fragments/advanced_AAAA.csv` y `per_game_AAAA.csv` — 54 fragmentos.
- `data/raw/advanced_raw_concat.csv` y `per_game_raw_concat.csv`.
- `outputs/logs/scrape_log.csv`.

`limpieza.py` crea `data/processed/nba_teams_clean.csv` (805 filas × 52 columnas).

## Verificación

```powershell
Get-FileHash data\processed\nba_teams_clean.csv -Algorithm SHA256
```

Hash esperado de la corrida documentada:

```text
c04704d9ecdd511b24bd81b1aef73250082e02bd1f63a501eed900f1f9ea3ea9
```

Si el hash no coincide, los resultados pueden diferir de los publicados. No se debe
presentar una corrida distinta como si fuera la documentada.

## Condiciones de uso

- El sitio limita a ~20 peticiones por minuto; el script usa pausas de 4 s y caché.
- Si el sitio responde 403/429, **detenerse** y usar los HTML ya guardados; no evadir
  autenticación ni CAPTCHA.
- No redistribuir los datos. Ver `docs/CONSIDERACIONES_LEGALES.md`.
- No usar los datos para crear una base de datos que compita con Sports Reference.
