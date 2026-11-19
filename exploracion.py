"""
FASE III - Analisis exploratorio de datos (EDA)
================================================
Entrada : data/processed/nba_teams_clean.csv  (Fase II, NO se modifica)
Salida  : outputs_corrida2_16vars/figures/*.png
          outputs_corrida2_16vars/metrics/*.csv
          outputs_corrida2_16vars/logs/*.log

Pregunta: que estadisticas de juego distinguen a los equipos que clasifican a
playoffs?

Unidad de analisis: equipo-temporada (una fila = un equipo en una temporada).
Variable objetivo: playoffs (1 = clasifico, 0 = no clasifico).

Idea clave: la NBA cambia con los anios (mas triples, mas ritmo, mas eficiencia).
Comparar un equipo de 2000 con uno de 2026 en valores absolutos mide la epoca,
no la calidad. Por eso cada predictor se usa tambien en version RELATIVA:
valor del equipo menos el promedio de la liga en esa temporada (sufijo _rel).

Esta corrida usa EXACTAMENTE 16 predictores (8 FOUR FACTORS + 8 OTHER_FEATURES).
No incorpora W, L, PW, PL, MOV, SOS, SRS, NRtg, win_pct, Rk, ORtg, DRtg,
Attend. ni Attend./G (fuga de informacion o causalidad inversa).

Uso:
    python exploracion.py
"""
from __future__ import annotations

import hashlib
import json
import logging
import platform
import sys
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")                     # guarda PNG sin abrir ventanas
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle

try:
    import sklearn
except ImportError:                       # no es necesario para el EDA
    sklearn = None

# --------------------------------------------------------------------------
# Rutas y constantes
# --------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data/processed/nba_teams_clean.csv"

# Carpeta independiente: NO se mezcla con outputs/ (corrida historica de 19 vars)
RUN_ID = "corrida2_16vars"
OUT_DIR = BASE_DIR / "outputs_corrida2_16vars"
FIG_DIR = OUT_DIR / "figures"
METRICS_DIR = OUT_DIR / "metrics"
LOG_DIR = OUT_DIR / "logs"

TARGET = "playoffs"
LABELS = {0: "No clasificó", 1: "Clasificó"}
COLORS = {0: "#D55E00", 1: "#0072B2"}      # naranja/azul (accesible)
ACCENT = "#0072B2"
NEGATIVE = "#D55E00"

# Predictores candidatos. NO incluye: W, L, PW, PL, MOV, SOS, SRS, NRtg,
# win_pct, Rk (revelan el resultado: fuga de datos), ORtg/DRtg (casi equivalen
# al margen de puntos; se evaluan aparte en la Fase IV) ni asistencia
# (causalidad inversa). Tampoco Team ni season como predictores.
FOUR_FACTORS = ["off_eFG%", "off_TOV%", "off_ORB%", "off_FT/FGA",
                "def_eFG%", "def_TOV%", "def_DRB%", "def_FT/FGA"]
OTHER_FEATURES = ["Age", "Pace", "3PAr", "3P%", "FT%", "AST", "BLK", "TRB"]
FEATURES = FOUR_FACTORS + OTHER_FEATURES
REL_FEATURES = [f"{c}_rel" for c in FEATURES]

FORBIDDEN = ["W", "L", "PW", "PL", "MOV", "SOS", "SRS", "NRtg", "win_pct",
             "Rk", "ORtg", "DRtg", "Attend.", "Attend./G"]
CONTEXT_COLS = ["Attend.", "Attend./G"]
DRIFT_COLS = ["3PAr", "Pace", "ORtg"]     # ORtg solo como contexto de epoca

UNITS = {
    "off_eFG%": "proporción (0-1)",
    "off_TOV%": "% de posesiones",
    "off_ORB%": "% de rebotes ofensivos",
    "off_FT/FGA": "razón FT/FGA",
    "def_eFG%": "proporción (0-1), menor es mejor",
    "def_TOV%": "% de posesiones, mayor es mejor",
    "def_DRB%": "% de rebotes defensivos",
    "def_FT/FGA": "razón FT/FGA, menor es mejor",
    "Age": "años (promedio ponderado)",
    "Pace": "posesiones por 48 min",
    "3PAr": "proporción de tiros de 3",
    "3P%": "proporción (0-1)",
    "FT%": "proporción (0-1)",
    "AST": "asistencias por partido",
    "BLK": "tapones por partido",
    "TRB": "rebotes por partido",
}

QUINTILES = ["Q1", "Q2", "Q3", "Q4", "Q5"]

LOG = logging.getLogger("eda16")


# --------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------
def rel(path: Path) -> str:
    """Ruta relativa a la raiz del proyecto, para logs reproducibles."""
    try:
        return str(path.relative_to(BASE_DIR))
    except ValueError:
        return str(path)


def setup_logging() -> Path:
    """Log simultaneo en consola y archivo, con fecha y hora."""
    for folder in (FIG_DIR, METRICS_DIR, LOG_DIR):
        folder.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = LOG_DIR / f"eda_16vars_{stamp}.log"

    LOG.setLevel(logging.INFO)
    LOG.handlers.clear()
    LOG.propagate = False

    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s",
                            "%Y-%m-%d %H:%M:%S")
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setFormatter(fmt)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    LOG.addHandler(fh)
    LOG.addHandler(sh)
    return log_path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def savefig(name: str) -> Path:
    """Guarda una figura PNG y la cierra (no abre ventanas)."""
    path = FIG_DIR / name
    plt.tight_layout()
    plt.savefig(path, dpi=160, bbox_inches="tight")
    plt.close()
    LOG.info("Figura guardada: %s", rel(path))
    return path


def save_table(df: pd.DataFrame, name: str, index: bool = False) -> Path:
    """Guarda una tabla CSV con BOM para que Excel respete los acentos."""
    path = METRICS_DIR / name
    df.to_csv(path, index=index, encoding="utf-8-sig")
    LOG.info("Tabla guardada: %s", rel(path))
    return path


def add_relative_features(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """valor - promedio de la liga en esa temporada (sufijo _rel).

    Se conserva la firma original porque modelado.py (Fase IV) importa esta
    funcion. No usa la variable objetivo, pero el promedio incluye todos los
    equipos de la temporada; es una transformacion transductiva que se declara
    como limitacion.
    """
    out = df.copy()
    for col in cols:
        out[f"{col}_rel"] = out[col] - out.groupby("season")[col].transform("mean")
    return out


def outlier_stats(s: pd.Series) -> dict[str, float | int]:
    """Conteo de atipicos con la regla 1.5 x IQR (no elimina nada)."""
    s = s.dropna()
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    low = int((s < lo).sum())
    high = int((s > hi).sum())
    return {
        "n_atipicos": low + high,
        "n_bajo": low,
        "n_alto": high,
        "limite_inferior": float(lo),
        "limite_superior": float(hi),
    }


def quadrant_masks(df: pd.DataFrame) -> dict[str, pd.Series]:
    """Cuadrantes de tiro efectivo propio vs permitido (valores relativos).

    y = def_eFG%_rel: por debajo de 0 significa que el rival tira peor que la
    media de la temporada, es decir, MEJOR defensa.
    """
    x = df["off_eFG%_rel"]
    y = df["def_eFG%_rel"]
    return {
        "Ataque > media; defensa mejor": (x > 0) & (y < 0),
        "Ataque > media; defensa peor": (x > 0) & (y >= 0),
        "Ataque <= media; defensa mejor": (x <= 0) & (y < 0),
        "Ataque <= media; defensa peor": (x <= 0) & (y >= 0),
    }


# --------------------------------------------------------------------------
# Carga y validacion (no imputa ni corrige datos)
# --------------------------------------------------------------------------
def load_data() -> pd.DataFrame:
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"No se encontro {DATA_FILE}. Ejecutar desde la raiz del proyecto "
            "y confirmar que la Fase II genero data/processed/nba_teams_clean.csv"
        )

    df = pd.read_csv(DATA_FILE)

    missing = [c for c in FEATURES + [TARGET, "season", "Team"] if c not in df.columns]
    if missing:
        raise KeyError(f"Faltan columnas en {DATA_FILE}: {missing}")

    if len(FEATURES) != 16:
        raise ValueError(f"Se esperaban 16 predictores y hay {len(FEATURES)}")
    if len(set(FEATURES)) != len(FEATURES):
        raise ValueError("Hay predictores duplicados en FEATURES")

    overlap = sorted(set(FEATURES) & set(FORBIDDEN))
    if overlap:
        raise ValueError(f"Predictores prohibidos por fuga de datos: {overlap}")

    non_numeric = [c for c in FEATURES + [TARGET, "season"]
                   if not pd.api.types.is_numeric_dtype(df[c])]
    if non_numeric:
        raise TypeError(f"Columnas que deberian ser numericas y no lo son: {non_numeric}")

    if df.duplicated(["season", "Team"]).any():
        raise ValueError("Hay duplicados en la clave (season, Team)")

    if df[TARGET].isna().any():
        raise ValueError("La variable objetivo tiene valores faltantes")

    if not set(df[TARGET].unique()).issubset({0, 1}):
        raise ValueError(f"La variable objetivo no esta codificada 0/1: {sorted(df[TARGET].unique())}")

    return df


# --------------------------------------------------------------------------
# Tablas
# --------------------------------------------------------------------------
def build_quality_table(df: pd.DataFrame) -> pd.DataFrame:
    """Calidad de cada columna relevante: nulos, infinitos, constantes, rango."""
    rows = []
    for col in FEATURES + [TARGET, "season"] + CONTEXT_COLS:
        if col not in df.columns:
            continue
        s = df[col]
        if col in FEATURES:
            role = "predictor"
        elif col == TARGET:
            role = "variable objetivo"
        elif col == "season":
            role = "clave temporal"
        else:
            role = "contexto (excluida del modelo)"

        numeric = pd.api.types.is_numeric_dtype(s)
        rows.append({
            "variable": col,
            "rol": role,
            "unidad": UNITS.get(col, "temporada" if col == "season" else
                                "0/1" if col == TARGET else "espectadores"),
            "tipo": str(s.dtype),
            "n": int(s.notna().sum()),
            "nulos": int(s.isna().sum()),
            "pct_nulos": round(100 * s.isna().mean(), 2),
            "infinitos": int(np.isinf(s).sum()) if numeric else 0,
            "valores_unicos": int(s.nunique(dropna=True)),
            "constante": bool(s.nunique(dropna=True) <= 1),
            "min": s.min() if numeric else np.nan,
            "max": s.max() if numeric else np.nan,
        })
    return pd.DataFrame(rows)


def build_descriptives(df: pd.DataFrame, cols: list[str], name: str) -> pd.DataFrame:
    """Estadisticas descriptivas + IQR, sesgo, curtosis y atipicos."""
    desc = df[cols].describe().T
    desc["iqr"] = desc["75%"] - desc["25%"]
    desc["sesgo"] = df[cols].skew()
    desc["curtosis"] = df[cols].kurt()
    desc["atipicos_iqr"] = [outlier_stats(df[c])["n_atipicos"] for c in cols]
    desc["pct_atipicos"] = (100 * desc["atipicos_iqr"] / desc["count"]).round(2)
    desc.index.name = "variable"
    desc = desc.round(4)
    save_table(desc, name, index=True)
    return desc


def build_balance_tables(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    counts = df[TARGET].value_counts().sort_index()
    total = len(df)
    balance = pd.DataFrame({
        "clase": [LABELS[i] for i in counts.index],
        "codigo": counts.index.astype(int),
        "n": counts.values.astype(int),
        "porcentaje": (100 * counts.values / total).round(2),
    })
    save_table(balance, "eda_balance_objetivo_16vars.csv")

    seasonal = (df.groupby("season")[TARGET]
                  .agg(n_equipos="size", clasificados="sum", tasa_playoffs="mean")
                  .reset_index())
    seasonal["no_clasificados"] = seasonal["n_equipos"] - seasonal["clasificados"]
    seasonal["tasa_playoffs_pct"] = (100 * seasonal["tasa_playoffs"]).round(3)
    seasonal = seasonal[["season", "n_equipos", "clasificados", "no_clasificados",
                         "tasa_playoffs", "tasa_playoffs_pct"]]
    save_table(seasonal, "eda_balance_por_temporada_16vars.csv")
    return balance, seasonal


def build_class_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Comparacion de predictores relativos entre clases + d de Cohen."""
    rows = []
    for col in FEATURES:
        a = df.loc[df[TARGET] == 0, f"{col}_rel"].dropna()
        b = df.loc[df[TARGET] == 1, f"{col}_rel"].dropna()
        n0, n1 = len(a), len(b)
        var0, var1 = a.var(ddof=1), b.var(ddof=1)
        pooled = np.sqrt(((n0 - 1) * var0 + (n1 - 1) * var1) / (n0 + n1 - 2))
        d = (b.mean() - a.mean()) / pooled if pooled > 0 else np.nan
        rows.append({
            "variable": col,
            "unidad": UNITS[col],
            "media_no_clasifico": a.mean(),
            "media_clasifico": b.mean(),
            "mediana_no_clasifico": a.median(),
            "mediana_clasifico": b.median(),
            "diferencia_medias_si_menos_no": b.mean() - a.mean(),
            "d_cohen": d,
            "n_no_clasifico": n0,
            "n_clasifico": n1,
        })
    out = pd.DataFrame(rows)
    out["abs_d_cohen"] = out["d_cohen"].abs()
    out = out.sort_values("d_cohen", ascending=False).round(4)
    save_table(out, "eda_resumen_por_clase_16vars.csv")
    return out


def build_target_correlation(df: pd.DataFrame) -> pd.DataFrame:
    """Pearson (punto-biserial) y Spearman de cada predictor relativo vs 0/1."""
    pear = df[REL_FEATURES + [TARGET]].corr(method="pearson")[TARGET].drop(TARGET)
    spear = df[REL_FEATURES + [TARGET]].corr(method="spearman")[TARGET].drop(TARGET)
    out = pd.DataFrame({"r_pearson": pear, "r_spearman": spear})
    out.index = [i.replace("_rel", "") for i in out.index]
    out["abs_r_pearson"] = out["r_pearson"].abs()
    out = out.sort_values("r_pearson", ascending=False)
    out.index.name = "variable"
    out = out.round(4)
    save_table(out, "eda_correlacion_objetivo_16vars.csv", index=True)
    return out


def build_feature_correlation(df: pd.DataFrame) -> pd.DataFrame:
    corr = df[REL_FEATURES].corr(method="pearson")
    corr.index = [c.replace("_rel", "") for c in corr.index]
    corr.columns = [c.replace("_rel", "") for c in corr.columns]
    corr.index.name = "variable"
    save_table(corr.round(4), "eda_matriz_correlacion_predictores_16vars.csv", index=True)
    return corr


def build_correlation_pairs(corr: pd.DataFrame, threshold: float = 0.7) -> pd.DataFrame:
    names = list(corr.columns)
    rows = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            r = float(corr.iloc[i, j])
            if abs(r) >= threshold:
                rows.append({"var_1": names[i], "var_2": names[j], "r": r,
                             "abs_r": abs(r), "supera_0_8": abs(r) >= 0.8})
    out = pd.DataFrame(rows, columns=["var_1", "var_2", "r", "abs_r", "supera_0_8"])
    if len(out):
        out = out.sort_values("abs_r", ascending=False)
    out = out.round(4)
    save_table(out, "eda_pares_correlacionados_16vars.csv")
    return out


def build_outlier_table(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in FEATURES:
        s = df[f"{col}_rel"]
        stats = outlier_stats(s)
        rows.append({
            "variable": col,
            "unidad": UNITS[col],
            "n_atipicos": stats["n_atipicos"],
            "porcentaje": round(100 * stats["n_atipicos"] / len(s), 2),
            "n_bajo": stats["n_bajo"],
            "n_alto": stats["n_alto"],
            "limite_inferior": stats["limite_inferior"],
            "limite_superior": stats["limite_superior"],
            "min": s.min(),
            "max": s.max(),
            "sesgo": s.skew(),
        })
    out = pd.DataFrame(rows).sort_values("n_atipicos", ascending=False).round(4)
    save_table(out, "eda_atipicos_16vars.csv")
    return out


def build_quintile_table(df: pd.DataFrame) -> pd.DataFrame:
    """Tasa de clasificacion por quintil DENTRO de cada temporada.

    Se usa el rango percentil dentro de la temporada (no el valor absoluto)
    para que Q1 sea "el 20% mas bajo de su temporada" y Q5 "el 20% mas alto",
    sin mezclar la deriva de epoca.
    """
    ranks = df.groupby("season")[FEATURES].rank(pct=True, method="average")
    rows = []
    for col in FEATURES:
        q = pd.cut(ranks[col],
                   bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
                   labels=QUINTILES, include_lowest=True)
        tab = (pd.DataFrame({"quintil": q, TARGET: df[TARGET]})
               .groupby("quintil", observed=True)[TARGET]
               .agg(n="size", clasificados="sum", tasa="mean")
               .reset_index())
        for _, r in tab.iterrows():
            rows.append({
                "variable": col,
                "quintil": str(r["quintil"]),
                "n": int(r["n"]),
                "clasificados": int(r["clasificados"]),
                "tasa": r["tasa"],
                "tasa_pct": 100 * r["tasa"],
            })
    out = pd.DataFrame(rows).round(4)
    save_table(out, "eda_tasa_playoffs_por_quintil_16vars.csv")
    return out


def build_quadrant_table(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for label, mask in quadrant_masks(df).items():
        n = int(mask.sum())
        k = int(df.loc[mask, TARGET].sum())
        rows.append({"cuadrante": label, "n": n, "clasificados": k,
                     "tasa": k / n if n else np.nan,
                     "tasa_pct": 100 * k / n if n else np.nan})
    out = pd.DataFrame(rows).round(4)
    save_table(out, "eda_cuadrantes_efg_16vars.csv")
    return out


def build_season_table(df: pd.DataFrame) -> pd.DataFrame:
    """Resumen por temporada: volumen, objetivo y medias de liga utiles."""
    aggs = {"n_equipos": (TARGET, "size"),
            "clasificados": (TARGET, "sum"),
            "tasa_playoffs": (TARGET, "mean")}
    out = df.groupby("season").agg(**aggs).reset_index()
    means = (df.groupby("season")[["3PAr", "Pace", "ORtg", "off_eFG%",
                                   "def_eFG%", "Age"]]
               .mean().reset_index())
    out = out.merge(means, on="season", how="left")
    out["tasa_playoffs_pct"] = (100 * out["tasa_playoffs"]).round(3)
    out = out.round(4)
    save_table(out, "eda_por_temporada_16vars.csv")
    return out


def games_by_season(df: pd.DataFrame) -> pd.DataFrame:
    """Control de calidad: partidos jugados por temporada (G no es predictor).

    Sirve para documentar temporadas acortadas o partidos cancelados, que
    afectan cualquier comparacion de TOTALES. El EDA usa tasas y promedios
    por partido, no totales.
    """
    if "G" not in df.columns:
        return pd.DataFrame()
    out = (df.groupby("season")["G"]
             .agg(n_equipos="size", partidos_min="min", partidos_max="max",
                  partidos_media="mean",
                  equipos_menos_de_82=lambda s: int((s < 82).sum()))
             .reset_index())
    out["temporada_completa_82"] = out["partidos_min"] == 82
    return out.round(2)


# --------------------------------------------------------------------------
# Figuras
# --------------------------------------------------------------------------
def fig_class_balance(df: pd.DataFrame) -> Path:
    counts = df[TARGET].value_counts().sort_index()
    total = len(df)
    fig, ax = plt.subplots(figsize=(5.6, 4.4))
    ax.bar([LABELS[i] for i in counts.index], counts.values,
           color=[COLORS[i] for i in counts.index], width=0.62)
    for x, v in enumerate(counts.values):
        ax.text(x, v + 8, f"{v}\n({v / total:.1%})", ha="center", va="bottom", fontsize=9)
    ax.set_ylim(0, max(counts.values) * 1.22)
    ax.set_title("Balance de la variable objetivo\n(805 equipos-temporada, 2000-2026)")
    ax.set_xlabel("Resultado de la temporada")
    ax.set_ylabel("Número de equipos-temporada")
    ax.grid(axis="y", alpha=0.25)
    return savefig("01_balance_clases_16vars.png")


def fig_season_target(df: pd.DataFrame) -> Path:
    by = (df.groupby("season")[TARGET]
            .agg(n_equipos="size", clasificados="sum", tasa="mean")
            .reset_index())
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 7), sharex=True,
                                   gridspec_kw={"height_ratios": [1, 1.2]})

    ax1.plot(by["season"], by["n_equipos"], marker="o", color="#777777",
             label="Equipos en la liga")
    ax1.plot(by["season"], by["clasificados"], marker="s", color=ACCENT,
             label="Clasificados a playoffs")
    ax1.set_ylim(0, 33)
    ax1.set_ylabel("Número de equipos")
    ax1.set_title("Composición de la liga por temporada")
    ax1.legend(loc="lower right", fontsize=8)
    ax1.grid(alpha=0.25)

    ax2.plot(by["season"], 100 * by["tasa"], marker="o", color=ACCENT,
             label="Tasa observada")
    ax2.axhline(100 * 16 / 29, color="#777777", ls="--", lw=1,
                label="16/29 = 55,2% (2000-2004)")
    ax2.axhline(100 * 16 / 30, color="black", ls=":", lw=1,
                label="16/30 = 53,3% (2005-2026)")
    ax2.set_ylim(50, 58)
    ax2.set_xlabel("Temporada (año de cierre)")
    ax2.set_ylabel("Tasa de clasificación (%)")
    ax2.set_title("Proporción de equipos que clasifican")
    ax2.legend(loc="lower right", fontsize=8)
    ax2.grid(alpha=0.25)

    fig.suptitle("16 clasificados por temporada: la tasa solo cambia por el "
                 "tamaño de la liga (29 hasta 2004; 30 desde 2005)", fontsize=10)
    return savefig("02_evolucion_playoffs_por_temporada_16vars.png")


def fig_era_drift(df: pd.DataFrame) -> Path:
    cols = [c for c in DRIFT_COLS if c in df.columns]
    by_season = df.groupby("season")[cols].mean()
    fig, axes = plt.subplots(1, len(cols), figsize=(4.6 * len(cols), 4.0))
    axes = np.atleast_1d(axes)
    for ax, col in zip(axes, cols):
        ax.plot(by_season.index, by_season[col], marker="o", color=ACCENT, ms=3.5)
        ax.set_title(f"Promedio de la liga: {col}")
        ax.set_xlabel("Temporada (año de cierre)")
        ax.set_ylabel(col)
        ax.grid(alpha=0.25)
    fig.suptitle("La NBA cambia con los años: por eso se usan variables relativas "
                 "a la temporada\n(ORtg se muestra solo como contexto; no es predictor)",
                 fontsize=10)
    return savefig("03_deriva_por_epoca_16vars.png")


def fig_histograms(df: pd.DataFrame) -> Path:
    fig, axes = plt.subplots(4, 4, figsize=(16, 12))
    for ax, col in zip(axes.ravel(), FEATURES):
        for cls in (0, 1):
            ax.hist(df.loc[df[TARGET] == cls, f"{col}_rel"].dropna(),
                    bins=20, density=True, alpha=0.55, color=COLORS[cls],
                    label=LABELS[cls], edgecolor="white", linewidth=0.3)
        ax.axvline(0, color="black", lw=0.8, ls="--")
        ax.set_title(col, fontsize=10)
        ax.grid(alpha=0.18)
    axes.ravel()[0].legend(fontsize=8, loc="upper left")
    fig.supxlabel("Diferencia vs promedio de la temporada (unidades originales)", fontsize=10)
    fig.supylabel("Densidad", fontsize=10)
    fig.suptitle("Distribución de los 16 predictores relativos según clasificación "
                 "a playoffs\n(la línea punteada marca el promedio de la temporada)",
                 fontsize=11)
    return savefig("04_histogramas_16vars.png")


def fig_boxplots(df: pd.DataFrame, cols: list[str], name: str, title: str) -> Path:
    fig, axes = plt.subplots(2, 4, figsize=(15, 7.5))
    for ax, col in zip(axes.ravel(), cols):
        data = [df.loc[df[TARGET] == c, f"{col}_rel"].dropna() for c in (0, 1)]
        bp = ax.boxplot(data, tick_labels=[LABELS[0], LABELS[1]],
                        patch_artist=True, widths=0.55)
        for patch, c in zip(bp["boxes"], (0, 1)):
            patch.set_facecolor(COLORS[c])
            patch.set_alpha(0.65)
        ax.axhline(0, color="black", lw=0.8, ls="--")
        ax.set_title(col, fontsize=10)
        ax.grid(axis="y", alpha=0.2)
    fig.supylabel("Diferencia vs promedio de la temporada (unidades originales)",
                  fontsize=10)
    fig.suptitle(title, fontsize=11)
    return savefig(name)


def fig_target_correlation(corr: pd.DataFrame) -> Path:
    d = corr.sort_values("r_pearson", ascending=True)
    y = np.arange(len(d))
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 8), sharey=True)

    ax1.barh(y, d["r_pearson"], color=[ACCENT if v >= 0 else NEGATIVE
                                       for v in d["r_pearson"]], height=0.65)
    ax1.axvline(0, color="black", lw=0.9)
    ax1.set_yticks(y, d.index)
    ax1.set_xlim(-0.72, 0.72)
    ax1.set_xlabel("r de Pearson (punto-biserial)")
    ax1.set_title("Pearson: asociación lineal con 0/1")
    ax1.grid(axis="x", alpha=0.25)
    for yi, v in zip(y, d["r_pearson"]):
        ax1.text(v + (0.012 if v >= 0 else -0.012), yi, f"{v:+.2f}",
                 va="center", ha="left" if v >= 0 else "right", fontsize=7)

    ax2.barh(y, d["r_spearman"], color=[ACCENT if v >= 0 else NEGATIVE
                                        for v in d["r_spearman"]], height=0.65)
    ax2.axvline(0, color="black", lw=0.9)
    ax2.set_xlim(-0.72, 0.72)
    ax2.set_xlabel("ρ de Spearman (rangos)")
    ax2.set_title("Spearman: asociación monótona")
    ax2.grid(axis="x", alpha=0.25)
    for yi, v in zip(y, d["r_spearman"]):
        ax2.text(v + (0.012 if v >= 0 else -0.012), yi, f"{v:+.2f}",
                 va="center", ha="left" if v >= 0 else "right", fontsize=7)

    fig.suptitle("Correlación de cada predictor relativo con clasificar a playoffs\n"
                 "Asociación, no causalidad; el coeficiente no ajusta por otras variables",
                 fontsize=11)
    return savefig("05_correlacion_con_objetivo_16vars.png")


def fig_feature_heatmap(corr: pd.DataFrame) -> Path:
    n = len(corr)
    fig, ax = plt.subplots(figsize=(11, 9))
    im = ax.imshow(corr.values, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
    names = list(corr.columns)
    ax.set_xticks(range(n), names, rotation=90, fontsize=8)
    ax.set_yticks(range(n), names, fontsize=8)
    for i in range(n):
        for j in range(n):
            if i != j and abs(corr.iloc[i, j]) >= 0.5:
                ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center",
                        fontsize=7, color="black")
    fig.colorbar(im, ax=ax, label="Correlación de Pearson", shrink=0.85)
    ax.set_title("Correlación entre los 16 predictores relativos\n"
                 "Solo se anotan los pares con |r| ≥ 0,50", fontsize=11)
    ax.set_xlabel("Predictor")
    ax.set_ylabel("Predictor")
    return savefig("06_correlacion_entre_predictores_16vars.png")


def fig_scatter(df: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(8, 6.5))
    for cls in (0, 1):
        sub = df[df[TARGET] == cls]
        ax.scatter(sub["off_eFG%_rel"], sub["def_eFG%_rel"], s=22, alpha=0.65,
                   color=COLORS[cls], label=LABELS[cls], edgecolors="none")
    ax.axhline(0, color="black", lw=0.9, ls="--")
    ax.axvline(0, color="black", lw=0.9, ls="--")

    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
    if ymin < 0 and xmax > 0:
        ax.add_patch(Rectangle((0, ymin), xmax, -ymin, facecolor="#009E73",
                               alpha=0.07, edgecolor="none", zorder=0))

    masks = quadrant_masks(df)
    placements = {
        "Ataque > media; defensa mejor": (0.97, 0.03, "right", "bottom"),
        "Ataque > media; defensa peor": (0.97, 0.97, "right", "top"),
        "Ataque <= media; defensa mejor": (0.03, 0.03, "left", "bottom"),
        "Ataque <= media; defensa peor": (0.03, 0.97, "left", "top"),
    }
    short = {
        "Ataque > media; defensa mejor": "Ataque > media\nDefensa mejor",
        "Ataque > media; defensa peor": "Ataque > media\nDefensa peor",
        "Ataque <= media; defensa mejor": "Ataque <= media\nDefensa mejor",
        "Ataque <= media; defensa peor": "Ataque <= media\nDefensa peor",
    }
    for label, mask in masks.items():
        n = int(mask.sum())
        rate = df.loc[mask, TARGET].mean()
        x, y, ha, va = placements[label]
        ax.text(x, y, f"{short[label]}\nn={n} | {rate:.0%} clasificó",
                transform=ax.transAxes, ha=ha, va=va, fontsize=7.5,
                bbox={"boxstyle": "round,pad=0.25", "facecolor": "white",
                      "alpha": 0.78, "edgecolor": "#cccccc"})

    ax.set_xlabel("eFG% del equipo vs liga (mayor = mejor ataque)")
    ax.set_ylabel("eFG% del rival vs liga (menor = mejor defensa)")
    ax.set_title("Puntería propia vs puntería permitida, relativa a la temporada\n"
                 "Cuadrante inferior derecho = ataque y defensa mejores que la media",
                 fontsize=10)
    ax.legend(loc="center right", fontsize=8, framealpha=0.9)
    ax.grid(alpha=0.2)
    return savefig("07_dispersion_efg_ataque_defensa_16vars.png")


def fig_quintiles(quintiles: pd.DataFrame, base_rate: float) -> Path:
    pivot = (quintiles.pivot(index="quintil", columns="variable", values="tasa_pct")
             .reindex(QUINTILES)[FEATURES])
    fig, axes = plt.subplots(4, 4, figsize=(16, 12))
    for ax, col in zip(axes.ravel(), FEATURES):
        vals = pivot[col].to_numpy()
        colors = [ACCENT if v >= base_rate else NEGATIVE for v in vals]
        ax.bar(range(len(QUINTILES)), vals, color=colors, width=0.68)
        ax.axhline(base_rate, color="black", lw=0.9, ls="--")
        ax.set_xticks(range(len(QUINTILES)), QUINTILES)
        ax.set_ylim(0, 100)
        ax.set_title(col, fontsize=10)
        ax.grid(axis="y", alpha=0.2)
    for ax in axes[:, 0]:
        ax.set_ylabel("Tasa de clasificación (%)")
    for ax in axes[-1, :]:
        ax.set_xlabel("Quintil dentro de su temporada")
    fig.suptitle("Tasa de clasificación por quintil relativo dentro de cada temporada\n"
                 f"Q1 = 20% más bajo de su temporada; Q5 = 20% más alto. "
                 f"Línea punteada = tasa global ({base_rate:.1f}%). "
                 "Azul = por encima; naranja = por debajo.", fontsize=11)
    return savefig("08_tasa_playoffs_por_quintil_16vars.png")


def fig_outliers(outliers: pd.DataFrame) -> Path:
    d = outliers.sort_values("porcentaje", ascending=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6.5))
    ax1.barh(d["variable"], d["porcentaje"], color=NEGATIVE, height=0.65)
    ax1.set_xlabel("% de observaciones atípicas (regla 1,5 × IQR)")
    ax1.set_title("Atípicos por predictor relativo")
    ax1.grid(axis="x", alpha=0.25)
    for yi, (v, n) in enumerate(zip(d["porcentaje"], d["n_atipicos"])):
        ax1.text(v + 0.04, yi, f"{n}", va="center", fontsize=7)

    ax2.barh(d["variable"], d["sesgo"],
             color=[ACCENT if v >= 0 else NEGATIVE for v in d["sesgo"]], height=0.65)
    ax2.axvline(0, color="black", lw=0.9)
    ax2.set_xlabel("Sesgo (asimetría de la distribución relativa)")
    ax2.set_title("Distribuciones sesgadas")
    ax2.grid(axis="x", alpha=0.25)

    fig.suptitle("Valores atípicos y sesgo de los predictores relativos\n"
                 "Los atípicos NO se eliminan: pueden ser equipos legítimamente extremos",
                 fontsize=10)
    return savefig("09_atipicos_y_sesgo_16vars.png")


# --------------------------------------------------------------------------
# Resumen y metadatos
# --------------------------------------------------------------------------
def write_summary(df: pd.DataFrame, corr: pd.DataFrame, pairs: pd.DataFrame,
                  class_summary: pd.DataFrame, outliers: pd.DataFrame,
                  season_table: pd.DataFrame, metadata: dict) -> Path:
    counts = df[TARGET].value_counts().sort_index()
    total = len(df)
    lines = []
    lines.append("FASE III - EDA - CORRIDA ACTUAL (16 PREDICTORES)")
    lines.append("=" * 64)
    lines.append(f"Fecha/hora: {metadata['timestamp']}")
    lines.append(f"Entrada: {metadata['input_file']}")
    lines.append(f"SHA256 entrada: {metadata['input_sha256']}")
    lines.append(f"Filas: {total} | Columnas originales: {metadata['n_columns_original']} | "
                 f"Columnas con relativas: {metadata['n_columns_working']} | "
                 f"Temporadas: {metadata['n_seasons']} "
                 f"({min(metadata['seasons'])}-{max(metadata['seasons'])})")
    lines.append(f"Predictores: {len(FEATURES)}")
    lines.append("  " + ", ".join(FEATURES))
    lines.append("")
    lines.append("1. VARIABLE OBJETIVO")
    for code in counts.index:
        lines.append(f"   {LABELS[code]} ({code}): {counts[code]} "
                     f"({counts[code] / total:.1%})")
    lines.append("   16 clasificados por temporada; 29 equipos hasta 2004 y 30 desde 2005.")
    lines.append("")
    lines.append("2. CALIDAD DE LOS PREDICTORES")
    lines.append(f"   Nulos en los 16 predictores: {int(df[FEATURES].isna().sum().sum())}")
    lines.append(f"   Infinitos en los 16 predictores: "
                 f"{int(np.isinf(df[FEATURES].to_numpy()).sum())}")
    lines.append(f"   Duplicados (season, Team): {int(df.duplicated(['season', 'Team']).sum())}")
    ctx_nulls = {c: int(df[c].isna().sum()) for c in CONTEXT_COLS if c in df.columns}
    lines.append(f"   Nulos en variables de contexto (excluidas): {ctx_nulls}")
    lines.append("   No se imputa ni elimina ninguna observación en esta fase.")
    lines.append("")
    games = games_by_season(df)
    if len(games):
        lines.append("   Partidos por temporada (G; no es predictor):")
        short = games[games["partidos_min"] < 82]
        for _, row in short.iterrows():
            lines.append(f"     {int(row['season'])}: "
                         f"{int(row['partidos_min'])}-{int(row['partidos_max'])} "
                         f"partidos ({int(row['equipos_menos_de_82'])} equipos)")
        lines.append("   Por eso el EDA usa tasas y promedios por partido, no totales.")
        lines.append("")
    lines.append("3. CORRELACIÓN CON EL OBJETIVO (predictores relativos)")
    lines.append("   Más positivas:")
    for name, row in corr.head(5).iterrows():
        lines.append(f"     {name:12s} r={row['r_pearson']:+.3f} | "
                     f"rho={row['r_spearman']:+.3f}")
    lines.append("   Más negativas:")
    for name, row in corr.sort_values("r_pearson").head(5).iterrows():
        lines.append(f"     {name:12s} r={row['r_pearson']:+.3f} | "
                     f"rho={row['r_spearman']:+.3f}")
    lines.append("")
    lines.append("4. REDUNDANCIA ENTRE PREDICTORES (|r| >= 0,70)")
    if len(pairs):
        for _, row in pairs.iterrows():
            lines.append(f"   {row['var_1']:12s} - {row['var_2']:12s} "
                         f"r={row['r']:+.3f}")
    else:
        lines.append("   Ningún par alcanza |r| >= 0,70.")
    lines.append("")
    lines.append("5. DIFERENCIAS ENTRE CLASES (d de Cohen, valores relativos)")
    lines.append("   Mayores diferencias absolutas:")
    for _, row in class_summary.reindex(class_summary["abs_d_cohen"]
                                        .sort_values(ascending=False).index).head(5).iterrows():
        lines.append(f"     {row['variable']:12s} d={row['d_cohen']:+.3f} | "
                     f"media no={row['media_no_clasifico']:+.3f} | "
                     f"media sí={row['media_clasifico']:+.3f}")
    lines.append("")
    lines.append("6. ATÍPICOS (1,5 × IQR sobre valores relativos)")
    top_out = outliers.head(5)
    for _, row in top_out.iterrows():
        lines.append(f"   {row['variable']:12s} {int(row['n_atipicos']):3d} "
                     f"({row['porcentaje']:.1f}%)")
    lines.append("   No se eliminan: pueden ser equipos legítimamente extremos.")
    lines.append("")
    lines.append("7. DERIVA DE ÉPOCA (promedio de liga, primera y última temporada)")
    first, last = season_table.iloc[0], season_table.iloc[-1]
    for col in ["3PAr", "Pace", "ORtg", "off_eFG%", "def_eFG%", "Age"]:
        if col in season_table.columns:
            lines.append(f"   {col:10s} {first[col]:8.3f} -> {last[col]:8.3f}")
    lines.append("")
    lines.append("8. ARCHIVOS")
    lines.append(f"   Figuras: {rel(FIG_DIR)}")
    lines.append(f"   Tablas : {rel(METRICS_DIR)}")
    lines.append(f"   Log    : {rel(LOG_DIR)}")
    lines.append("")
    lines.append("Limitaciones: asociación no es causalidad; una sola fuente; "
                 "cambios de formato de playoffs (play-in desde 2021); temporadas "
                 "con menos de 82 partidos (ver tabla de partidos por temporada); "
                 "variables relativas calculadas con el promedio de la temporada "
                 "(incluye equipos de test).")
    path = METRICS_DIR / "eda_resumen_16vars.txt"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8-sig")
    LOG.info("Resumen guardado: %s", rel(path))
    return path


def build_metadata(df: pd.DataFrame, log_path: Path) -> dict:
    counts = df[TARGET].value_counts().sort_index()
    return {
        "run_id": RUN_ID,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "pandas": pd.__version__,
        "numpy": np.__version__,
        "matplotlib": matplotlib.__version__,
        "scikit_learn": sklearn.__version__ if sklearn is not None else None,
        "input_file": rel(DATA_FILE),
        "input_sha256": sha256_file(DATA_FILE),
        "n_rows": int(len(df)),
        "n_columns_original": int(df.shape[1] - len(REL_FEATURES)),
        "n_columns_working": int(df.shape[1]),
        "n_seasons": int(df["season"].nunique()),
        "seasons": [int(x) for x in sorted(df["season"].unique())],
        "target": TARGET,
        "target_counts": {str(int(k)): int(v) for k, v in counts.items()},
        "target_pct": {str(int(k)): round(100 * v / len(df), 2)
                       for k, v in counts.items()},
        "n_features": len(FEATURES),
        "features": FEATURES,
        "forbidden_in_features": sorted(set(FEATURES) & set(FORBIDDEN)),
        "predictor_nulls": int(df[FEATURES].isna().sum().sum()),
        "context_nulls": {c: int(df[c].isna().sum())
                          for c in CONTEXT_COLS if c in df.columns},
        "log_file": rel(log_path),
    }


# --------------------------------------------------------------------------
# Principal
# --------------------------------------------------------------------------
def main() -> None:
    log_path = setup_logging()
    LOG.info("=" * 70)
    LOG.info("FASE III - EDA | corrida actual de 16 predictores")
    LOG.info("Python %s | pandas %s | numpy %s | matplotlib %s",
             sys.version.split()[0], pd.__version__, np.__version__,
             matplotlib.__version__)
    if sklearn is not None:
        LOG.info("scikit-learn %s (no se usa en esta fase)", sklearn.__version__)
    LOG.info("Entrada: %s", rel(DATA_FILE))
    LOG.info("Salida : %s", rel(OUT_DIR))

    df = load_data()
    LOG.info("Dataset: %d filas x %d columnas | %d temporadas (%d-%d)",
             len(df), df.shape[1], df["season"].nunique(),
             df["season"].min(), df["season"].max())
    LOG.info("Predictores (%d): %s", len(FEATURES), ", ".join(FEATURES))
    LOG.info("Nulos en predictores: %d | Infinitos: %d",
             int(df[FEATURES].isna().sum().sum()),
             int(np.isinf(df[FEATURES].to_numpy()).sum()))
    counts = df[TARGET].value_counts().sort_index()
    LOG.info("Objetivo: 0=%d (%.1f%%) | 1=%d (%.1f%%) | nulos=%d",
             counts.get(0, 0), 100 * counts.get(0, 0) / len(df),
             counts.get(1, 0), 100 * counts.get(1, 0) / len(df),
             int(df[TARGET].isna().sum()))

    df = add_relative_features(df, FEATURES)

    LOG.info("Generando tablas descriptivas y de calidad...")
    quality = build_quality_table(df)
    save_table(quality, "eda_calidad_datos_16vars.csv")
    build_descriptives(df, FEATURES, "eda_descriptivas_absolutas_16vars.csv")
    build_descriptives(df, REL_FEATURES, "eda_descriptivas_relativas_16vars.csv")
    _balance, _seasonal = build_balance_tables(df)
    class_summary = build_class_summary(df)
    corr_target = build_target_correlation(df)
    corr_features = build_feature_correlation(df)
    pairs = build_correlation_pairs(corr_features)
    outliers = build_outlier_table(df)
    quintiles = build_quintile_table(df)
    _quadrants = build_quadrant_table(df)
    season_table = build_season_table(df)
    games = games_by_season(df)
    save_table(games, "eda_partidos_por_temporada_16vars.csv")

    LOG.info("Generando figuras...")
    fig_class_balance(df)
    fig_season_target(df)
    fig_era_drift(df)
    fig_histograms(df)
    fig_boxplots(df, FOUR_FACTORS, "10_boxplots_cuatro_factores_16vars.png",
                 "Cuatro factores (ataque y defensa) según clasificación a playoffs\n"
                 "Valores relativos al promedio de la temporada")
    fig_boxplots(df, OTHER_FEATURES, "11_boxplots_otras_variables_16vars.png",
                 "Otras ocho variables según clasificación a playoffs\n"
                 "Valores relativos al promedio de la temporada")
    fig_target_correlation(corr_target)
    fig_feature_heatmap(corr_features)
    fig_scatter(df)
    fig_quintiles(quintiles, base_rate=100 * df[TARGET].mean())
    fig_outliers(outliers)

    metadata = build_metadata(df, log_path)
    summary_path = write_summary(df, corr_target, pairs, class_summary,
                                 outliers, season_table, metadata)
    metadata["files"] = {
        "figures": sorted(p.name for p in FIG_DIR.glob("*.png")),
        "tables": sorted(p.name for p in METRICS_DIR.glob("*.csv")),
        "summary": rel(summary_path),
        "log": rel(log_path),
    }
    meta_path = METRICS_DIR / "eda_resumen_ejecucion_16vars.json"
    meta_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")
    LOG.info("Metadatos guardados: %s", rel(meta_path))

    LOG.info("-" * 70)
    LOG.info("Correlación con el objetivo (Pearson, top 5):")
    for name, row in corr_target.head(5).iterrows():
        LOG.info("  %-12s %+.3f", name, row["r_pearson"])
    LOG.info("Pares con |r| >= 0,70: %d", len(pairs))
    LOG.info("Atípicos máximos: %s (%d, %.1f%%)",
             outliers.iloc[0]["variable"], int(outliers.iloc[0]["n_atipicos"]),
             outliers.iloc[0]["porcentaje"])
    LOG.info("Estado: OK | figuras=%d | tablas=%d",
             len(metadata["files"]["figures"]), len(metadata["files"]["tables"]))
    LOG.info("=" * 70)


if __name__ == "__main__":
    main()
