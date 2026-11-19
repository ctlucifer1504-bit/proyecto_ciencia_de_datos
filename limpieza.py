"""
FASE II - Limpieza y manipulacion avanzada
Entrada : data/raw/fragments/advanced_AAAA.csv y per_game_AAAA.csv (Fase I)
Salida  : data/processed/nba_teams_clean.csv
          outputs/metrics/limpieza_resumen.csv  (antes/despues, para el PDF y el video)

Requisitos de la guia que cubre:
  - pd.concat() de los fragmentos
  - duplicados y NaN: conteo, decision justificada
  - conversion explicita de texto a numerico (con control de valores invalidos)
  - filtros con condiciones multiples (&, |) agrupadas con parentesis

Uso:  python limpieza.py
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

FRAGMENTS_DIR = Path("data/raw/fragments")
RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
METRICS_DIR = Path("outputs/metrics")

KEYS = ["season", "Team"]

# Columnas que deben ser numericas (se usa solo la interseccion con las existentes)
ADV_NUM = ["Age", "W", "L", "PW", "PL", "MOV", "SOS", "SRS", "ORtg", "DRtg", "NRtg",
           "Pace", "FTr", "3PAr", "TS%", "off_eFG%", "off_TOV%", "off_ORB%", "off_FT/FGA",
           "def_eFG%", "def_TOV%", "def_DRB%", "def_FT/FGA", "Attend.", "Attend./G"]
PG_NUM = ["G", "MP", "FG", "FGA", "FG%", "3P", "3PA", "3P%", "2P", "2PA", "2P%", "FT", "FTA",
          "FT%", "ORB", "DRB", "TRB", "AST", "STL", "BLK", "TOV", "PF", "PTS"]

SEP = "=" * 70


def title(text: str) -> None:
    print(f"\n{SEP}\n{text}\n{SEP}")


# --------------------------------------------------------------------------
# 1. Carga y concatenacion
# --------------------------------------------------------------------------
def load_fragments(kind: str) -> list[pd.DataFrame]:
    """Lee los fragmentos por temporada como TEXTO (dtype=str) para que la
    conversion de tipos de la seccion 4 sea explicita y auditable."""
    files = sorted(FRAGMENTS_DIR.glob(f"{kind}_*.csv"))
    if not files:
        raise FileNotFoundError(f"No hay fragmentos '{kind}_*.csv' en {FRAGMENTS_DIR}")
    # keep_default_na=False: solo la celda vacia cuenta como nulo; un texto como
    # "N/A" o "--" se conserva y la conversion numerica lo reportara.
    return [pd.read_csv(f, dtype=str, keep_default_na=False, na_values=[""]) for f in files]


def concat_fragments(fragments: list[pd.DataFrame], name: str) -> pd.DataFrame:
    """pd.concat apila los 27 DataFrames (uno por temporada).

    ignore_index=True: cada fragmento trae indice 0..29; sin esto el indice
    final tendria valores repetidos y .loc devolveria varias filas por etiqueta.
    join='outer' (por defecto): si una temporada no tuviera una columna, se
    conserva con NaN en vez de perder la columna para todas.
    """
    column_sets = {tuple(f.columns) for f in fragments}
    if len(column_sets) > 1:
        print(f"[AVISO] {name}: los fragmentos NO tienen las mismas columnas ({len(column_sets)} variantes)")
    df = pd.concat(fragments, ignore_index=True, join="outer")
    print(f"{name}: {len(fragments)} fragmentos -> {df.shape[0]} filas x {df.shape[1]} columnas")
    return df


# --------------------------------------------------------------------------
# 2. Inspeccion, duplicados y nulos
# --------------------------------------------------------------------------
def missing_report(df: pd.DataFrame) -> pd.Series:
    nulls = df.isna().sum()
    return nulls[nulls > 0].sort_values(ascending=False)


def remove_duplicates(df: pd.DataFrame, name: str) -> tuple[pd.DataFrame, dict]:
    """Un equipo solo puede aparecer una vez por temporada (clave: season + Team)."""
    dup_full = int(df.duplicated().sum())
    dup_key = int(df.duplicated(subset=KEYS).sum())
    out = df.drop_duplicates(subset=KEYS, keep="first").reset_index(drop=True)
    print(f"{name}: duplicados exactos={dup_full} | duplicados por (season, Team)={dup_key} "
          f"| filas {len(df)} -> {len(out)}")
    return out, {"duplicados_exactos": dup_full, "duplicados_clave": dup_key}


# --------------------------------------------------------------------------
# 3. Conversion explicita texto -> numerico
# --------------------------------------------------------------------------
def to_numeric_explicit(df: pd.DataFrame, columns: list[str], name: str) -> pd.DataFrame:
    """Convierte con pd.to_numeric(errors='coerce') y AUDITA: un valor invalido
    pasa a NaN, nunca a 0. Se reporta cuantos NaN nuevos aparecen por la
    conversion (lo esperado es 0)."""
    df = df.copy()
    present = [c for c in columns if c in df.columns]
    missing = sorted(set(columns) - set(present))
    if missing:
        print(f"[AVISO] {name}: columnas esperadas que no existen: {missing}")

    problems = []
    for col in present:
        raw = df[col]
        # separadores de miles ("754,832") y espacios; '+12.8' lo entiende to_numeric
        cleaned = raw.astype("string").str.replace(",", "", regex=False).str.strip()
        converted = pd.to_numeric(cleaned, errors="coerce")
        new_nan = int(converted.isna().sum() - raw.isna().sum())
        if new_nan > 0:
            bad = sorted(set(raw[converted.isna() & raw.notna()].astype(str)))[:5]
            problems.append((col, new_nan, bad))
        df[col] = converted.astype("float64")

    print(f"{name}: {len(present)} columnas convertidas a float64")
    if problems:
        for col, n, bad in problems:
            print(f"  [REVISAR] {col}: {n} valores no numericos pasaron a NaN. Ejemplos: {bad}")
    else:
        print("  Sin valores invalidos: la conversion no creo NaN nuevos")
    return df


# --------------------------------------------------------------------------
# Pipeline completo
# --------------------------------------------------------------------------
def run_cleaning() -> pd.DataFrame:
    for folder in (RAW_DIR, PROCESSED_DIR, METRICS_DIR):
        folder.mkdir(parents=True, exist_ok=True)
    summary: dict[str, object] = {}

    # ---- 1. Concatenacion -------------------------------------------------
    title("1. pd.concat de los fragmentos por temporada")
    adv = concat_fragments(load_fragments("advanced"), "advanced")
    pg = concat_fragments(load_fragments("per_game"), "per_game")

    # Copia de datos crudos: la limpieza no toca estos archivos
    adv.to_csv(RAW_DIR / "advanced_raw_concat.csv", index=False)
    pg.to_csv(RAW_DIR / "per_game_raw_concat.csv", index=False)
    summary.update(filas_antes_advanced=len(adv), filas_antes_per_game=len(pg),
                   columnas_antes_advanced=adv.shape[1], columnas_antes_per_game=pg.shape[1])

    # ---- 2. Calidad inicial ----------------------------------------------
    title("2. Calidad inicial: nulos y duplicados")
    print("Nulos por columna (advanced):")
    print(missing_report(adv).to_string() if len(missing_report(adv)) else "  ninguno")
    print("Nulos por columna (per_game):")
    print(missing_report(pg).to_string() if len(missing_report(pg)) else "  ninguno")
    summary["nulos_antes_total"] = int(adv.isna().sum().sum() + pg.isna().sum().sum())

    adv, d1 = remove_duplicates(adv, "advanced")
    pg, d2 = remove_duplicates(pg, "per_game")
    summary["duplicados_eliminados"] = (d1["duplicados_clave"] + d2["duplicados_clave"])

    # ---- 3. Consistencia entre tablas ------------------------------------
    title("3. Consistencia: el asterisco de playoffs debe coincidir en ambas tablas")
    check = adv[KEYS + ["playoffs"]].merge(pg[KEYS + ["playoffs"]], on=KEYS,
                                           how="outer", suffixes=("_adv", "_pg"),
                                           indicator=True)
    only_one = int((check["_merge"] != "both").sum())
    disagree = int((check["playoffs_adv"] != check["playoffs_pg"]).sum())
    print(f"Equipos que estan en una tabla y no en la otra: {only_one}")
    print(f"Equipos con 'playoffs' distinto entre tablas   : {disagree}")
    if only_one or disagree:
        print("  [REVISAR] los nombres de equipo no coinciden entre tablas; no se debe continuar")

    # ---- 4. Tipos numericos ----------------------------------------------
    title("4. Conversion explicita de texto a numerico")
    adv = to_numeric_explicit(adv, ADV_NUM, "advanced")
    pg = to_numeric_explicit(pg, PG_NUM, "per_game")
    for df_ in (adv, pg):
        df_["playoffs"] = pd.to_numeric(df_["playoffs"], errors="raise").astype(int)
        df_["season"] = pd.to_numeric(df_["season"], errors="raise").astype(int)

    # ---- 5. Union de las dos tablas --------------------------------------
    title("5. Union advanced + per_game")
    # Se descartan de per_game las columnas repetidas o sin valor analitico.
    # 'Rk' se elimina de ambas: en 'advanced' el ranking sigue el rendimiento
    # (revela el resultado) y no es una estadistica de juego.
    pg_small = pg.drop(columns=["Rk", "playoffs", "source_url", "scraped_at"], errors="ignore")
    adv_small = adv.drop(columns=["Rk", "Arena", "source_url", "scraped_at"], errors="ignore")
    df = adv_small.merge(pg_small, on=KEYS, how="inner", validate="one_to_one")
    print(f"Filas tras la union: {len(df)} (advanced={len(adv)}, per_game={len(pg)})")

    # Variable derivada solo para exploracion (NO usar como predictor: usa W y L)
    df["win_pct"] = df["W"] / (df["W"] + df["L"])

    # ---- 6. Nulos: decision justificada ----------------------------------
    title("6. Tratamiento de nulos")
    nulls_after = missing_report(df)
    print("Nulos restantes por columna:")
    print(nulls_after.to_string() if len(nulls_after) else "  ninguno")
    assert df["playoffs"].notna().all(), "La variable objetivo no puede tener nulos"
    print(
        "\nDecision: la variable objetivo ('playoffs') no tiene nulos. Los nulos que\n"
        "queden en predictores NO se imputan aqui: se imputaran dentro del Pipeline de\n"
        "la Fase IV (mediana aprendida solo con el set de entrenamiento) para evitar\n"
        "fuga de datos. Eliminar filas no se justifica: cada fila es un equipo-temporada\n"
        "unico y son pocos registros."
    )
    summary["nulos_despues_total"] = int(df.isna().sum().sum())

    # ---- 7. Filtros con condiciones multiples ----------------------------
    title("7. Filtros compuestos con & y | (parentesis obligatorios)")
    # En pandas & y | tienen MAS precedencia que > < ==, asi que cada comparacion
    # va entre parentesis; sin ellos pandas lanza un error o filtra mal.
    cond_cinderella = (df["playoffs"] == 1) & ((df["win_pct"] < 0.5) | (df["NRtg"] < 0))
    cinderellas = df[cond_cinderella]
    print(f"Clasificaron a playoffs con record perdedor O diferencial negativo: {len(cinderellas)}")
    print(cinderellas[["season", "Team", "W", "L", "NRtg", "playoffs"]].head(8).to_string(index=False))
    assert (cinderellas["playoffs"] == 1).all()
    assert ((cinderellas["win_pct"] < 0.5) | (cinderellas["NRtg"] < 0)).all()

    # Cuantiles DENTRO de cada temporada: la eficiencia de la liga cambia con los
    # anios (ORtg medio ~100 en 2000 vs ~114 en 2025); un cuantil global mediria la epoca.
    q75_off = df.groupby("season")["ORtg"].transform(lambda s: s.quantile(0.75))
    q25_def = df.groupby("season")["DRtg"].transform(lambda s: s.quantile(0.25))
    cond_missed = (df["playoffs"] == 0) & ((df["ORtg"] >= q75_off) | (df["DRtg"] <= q25_def))
    missed = df[cond_missed]
    print(f"\nNO clasificaron pese a ataque top-25% O defensa top-25% DE SU TEMPORADA: {len(missed)}")
    print(missed[["season", "Team", "W", "L", "ORtg", "DRtg"]].head(8).to_string(index=False))
    assert (missed["playoffs"] == 0).all()
    summary.update(filtro_clasificados_record_perdedor=len(cinderellas),
                   filtro_buenos_que_no_clasificaron=len(missed))

    # ---- 8. Verificaciones finales ---------------------------------------
    title("8. Verificaciones finales")
    num = df.select_dtypes("number")
    n_inf = int(np.isinf(num).sum().sum())
    n_dup = int(df.duplicated(subset=KEYS).sum())
    print(f"Infinitos: {n_inf} | duplicados (season, Team): {n_dup}")
    print(f"Filas: {len(df)} | columnas: {df.shape[1]} | temporadas: {df['season'].nunique()}")
    print("Equipos por temporada (min/max):",
          df.groupby("season").size().min(), "/", df.groupby("season").size().max())
    print("\nBalance de la variable objetivo:")
    print(df["playoffs"].value_counts().rename({1: "clasifico", 0: "no clasifico"}).to_string())
    print((df["playoffs"].value_counts(normalize=True) * 100).round(1).to_string())
    summary.update(filas_final=len(df), columnas_final=df.shape[1],
                   infinitos=n_inf, duplicados_final=n_dup)

    # ---- 9. Guardado ------------------------------------------------------
    df.to_csv(PROCESSED_DIR / "nba_teams_clean.csv", index=False)
    pd.Series(summary, name="valor").to_csv(METRICS_DIR / "limpieza_resumen.csv")
    print(f"\nGuardado: {PROCESSED_DIR / 'nba_teams_clean.csv'}")
    print(f"Guardado: {METRICS_DIR / 'limpieza_resumen.csv'}")
    return df


if __name__ == "__main__":
    run_cleaning()
