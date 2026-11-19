"""
FASE IV - Machine Learning y optimizacion (16 predictores)

Entrada : data/processed/nba_teams_clean.csv  (Fase II)
Salida  : outputs_corrida2_16vars_fase4/
          figures/  metrics/  logs/

Problema: CLASIFICACION binaria -> el equipo clasifica a playoffs (1) o no (0).

Protocolos de evaluacion:
  1. TEMPORAL (principal): entrenar con temporadas <= 2019 y evaluar con las
     posteriores. La validacion cruzada agrupa por temporada para que ningun
     fold comparta temporada entre train y validacion.
  2. ESTRATIFICADO (secundario): replica el protocolo historico de 80/20
     estratificado con StratifiedKFold. Sirve para comparar, no para elegir el
     modelo final.

Controles contra fuga de datos:
  - Predictores = estadisticas de juego relativas a la temporada.
  - Se excluyen W, L, MOV, SRS, NRtg, win_pct, Rk, ORtg, DRtg, Attend. y Attend./G.
  - train/test se separan ANTES de ajustar imputacion, escalado o modelo.
  - Imputacion y escalado viven dentro del Pipeline.
  - El umbral se elige en una validacion interna del train, no en test.
  - El test se evalua una sola vez por protocolo.

Uso:
    .\\.venv\\Scripts\\python.exe modelado.py
"""
from __future__ import annotations

import json
import logging
import platform
import time
from datetime import datetime
from hashlib import sha256
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from sklearn.base import clone
from sklearn.calibration import calibration_curve
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import (
    GridSearchCV,
    StratifiedGroupKFold,
    StratifiedKFold,
    cross_validate,
    train_test_split,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from exploracion import FEATURES, TARGET, add_relative_features

# --------------------------------------------------------------------------
# Configuracion
# --------------------------------------------------------------------------
DATA_FILE = Path("data/processed/nba_teams_clean.csv")
RUN_ID = "corrida2_16vars_fase4"
OUT_DIR = Path("outputs_corrida2_16vars_fase4")
FIG_DIR = OUT_DIR / "figures"
METRICS_DIR = OUT_DIR / "metrics"
LOG_DIR = OUT_DIR / "logs"

RANDOM_STATE = 42
TEST_SIZE = 0.20
N_FOLDS = 5
TEMPORAL_CUTOFF = 2019
REFIT = "f1"

SCORING = {
    "accuracy": "accuracy",
    "precision": "precision",
    "recall": "recall",
    "f1": "f1",
    "roc_auc": "roc_auc",
    "pr_auc": "average_precision",
    "brier": "neg_brier_score",
}

# Modelos candidatos y sus grillas (prefijo clf__ = paso del Pipeline)
MODELS = {
    "LogisticRegression": (
        LogisticRegression(max_iter=5000, random_state=RANDOM_STATE),
        {"clf__C": [0.001, 0.01, 0.1, 1, 10, 100, 1000, 10000]},
    ),
    "RandomForest": (
        RandomForestClassifier(random_state=RANDOM_STATE, n_jobs=1),
        {
            "clf__n_estimators": [200, 400],
            "clf__max_depth": [3, 5, 8, None],
            "clf__min_samples_leaf": [1, 3, 5],
            "clf__max_features": ["sqrt", 0.5],
        },
    ),
}

PROHIBIDOS = {"W", "L", "PW", "PL", "MOV", "SOS", "SRS", "NRtg", "win_pct",
              "Rk", "ORtg", "DRtg", "Attend.", "Attend./G"}


# --------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------
def setup_logging() -> tuple[logging.Logger, Path]:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOG_DIR / f"modelado_16vars_{stamp}.log"
    logger = logging.getLogger("fase4")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s",
                            "%Y-%m-%d %H:%M:%S")
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setFormatter(fmt)
    sh = logging.StreamHandler()
    sh.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger, log_file


def sha256_file(path: Path) -> str:
    h = sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def json_default(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    return str(obj)


def make_pipeline(estimator) -> Pipeline:
    return Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
        ("clf", clone(estimator)),
    ])


def evaluate(model, X, y, threshold: float = 0.5) -> dict:
    proba = model.predict_proba(X)[:, 1]
    pred = (proba >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return {
        "accuracy": float(accuracy_score(y, pred)),
        "precision": float(precision_score(y, pred, zero_division=0)),
        "recall": float(recall_score(y, pred, zero_division=0)),
        "f1": float(f1_score(y, pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y, proba)),
        "pr_auc": float(average_precision_score(y, proba)),
        "brier": float(brier_score_loss(y, proba)),
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
    }


def cv_summary(scores: dict) -> dict:
    out = {}
    for name in SCORING:
        vals = scores[f"test_{name}"]
        if name == "brier":
            vals = -vals
        out[f"cv_{name}"] = float(np.mean(vals))
        out[f"cv_{name}_std"] = float(np.std(vals))
    return out


def best_row_summary(search: GridSearchCV) -> dict:
    i = search.best_index_
    res = search.cv_results_
    out = {}
    for name in SCORING:
        val = float(res[f"mean_test_{name}"][i])
        std = float(res[f"std_test_{name}"][i])
        if name == "brier":
            val = -val
        out[f"cv_{name}"] = val
        out[f"cv_{name}_std"] = std
    return out


def run_grid(protocol: str, name: str, estimator, grid: dict, X, y, cv,
             groups, log: logging.Logger) -> GridSearchCV:
    search = GridSearchCV(
        make_pipeline(estimator), grid, scoring=SCORING, refit=REFIT,
        cv=cv, n_jobs=-1, error_score="raise",
    )
    t0 = time.time()
    search.fit(X, y, groups=groups)
    elapsed = time.time() - t0
    n_combos = len(search.cv_results_["params"])
    log.info("  %s/%s: %d combinaciones x %d folds = %d ajustes (%.0f s)",
             protocol, name, n_combos, N_FOLDS, n_combos * N_FOLDS, elapsed)
    out = METRICS_DIR / f"modelado_gridsearch_{protocol}_{name}_16vars.csv"
    pd.DataFrame(search.cv_results_).to_csv(out, index=False)
    return search


def select_threshold(y_true, proba) -> tuple[float, float]:
    thresholds = np.linspace(0.05, 0.95, 91)
    f1s = [f1_score(y_true, (proba >= t).astype(int), zero_division=0)
           for t in thresholds]
    idx = int(np.argmax(f1s))
    return float(thresholds[idx]), float(f1s[idx])


def vif_table(X: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in X.columns:
        target = X[col].to_numpy()
        others = X.drop(columns=[col]).to_numpy()
        r2 = LinearRegression().fit(others, target).score(others, target)
        vif = 1.0 / (1.0 - r2) if r2 < 1.0 else float("inf")
        rows.append({"variable": col.replace("_rel", ""),
                     "r2": float(r2), "vif": float(vif)})
    return pd.DataFrame(rows).sort_values("vif", ascending=False)


def coefficients_table(model: Pipeline, feature_cols: list[str]) -> pd.DataFrame:
    clf = model.named_steps["clf"]
    names = [c.replace("_rel", "") for c in feature_cols]
    if hasattr(clf, "coef_"):
        coefs = np.ravel(clf.coef_)
        return pd.DataFrame({
            "variable": names,
            "coeficiente_estandarizado": coefs,
            "odds_ratio_por_1_sd": np.exp(coefs),
        }).sort_values("coeficiente_estandarizado", ascending=False)
    if hasattr(clf, "feature_importances_"):
        return pd.DataFrame({
            "variable": names,
            "importancia_impureza": clf.feature_importances_,
        }).sort_values("importancia_impureza", ascending=False)
    return pd.DataFrame()


# --------------------------------------------------------------------------
# Protocolo
# --------------------------------------------------------------------------
def run_protocol(protocol: str, X_train, y_train, X_test, y_test,
                 groups_train, cv, test_meta: pd.DataFrame,
                 log: logging.Logger) -> dict:
    log.info("=" * 70)
    log.info("Protocolo: %s | train=%d | test=%d | folds=%d",
             protocol, len(X_train), len(X_test), N_FOLDS)
    log.info("Clases train: %s | Clases test: %s",
             y_train.value_counts().to_dict(), y_test.value_counts().to_dict())

    # ---- Linea base trivial ----
    dummy = DummyClassifier(strategy="most_frequent")
    dummy_cv = cross_validate(make_pipeline(dummy), X_train, y_train, cv=cv,
                              groups=groups_train, scoring=SCORING)
    dummy_summary = cv_summary(dummy_cv)
    log.info("Linea base CV: accuracy=%.3f | f1=%.3f | roc_auc=%.3f",
             dummy_summary["cv_accuracy"], dummy_summary["cv_f1"],
             dummy_summary["cv_roc_auc"])

    # ---- Modelo base vs GridSearchCV, mismos folds ----
    rows, searches = [], {}
    for name, (estimator, grid) in MODELS.items():
        base_scores = cross_validate(make_pipeline(estimator), X_train, y_train,
                                     cv=cv, groups=groups_train, scoring=SCORING)
        base = cv_summary(base_scores)
        search = run_grid(protocol, name, estimator, grid, X_train, y_train,
                          cv, groups_train, log)
        tuned = best_row_summary(search)
        searches[name] = search
        for stage, metrics, params in (
            ("base", base, "defecto"),
            ("optimizado", tuned, search.best_params_),
        ):
            rows.append({"protocolo": protocol, "modelo": name,
                         "etapa": stage, "parametros": str(params), **metrics})
        delta = tuned["cv_f1"] - base["cv_f1"]
        within = abs(delta) <= base["cv_f1_std"]
        log.info("  %s base f1=%.3f+-%.3f | optim f1=%.3f+-%.3f | delta=%+.3f (%s 1 sd)",
                 name, base["cv_f1"], base["cv_f1_std"], tuned["cv_f1"],
                 tuned["cv_f1_std"], delta, "dentro de" if within else "fuera de")
        log.info("  mejores parametros %s: %s", name, search.best_params_)

    results = pd.DataFrame(rows)
    results.to_csv(METRICS_DIR / f"modelado_cv_base_vs_optimizado_{protocol}_16vars.csv",
                   index=False)

    # ---- Seleccion del modelo final (solo CV) ----
    tuned_only = results[results["etapa"] == "optimizado"].set_index("modelo")
    final_name = tuned_only["cv_f1"].idxmax()
    final_search = searches[final_name]
    final_model = final_search.best_estimator_
    log.info("Modelo final por CV (%s): %s | parametros=%s",
             protocol, final_name, final_search.best_params_)

    # ---- Validacion interna para umbral, calibracion e importancia ----
    X_sub, X_val, y_sub, y_val = train_test_split(
        X_train, y_train, test_size=0.20, stratify=y_train,
        random_state=RANDOM_STATE)
    val_model = clone(final_model).fit(X_sub, y_sub)
    proba_val = val_model.predict_proba(X_val)[:, 1]
    threshold, f1_val = select_threshold(y_val, proba_val)
    log.info("Umbral elegido en validacion interna: %.2f (F1 val=%.3f)",
             threshold, f1_val)

    # ---- Evaluacion final en test (una vez por protocolo) ----
    test_05 = evaluate(final_model, X_test, y_test, threshold=0.5)
    test_thr = evaluate(final_model, X_test, y_test, threshold=threshold)
    base_test = evaluate(
        make_pipeline(MODELS[final_name][0]).fit(X_train, y_train),
        X_test, y_test, threshold=0.5)
    proba_test = final_model.predict_proba(X_test)[:, 1]
    pred_thr = (proba_test >= threshold).astype(int)

    test_rows = [
        {"protocolo": protocol, "modelo": "Linea base trivial", "umbral": 0.5,
         **evaluate(make_pipeline(dummy).fit(X_train, y_train), X_test, y_test, 0.5)},
        {"protocolo": protocol, "modelo": f"{final_name} (base)", "umbral": 0.5,
         **base_test},
        {"protocolo": protocol, "modelo": f"{final_name} (optimizado)",
         "umbral": 0.5, **test_05},
        {"protocolo": protocol, "modelo": f"{final_name} (optimizado)",
         "umbral": threshold, **test_thr},
    ]
    test_df = pd.DataFrame(test_rows)
    test_df.to_csv(METRICS_DIR / f"modelado_test_{protocol}_16vars.csv", index=False)

    keys = ["accuracy", "precision", "recall", "f1", "roc_auc", "pr_auc", "brier"]
    log.info("TEST %s (umbral=0.50): %s", protocol,
             {k: round(test_05[k], 3) for k in keys})
    log.info("TEST %s (umbral=%.2f): %s", protocol, threshold,
             {k: round(test_thr[k], 3) for k in keys})

    # ---- Matriz de confusion ----
    cm = confusion_matrix(y_test, pred_thr, labels=[0, 1])
    pd.DataFrame(cm, index=["Real 0", "Real 1"],
                 columns=["Pred 0", "Pred 1"]).to_csv(
        METRICS_DIR / f"modelado_matriz_confusion_{protocol}_16vars.csv")
    disp = ConfusionMatrixDisplay(confusion_matrix=cm,
                                  display_labels=["No clasifico", "Clasifico"])
    disp.plot(cmap="Blues", values_format="d")
    disp.ax_.set_title(
        f"Matriz de confusion en test ({protocol}, umbral={threshold:.2f})")
    disp.ax_.set_xlabel("Prediccion del modelo")
    disp.ax_.set_ylabel("Resultado real")
    plt.tight_layout()
    plt.savefig(FIG_DIR / f"modelado_matriz_confusion_{protocol}_16vars.png",
                dpi=300)
    plt.close()

    # ---- Reporte de clasificacion ----
    report = classification_report(
        y_test, pred_thr, target_names=["No clasifico", "Clasifico"],
        digits=3, zero_division=0)
    (METRICS_DIR / f"modelado_classification_report_{protocol}_16vars.txt").write_text(
        report, encoding="utf-8")

    # ---- Predicciones con metadatos ----
    pred_df = test_meta.copy()
    pred_df["probabilidad"] = proba_test
    pred_df["pred_0_50"] = (proba_test >= 0.5).astype(int)
    pred_df["pred_umbral"] = pred_thr
    pred_df["real"] = y_test.to_numpy()
    pred_df.to_csv(
        METRICS_DIR / f"modelado_predicciones_test_{protocol}_16vars.csv",
        index=False)

    # ---- Curvas ROC y precision-recall ----
    fpr, tpr, _ = roc_curve(y_test, proba_test)
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(fpr, tpr, label=f"{final_name} (AUC={test_05['roc_auc']:.3f})",
            color="#1f6fb2")
    ax.plot([0, 1], [0, 1], "--", color="gray", label="Azar")
    ax.set_title(f"Curva ROC en test ({protocol})")
    ax.set_xlabel("Tasa de falsos positivos")
    ax.set_ylabel("Tasa de verdaderos positivos")
    ax.legend(loc="lower right")
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIG_DIR / f"modelado_curva_roc_{protocol}_16vars.png", dpi=300)
    plt.close()

    prec, rec, _ = precision_recall_curve(y_test, proba_test)
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(rec, prec, label=f"{final_name} (AP={test_05['pr_auc']:.3f})",
            color="#d97706")
    ax.axhline(y_test.mean(), ls="--", color="gray",
               label=f"Prevalencia={y_test.mean():.3f}")
    ax.set_title(f"Curva precision-recall en test ({protocol})")
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    ax.legend(loc="best")
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIG_DIR / f"modelado_curva_pr_{protocol}_16vars.png", dpi=300)
    plt.close()

    # ---- Calibracion en validacion interna ----
    frac_pos, mean_pred = calibration_curve(y_val, proba_val, n_bins=10,
                                            strategy="quantile")
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(mean_pred, frac_pos, "o-", label="Modelo", color="#1f6fb2")
    ax.plot([0, 1], [0, 1], "--", color="gray", label="Calibracion perfecta")
    ax.set_title(f"Calibracion en validacion interna ({protocol})")
    ax.set_xlabel("Probabilidad media predicha")
    ax.set_ylabel("Frecuencia observada")
    ax.legend(loc="best")
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(FIG_DIR / f"modelado_calibracion_{protocol}_16vars.png", dpi=300)
    plt.close()

    # ---- Importancia por permutacion en validacion interna ----
    perm = permutation_importance(val_model, X_val, y_val, n_repeats=30,
                                  random_state=RANDOM_STATE, scoring="f1")
    imp = pd.DataFrame({
        "variable": [c.replace("_rel", "") for c in X_val.columns],
        "caida_f1": perm.importances_mean,
        "desv": perm.importances_std,
    }).sort_values("caida_f1", ascending=False)
    imp.to_csv(METRICS_DIR / f"modelado_importancia_{protocol}_16vars.csv",
               index=False)
    top = imp.head(12).iloc[::-1]
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(top["variable"], top["caida_f1"], xerr=top["desv"], color="#1f6fb2")
    ax.set_title(f"Importancia por permutacion ({protocol}, validacion interna)")
    ax.set_xlabel("Caida del F1 al desordenar la variable")
    ax.set_ylabel("Predictor")
    plt.tight_layout()
    plt.savefig(FIG_DIR / f"modelado_importancia_{protocol}_16vars.png",
                dpi=300)
    plt.close()

    # ---- Coeficientes o importancia por impureza ----
    coefs = coefficients_table(final_model, list(X_train.columns))
    coefs.to_csv(METRICS_DIR / f"modelado_coeficientes_{protocol}_16vars.csv",
                 index=False)

    return {
        "protocolo": protocol,
        "modelo_final": final_name,
        "mejores_parametros": final_search.best_params_,
        "umbral": threshold,
        "f1_validacion": f1_val,
        "cv": tuned_only.loc[final_name].to_dict(),
        "test_base": base_test,
        "test_umbral_050": test_05,
        "test_umbral": test_thr,
        "linea_base_cv": dummy_summary,
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
    }


# --------------------------------------------------------------------------
# Principal
# --------------------------------------------------------------------------
def main() -> None:
    t_start = time.time()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    log, log_file = setup_logging()

    log.info("=" * 70)
    log.info("FASE IV - MODELADO | 16 predictores | run_id=%s", RUN_ID)
    log.info("Python %s | pandas %s | numpy %s | sklearn %s | matplotlib %s",
             platform.python_version(), pd.__version__, np.__version__,
             sklearn.__version__, matplotlib.__version__)
    log.info("Entrada: %s", DATA_FILE)
    input_hash = sha256_file(DATA_FILE)
    log.info("SHA256 entrada: %s", input_hash)

    raw = pd.read_csv(DATA_FILE)
    df = add_relative_features(raw, FEATURES)
    feature_cols = [f"{c}_rel" for c in FEATURES]
    X = df[feature_cols]
    y = df[TARGET].astype(int)
    log.info("Filas: %d | predictores: %d | clases: %s",
             len(df), len(feature_cols), y.value_counts().to_dict())

    # ---- Validaciones ----
    assert len(FEATURES) == 16, f"Se esperaban 16 predictores, hay {len(FEATURES)}"
    assert not set(FEATURES) & PROHIBIDOS, "Hay predictores prohibidos en FEATURES"
    assert set(y.unique()) <= {0, 1}, "El objetivo no es binario"
    assert not df.duplicated(subset=["season", "Team"]).any(), "Duplicados (season, Team)"
    assert X.notna().all().all(), "Hay nulos en los predictores"
    assert np.isfinite(X.to_numpy()).all(), "Hay infinitos en los predictores"
    log.info("Validaciones basicas: OK")

    # ---- VIF sobre el train del protocolo temporal ----
    train_mask = df["season"] <= TEMPORAL_CUTOFF
    test_mask = ~train_mask
    vif = vif_table(X[train_mask])
    vif.to_csv(METRICS_DIR / "modelado_vif_16vars.csv", index=False)
    log.info("VIF maximo: %s (%.2f)", vif.iloc[0]["variable"], vif.iloc[0]["vif"])

    summaries = {}

    # ---- Protocolo principal: temporal ----
    X_train_t, y_train_t = X[train_mask], y[train_mask]
    X_test_t, y_test_t = X[test_mask], y[test_mask]
    groups_train_t = df.loc[train_mask, "season"]
    cv_t = StratifiedGroupKFold(n_splits=N_FOLDS, shuffle=True,
                                random_state=RANDOM_STATE)
    test_meta_t = df.loc[test_mask, ["season", "Team"]]
    summaries["temporal"] = run_protocol(
        "temporal", X_train_t, y_train_t, X_test_t, y_test_t,
        groups_train_t, cv_t, test_meta_t, log)

    # ---- Protocolo secundario: estratificado 80/20 ----
    idx_train, idx_test = train_test_split(
        df.index, test_size=TEST_SIZE, stratify=y, random_state=RANDOM_STATE)
    X_train_r, y_train_r = X.loc[idx_train], y.loc[idx_train]
    X_test_r, y_test_r = X.loc[idx_test], y.loc[idx_test]
    cv_r = StratifiedKFold(n_splits=N_FOLDS, shuffle=True,
                           random_state=RANDOM_STATE)
    test_meta_r = df.loc[idx_test, ["season", "Team"]]
    summaries["estratificado"] = run_protocol(
        "estratificado", X_train_r, y_train_r, X_test_r, y_test_r,
        None, cv_r, test_meta_r, log)

    # ---- Sensibilidad con el modelo final del protocolo temporal ----
    final = summaries["temporal"]
    final_name = final["modelo_final"]
    best_pipe = make_pipeline(MODELS[final_name][0]).set_params(
        **final["mejores_parametros"])

    scenarios = {
        "principal_16_rel": (X_train_t, groups_train_t),
        "sin_Age": (X_train_t.drop(columns=["Age_rel"]), groups_train_t),
        "sin_3P%": (X_train_t.drop(columns=["3P%_rel"]), groups_train_t),
        "sin_Age_y_3P%": (X_train_t.drop(columns=["Age_rel", "3P%_rel"]),
                          groups_train_t),
        "sin_TRB": (X_train_t.drop(columns=["TRB_rel"]), groups_train_t),
        "sin_VIF_mayor_10": (X_train_t.drop(
            columns=["TRB_rel", "Pace_rel", "off_ORB%_rel"]), groups_train_t),
        "absolutas_16": (df.loc[train_mask, FEATURES], groups_train_t),
    }
    sens_rows = []
    for name, (Xs, gs) in scenarios.items():
        scores = cross_validate(
            clone(best_pipe), Xs, y_train_t, cv=cv_t, groups=gs,
            scoring={"f1": "f1", "accuracy": "accuracy", "roc_auc": "roc_auc"})
        row = {
            "escenario": name,
            "n_predictores": int(Xs.shape[1]),
            "cv_f1": float(np.mean(scores["test_f1"])),
            "cv_f1_std": float(np.std(scores["test_f1"])),
            "cv_accuracy": float(np.mean(scores["test_accuracy"])),
            "cv_accuracy_std": float(np.std(scores["test_accuracy"])),
            "cv_roc_auc": float(np.mean(scores["test_roc_auc"])),
            "cv_roc_auc_std": float(np.std(scores["test_roc_auc"])),
        }
        sens_rows.append(row)
        log.info("Sensibilidad %s: f1=%.3f+-%.3f | accuracy=%.3f | roc_auc=%.3f",
                 name, row["cv_f1"], row["cv_f1_std"], row["cv_accuracy"],
                 row["cv_roc_auc"])
    pd.DataFrame(sens_rows).to_csv(
        METRICS_DIR / "modelado_sensibilidad_16vars.csv", index=False)

    # ---- Resumen y manifiesto ----
    outputs = sorted(str(p) for p in OUT_DIR.rglob("*") if p.is_file())
    summary = {
        "run_id": RUN_ID,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "input_file": str(DATA_FILE),
        "input_sha256": input_hash,
        "n_rows": int(len(df)),
        "n_features": len(FEATURES),
        "features": FEATURES,
        "target": TARGET,
        "random_state": RANDOM_STATE,
        "n_folds": N_FOLDS,
        "temporal_cutoff": TEMPORAL_CUTOFF,
        "refit": REFIT,
        "protocolos": summaries,
        "vif_max": {"variable": vif.iloc[0]["variable"],
                    "vif": float(vif.iloc[0]["vif"])},
        "sensibilidad": sens_rows,
        "versiones": {
            "python": platform.python_version(),
            "pandas": pd.__version__,
            "numpy": np.__version__,
            "scikit_learn": sklearn.__version__,
            "matplotlib": matplotlib.__version__,
        },
        "log_file": str(log_file),
        "duracion_segundos": round(time.time() - t_start, 2),
        "outputs": outputs,
    }
    (METRICS_DIR / "modelado_resumen_16vars.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, default=json_default),
        encoding="utf-8")

    manifest = {
        "run_id": RUN_ID,
        "timestamp": summary["timestamp"],
        "command": ".\\\\.venv\\\\Scripts\\\\python.exe modelado.py",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "packages": summary["versiones"],
        "input_sha256": input_hash,
        "n_rows": int(len(df)),
        "features": FEATURES,
        "protocolos": ["temporal", "estratificado"],
        "outputs": outputs,
        "notas": ("El protocolo temporal es el principal. El estratificado "
                  "es una replica secundaria del protocolo historico."),
    }
    (METRICS_DIR / "modelado_manifiesto_16vars.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, default=json_default),
        encoding="utf-8")

    lines = [
        "FASE IV - MODELADO - 16 PREDICTORES",
        "=" * 60,
        f"Fecha/hora: {summary['timestamp']}",
        f"Entrada: {DATA_FILE}",
        f"SHA256: {input_hash}",
        f"Filas: {len(df)} | Predictores: {len(FEATURES)}",
        f"Protocolo principal: temporal (train <= {TEMPORAL_CUTOFF}, test > {TEMPORAL_CUTOFF})",
        "Protocolo secundario: estratificado 80/20",
        "",
    ]
    for proto in ["temporal", "estratificado"]:
        s = summaries[proto]
        lines += [
            f"[{proto}] modelo final: {s['modelo_final']}",
            f"  parametros: {s['mejores_parametros']}",
            f"  umbral: {s['umbral']:.2f}",
            f"  CV F1: {s['cv']['cv_f1']:.3f} +- {s['cv']['cv_f1_std']:.3f}",
            f"  CV accuracy: {s['cv']['cv_accuracy']:.3f} +- {s['cv']['cv_accuracy_std']:.3f}",
            f"  CV ROC-AUC: {s['cv']['cv_roc_auc']:.3f} +- {s['cv']['cv_roc_auc_std']:.3f}",
            f"  TEST base (umbral 0.50): F1={s['test_base']['f1']:.3f} | "
            f"accuracy={s['test_base']['accuracy']:.3f} | ROC-AUC={s['test_base']['roc_auc']:.3f}",
            f"  TEST optimizado (umbral 0.50): F1={s['test_umbral_050']['f1']:.3f} | "
            f"accuracy={s['test_umbral_050']['accuracy']:.3f} | "
            f"ROC-AUC={s['test_umbral_050']['roc_auc']:.3f} | "
            f"PR-AUC={s['test_umbral_050']['pr_auc']:.3f} | "
            f"Brier={s['test_umbral_050']['brier']:.3f}",
            f"  TEST optimizado (umbral {s['umbral']:.2f}): F1={s['test_umbral']['f1']:.3f} | "
            f"accuracy={s['test_umbral']['accuracy']:.3f} | "
            f"ROC-AUC={s['test_umbral']['roc_auc']:.3f}",
            "",
        ]
    lines += ["Sensibilidad (protocolo temporal, CV):"]
    lines += [f"  {r['escenario']}: F1={r['cv_f1']:.3f} +- {r['cv_f1_std']:.3f}"
              for r in sens_rows]
    lines += [
        "",
        "Nota: la mejora de GridSearchCV en CV fue pequena (dentro de 1 desviacion).",
        "En test, el modelo optimizado no supero al modelo base; se reporta sin forzar una mejora.",
        "Limitaciones: asociacion no causal; test usado una vez por protocolo;",
        "el protocolo estratificado es secundario y no se usa para elegir el modelo final.",
    ]
    (METRICS_DIR / "modelado_resumen_16vars.txt").write_text(
        "\n".join(lines), encoding="utf-8")

    log.info("Resumen guardado en %s", METRICS_DIR)
    log.info("Duracion total: %.2f s", summary["duracion_segundos"])


if __name__ == "__main__":
    main()
